"""Tests for pynball's click commands."""

from __future__ import annotations

import shutil
from pathlib import Path
from unittest import mock

import pytest
from click.testing import CliRunner

from pynball import pynball as pb


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def fake_registry(monkeypatch):
    store: dict[str, dict[str, str]] = {"user": {}, "system": {"PATH": ""}}

    def fake_getenv(scope, name):
        if scope not in ("user", "system"):
            pb._feedback("Scope value must be 'user' or 'system'", "warning")
            return None
        return store[scope].get(name)

    def fake_setenv(scope, name, value):
        if scope not in ("user", "system"):
            pb._feedback("Scope value must be 'user' or 'system'", "warning")
            return
        store[scope][name] = value

    def fake_delenv(scope, name):
        if scope not in ("user", "system"):
            pb._feedback("Scope value must be 'user' or 'system'", "warning")
            return
        store[scope].pop(name, None)

    monkeypatch.setattr(pb, "_getenv", fake_getenv)
    monkeypatch.setattr(pb, "_setenv", fake_setenv)
    monkeypatch.setattr(pb, "_delenv", fake_delenv)
    return store


def make_python_exe(directory: Path, size: int = 10) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "python.exe").write_bytes(b"0" * size)


# ---------------------------------------------------------------------------
# add
# ---------------------------------------------------------------------------


def test_add_no_python_exe(runner, fake_registry, tmp_path):
    bad_path = tmp_path / "nointerpreter"
    bad_path.mkdir()
    result = runner.invoke(pb.cli, ["add", "3.10", str(bad_path)])
    assert "no Python Interpreter" in result.output
    assert pb._get_pynball("dict", "PYNBALL") is None


def test_add_first_entry(runner, fake_registry, tmp_path):
    path310 = tmp_path / "py310"
    make_python_exe(path310)
    result = runner.invoke(pb.cli, ["add", "3.10", str(path310)])
    assert "Successfully added" in result.output
    assert pb._get_pynball("dict", "PYNBALL") == {"3.10": str(path310)}


def test_add_duplicate_path(runner, fake_registry, tmp_path):
    path310 = tmp_path / "py310"
    make_python_exe(path310)
    runner.invoke(pb.cli, ["add", "3.10", str(path310)])
    result = runner.invoke(pb.cli, ["add", "3.10-again", str(path310)])
    assert "already added to configuration as '3.10'" in result.output


def test_add_second_entry_sorts_versions(runner, fake_registry, tmp_path):
    path39 = tmp_path / "py39"
    make_python_exe(path39)
    path310 = tmp_path / "py310"
    make_python_exe(path310)

    runner.invoke(pb.cli, ["add", "3.9", str(path39)])
    result = runner.invoke(pb.cli, ["add", "3.10", str(path310)])

    assert "Successfully added" in result.output
    stored = pb._get_pynball("dict", "PYNBALL")
    assert stored == {"3.10": str(path310), "3.9": str(path39)}
    # sorted reverse numerically: 3.10 before 3.9
    assert list(stored.keys()) == ["3.10", "3.9"]


# ---------------------------------------------------------------------------
# addall
# ---------------------------------------------------------------------------


def test_addall_uses_env_var(runner, fake_registry, tmp_path, monkeypatch):
    home = tmp_path / "installs"
    v1 = home / "3.10.1"
    make_python_exe(v1)
    v2 = home / "not_a_version"
    v2.mkdir()  # no python.exe - should be skipped

    monkeypatch.setenv("PYNBALL_HOME", str(home))
    monkeypatch.setattr(pb, "_execute", lambda *a, **k: "Python 3.10.1")

    result = runner.invoke(pb.cli, ["addall"])

    assert result.exit_code == 0
    stored = pb._get_pynball("dict", "PYNBALL")
    assert stored == {"3.10.1": str(v1)}
    assert fake_registry["user"]["PYNBALL_HOME"] == str(home)


def test_addall_no_active_dirs_skips_pynball_home_write(
    runner, fake_registry, tmp_path, monkeypatch
):
    home = tmp_path / "empty_installs"
    home.mkdir()
    monkeypatch.setenv("PYNBALL_HOME", str(home))

    result = runner.invoke(pb.cli, ["addall"])

    assert result.exit_code == 0
    assert "PYNBALL_HOME" not in fake_registry["user"]


def test_addall_prompts_and_accepts_keyboard_interrupt(
    runner, fake_registry, monkeypatch
):
    monkeypatch.delenv("PYNBALL_HOME", raising=False)

    def raise_keyboard_interrupt(_prompt=""):
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", raise_keyboard_interrupt)

    result = runner.invoke(pb.cli, ["addall"])

    assert result.exit_code == 0
    assert "Please specify the root directory" in result.output


def test_addall_prompts_until_valid_path(
    runner, fake_registry, tmp_path, monkeypatch
):
    monkeypatch.delenv("PYNBALL_HOME", raising=False)
    home = tmp_path / "installs2"
    v1 = home / "3.11.0"
    make_python_exe(v1)

    answers = iter(["/does/not/exist", str(home)])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))
    monkeypatch.setattr(pb, "_execute", lambda *a, **k: "Python 3.11.0")

    result = runner.invoke(pb.cli, ["addall"])

    assert result.exit_code == 0
    assert pb._get_pynball("dict", "PYNBALL") == {"3.11.0": str(v1)}


# ---------------------------------------------------------------------------
# delete
# ---------------------------------------------------------------------------


def test_delete_removes_entry(runner, fake_registry, tmp_path):
    path310 = tmp_path / "py310"
    make_python_exe(path310)
    runner.invoke(pb.cli, ["add", "3.10", str(path310)])

    result = runner.invoke(pb.cli, ["delete", "3.10"])

    assert result.exit_code == 0
    assert pb._get_pynball("dict", "PYNBALL") == {}


def test_delete_refuses_system_interpreter(runner, fake_registry, tmp_path):
    path310 = tmp_path / "py310"
    make_python_exe(path310)
    runner.invoke(pb.cli, ["add", "3.10", str(path310)])
    fake_registry["system"]["PATH"] = str(path310)

    result = runner.invoke(pb.cli, ["delete", "3.10"])

    assert "Cannot delete System Interpreter" in result.output
    assert pb._get_pynball("dict", "PYNBALL") == {"3.10": str(path310)}


# ---------------------------------------------------------------------------
# reset
# ---------------------------------------------------------------------------


def test_reset(runner, fake_registry, tmp_path):
    path310 = tmp_path / "py310"
    make_python_exe(path310)
    runner.invoke(pb.cli, ["add", "3.10", str(path310)])

    result = runner.invoke(pb.cli, ["reset"])

    assert result.exit_code == 0
    assert "PYNBALL" not in fake_registry["user"]


# ---------------------------------------------------------------------------
# version
# ---------------------------------------------------------------------------


def test_version(runner):
    result = runner.invoke(pb.cli, ["version"])
    assert result.exit_code == 0
    assert "ReleaseLevel" in result.output


# ---------------------------------------------------------------------------
# versions
# ---------------------------------------------------------------------------


def test_versions_no_system_interpreter_no_pynball(runner, fake_registry):
    result = runner.invoke(pb.cli, ["versions"])
    assert "System Interpreter is not configured" in result.output
    assert "Pynball configuration is empty" in result.output


def test_versions_system_not_in_pynball_config(runner, fake_registry, tmp_path):
    sys_path = tmp_path / "sysinterp"
    make_python_exe(sys_path)
    fake_registry["system"]["PATH"] = str(sys_path)

    other_path = tmp_path / "other"
    make_python_exe(other_path)
    pb._set_pynball({"3.9": other_path}, "PYNBALL")

    result = runner.invoke(pb.cli, ["versions"])

    assert f"{sys_path} : --> System Interpreter" in result.output
    assert "System Interpreter is not in Pynball Configuration" in result.output


def test_versions_system_matches_pynball_entry(runner, fake_registry, tmp_path):
    sys_path = tmp_path / "sysinterp"
    make_python_exe(sys_path)
    fake_registry["system"]["PATH"] = str(sys_path)
    pb._set_pynball({"3.11": sys_path}, "PYNBALL")

    result = runner.invoke(pb.cli, ["versions"])

    assert "System Interpreter" in result.output
    assert "3.11" in result.output


# ---------------------------------------------------------------------------
# system
# ---------------------------------------------------------------------------


def test_system_name_not_configured(runner, fake_registry, tmp_path):
    other_path = tmp_path / "other"
    make_python_exe(other_path)
    pb._set_pynball({"3.10": other_path}, "PYNBALL")

    result = runner.invoke(pb.cli, ["system", "3.99"])
    assert "is not in Pynballs' configuration" in result.output


def test_system_multiple_interpreters_detected(runner, fake_registry, tmp_path):
    p1 = tmp_path / "py1"
    make_python_exe(p1)
    p2 = tmp_path / "py2"
    make_python_exe(p2)
    fake_registry["system"]["PATH"] = ";".join([str(p1), str(p2)])
    pb._set_pynball({"3.10": p1, "3.11": p2}, "PYNBALL")

    result = runner.invoke(pb.cli, ["system", "3.10"])

    assert "Multiple system interpreters" in result.output


def test_system_already_configured(runner, fake_registry, tmp_path):
    p1 = tmp_path / "py1"
    make_python_exe(p1)
    fake_registry["system"]["PATH"] = str(p1)
    pb._set_pynball({"3.10": p1}, "PYNBALL")

    result = runner.invoke(pb.cli, ["system", "3.10"])

    assert "already configured as the system interpreter" in result.output


def test_system_switch_from_existing(runner, fake_registry, tmp_path):
    old_path = tmp_path / "old"
    make_python_exe(old_path)
    new_path = tmp_path / "new"
    make_python_exe(new_path)

    fake_registry["system"]["PATH"] = f"{old_path};C:\\Windows"
    pb._set_pynball({"old": old_path, "new": new_path}, "PYNBALL")

    # Only "old" is currently on PATH so only "old" resolves as system version.
    result = runner.invoke(pb.cli, ["system", "new"])

    assert "New version set" in result.output
    assert str(new_path) in fake_registry["system"]["PATH"]
    assert str(old_path) not in fake_registry["system"]["PATH"]


def test_system_no_existing_interpreter_prepends(runner, fake_registry, tmp_path):
    new_path = tmp_path / "new"
    make_python_exe(new_path)
    fake_registry["system"]["PATH"] = "C:\\Windows"
    pb._set_pynball({"new": new_path}, "PYNBALL")

    result = runner.invoke(pb.cli, ["system", "new"])

    assert "New version set" in result.output
    assert fake_registry["system"]["PATH"].startswith(str(new_path))


# ---------------------------------------------------------------------------
# pyenv
# ---------------------------------------------------------------------------


def test_pyenv_not_configured(runner, fake_registry, monkeypatch):
    monkeypatch.setattr(pb, "_PYENV_HOME", Path(""))
    result = runner.invoke(pb.cli, ["pyenv"])
    assert "not configured" in result.output


def test_pyenv_use_adds_new_versions(runner, fake_registry, tmp_path, monkeypatch):
    pyenv_home = tmp_path / "pyenv"
    versions_dir = pyenv_home / "versions"
    make_python_exe(versions_dir / "3.12.0")
    monkeypatch.setattr(pb, "_PYENV_HOME", pyenv_home)

    unrelated_path = tmp_path / "unrelated"
    make_python_exe(unrelated_path)
    pb._set_pynball({"3.5": unrelated_path}, "PYNBALL")

    result = runner.invoke(pb.cli, ["pyenv", "-u"])

    assert result.exit_code == 0
    assert set(pb._get_pynball("names", "PYNBALL")) == {"3.5", "3.12.0"}


def test_pyenv_use_skips_system_version(runner, fake_registry, tmp_path, monkeypatch):
    pyenv_home = tmp_path / "pyenv"
    versions_dir = pyenv_home / "versions"
    sysver_dir = versions_dir / "3.12.0"
    make_python_exe(sysver_dir)
    monkeypatch.setattr(pb, "_PYENV_HOME", pyenv_home)
    fake_registry["system"]["PATH"] = str(sysver_dir)
    pb._set_pynball({"3.12.0": sysver_dir}, "PYNBALL")

    result = runner.invoke(pb.cli, ["pyenv", "-u"])

    assert result.exit_code == 0
    # Still just the one, untouched, entry - not duplicated / errored.
    assert pb._get_pynball("names", "PYNBALL") == ["3.12.0"]


def test_pyenv_use_noforce_keeps_manual_entry(
    runner, fake_registry, tmp_path, monkeypatch
):
    pyenv_home = tmp_path / "pyenv"
    versions_dir = pyenv_home / "versions"
    make_python_exe(versions_dir / "3.12.0")
    monkeypatch.setattr(pb, "_PYENV_HOME", pyenv_home)

    manual_path = tmp_path / "manual312"
    make_python_exe(manual_path)
    pb._set_pynball({"3.12.0": manual_path}, "PYNBALL")

    result = runner.invoke(pb.cli, ["pyenv", "-u", "--noforce"])

    assert result.exit_code == 0
    assert pb._get_pynball("dict", "PYNBALL") == {"3.12.0": str(manual_path)}


def test_pyenv_use_force_overrides_manual_entry(
    runner, fake_registry, tmp_path, monkeypatch
):
    pyenv_home = tmp_path / "pyenv"
    versions_dir = pyenv_home / "versions"
    pyenv_path = versions_dir / "3.12.0"
    make_python_exe(pyenv_path)
    monkeypatch.setattr(pb, "_PYENV_HOME", pyenv_home)

    manual_path = tmp_path / "manual312"
    make_python_exe(manual_path)
    pb._set_pynball({"3.12.0": manual_path}, "PYNBALL")

    result = runner.invoke(pb.cli, ["pyenv", "-u", "-f"])

    assert result.exit_code == 0
    assert pb._get_pynball("dict", "PYNBALL") == {"3.12.0": str(pyenv_path)}


def test_pyenv_default_removes_matching_entries(
    runner, fake_registry, tmp_path, monkeypatch
):
    pyenv_home = tmp_path / "pyenv"
    versions_dir = pyenv_home / "versions"
    pyenv_path = versions_dir / "3.12.0"
    make_python_exe(pyenv_path)
    monkeypatch.setattr(pb, "_PYENV_HOME", pyenv_home)
    pb._set_pynball({"3.12.0": pyenv_path}, "PYNBALL")

    result = runner.invoke(pb.cli, ["pyenv"])

    assert result.exit_code == 0
    assert pb._get_pynball("dict", "PYNBALL") == {}


def test_pyenv_default_skips_system_version(
    runner, fake_registry, tmp_path, monkeypatch
):
    pyenv_home = tmp_path / "pyenv"
    versions_dir = pyenv_home / "versions"
    pyenv_path = versions_dir / "3.12.0"
    make_python_exe(pyenv_path)
    monkeypatch.setattr(pb, "_PYENV_HOME", pyenv_home)
    fake_registry["system"]["PATH"] = str(pyenv_path)
    pb._set_pynball({"3.12.0": pyenv_path}, "PYNBALL")

    result = runner.invoke(pb.cli, ["pyenv"])

    assert result.exit_code == 0
    # system version must survive the "prune" pass
    assert pb._get_pynball("dict", "PYNBALL") == {"3.12.0": str(pyenv_path)}


def test_pyenv_default_no_matching_paths_noop(
    runner, fake_registry, tmp_path, monkeypatch
):
    pyenv_home = tmp_path / "pyenv"
    versions_dir = pyenv_home / "versions"
    make_python_exe(versions_dir / "3.12.0")
    monkeypatch.setattr(pb, "_PYENV_HOME", pyenv_home)

    unrelated_path = tmp_path / "unrelated"
    make_python_exe(unrelated_path)
    pb._set_pynball({"3.5": unrelated_path}, "PYNBALL")

    result = runner.invoke(pb.cli, ["pyenv"])

    assert result.exit_code == 0
    assert pb._get_pynball("dict", "PYNBALL") == {"3.5": str(unrelated_path)}
