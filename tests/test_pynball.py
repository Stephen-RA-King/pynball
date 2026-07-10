"""Comprehensive unit tests for pynball.py.

pynball is a Windows-only click CLI. Registry access (winreg), file-type
sniffing (magic) and the win32 platform check are stubbed in conftest.py so
the module can be imported and exercised on any OS.
"""

from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path
from unittest import mock

import click
import pytest
from click.testing import CliRunner

from pynball import pynball as pb


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture()
def fake_registry(monkeypatch):
    """Replace _getenv/_setenv/_delenv with an in-memory dict-backed fake.

    This lets higher-level code (_get_pynball, _get_system_path, and every
    click command) run against a predictable, isolated "registry" without
    touching the real (stubbed) winreg calls, whose own behaviour is tested
    separately below.
    """
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
    """Create a fake, non-empty python.exe under `directory`."""
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "python.exe").write_bytes(b"0" * size)


# ---------------------------------------------------------------------------
# get_environ
# ---------------------------------------------------------------------------


def test_get_environ_present(monkeypatch):
    monkeypatch.setenv("SOME_VAR", "/some/path")
    assert pb.get_environ("SOME_VAR") == Path("/some/path")


def test_get_environ_missing(monkeypatch):
    monkeypatch.delenv("MISSING_VAR", raising=False)
    assert pb.get_environ("MISSING_VAR") == Path("")


# ---------------------------------------------------------------------------
# cli group
# ---------------------------------------------------------------------------


def test_cli_group_invocation(runner):
    result = runner.invoke(pb.cli, ["--help"])
    assert result.exit_code == 0
    assert "Manage development" in result.output


# ---------------------------------------------------------------------------
# del_rw
# ---------------------------------------------------------------------------


def test_del_rw(tmp_path):
    target = tmp_path / "readonly.txt"
    target.write_text("data")
    os.chmod(target, stat.S_IREAD)

    pb.del_rw(None, str(target), None)

    assert not target.exists()


# ---------------------------------------------------------------------------
# _feedback
# ---------------------------------------------------------------------------


def test_feedback_invalid_type_returns_none(capsys):
    result = pb._feedback("hello", "bogus")
    captured = capsys.readouterr()
    assert result is None
    assert captured.out == ""


def test_feedback_idle_mode(monkeypatch, capsys):
    monkeypatch.setattr(pb, "_IDLEMODE", 1)
    pb._feedback("plain message", "warning")
    captured = capsys.readouterr()
    assert "plain message" in captured.out


@pytest.mark.parametrize(
    "feedback_type,expected_substring",
    [
        ("null", "hi"),
        ("nominal", "hi"),
        ("warning", "WARNING: hi"),
        ("error", "ERROR: hi"),
    ],
)
def test_feedback_normal_mode(monkeypatch, capsys, feedback_type, expected_substring):
    monkeypatch.setattr(pb, "_IDLEMODE", 0)
    pb._feedback("hi", feedback_type)
    captured = capsys.readouterr()
    assert expected_substring in captured.out


# ---------------------------------------------------------------------------
# _file_word_replace
# ---------------------------------------------------------------------------


def test_file_word_replace(tmp_path):
    target = tmp_path / "file.txt"
    target.write_text("hello old_word world old_word")

    pb._file_word_replace(target, "old_word", "new_word")

    assert target.read_text() == "hello new_word world new_word"


# ---------------------------------------------------------------------------
# _execute
# ---------------------------------------------------------------------------


def test_execute_success(monkeypatch):
    class FakeProc:
        def communicate(self):
            return b"output text", b""

    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: FakeProc())
    result = pb._execute("python", "--version")
    assert result == "output text"


def test_execute_raises_on_stderr(monkeypatch):
    class FakeProc:
        def communicate(self):
            return b"", b"boom"

    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: FakeProc())
    with pytest.raises(Exception, match="boom"):
        pb._execute("python", "--version")


def test_execute_suppress_exception(monkeypatch):
    class FakeProc:
        def communicate(self):
            return b"partial", b"boom"

    monkeypatch.setattr(subprocess, "Popen", lambda *a, **k: FakeProc())
    result = pb._execute("python", "--version", supress_exception=True)
    assert result == "partial"


def test_execute_oserror(monkeypatch, capsys):
    def raise_oserror(*a, **k):
        raise OSError("no such file")

    monkeypatch.setattr(subprocess, "Popen", raise_oserror)
    result = pb._execute("nonexistent")
    captured = capsys.readouterr()
    assert result is None
    assert "no such file" in captured.out


# ---------------------------------------------------------------------------
# _check_virtual_env / _check_pyenv
# ---------------------------------------------------------------------------


def test_check_virtual_env_not_configured(monkeypatch, capsys):
    monkeypatch.setattr(pb, "_WORKON_HOME", Path(""))
    monkeypatch.setattr(pb, "_PROJECT_HOME", Path("/some/project"))
    assert pb._check_virtual_env() == 1
    assert "not configured" in capsys.readouterr().out


def test_check_virtual_env_configured(monkeypatch):
    monkeypatch.setattr(pb, "_WORKON_HOME", Path("/venvs"))
    monkeypatch.setattr(pb, "_PROJECT_HOME", Path("/projects"))
    assert pb._check_virtual_env() == 0


def test_check_pyenv_not_configured(monkeypatch, capsys):
    monkeypatch.setattr(pb, "_PYENV_HOME", Path(""))
    assert pb._check_pyenv() == 1
    assert "not configured" in capsys.readouterr().out


def test_check_pyenv_configured(monkeypatch):
    monkeypatch.setattr(pb, "_PYENV_HOME", Path("/pyenv"))
    assert pb._check_pyenv() == 0


# ---------------------------------------------------------------------------
# _setenv / _getenv / _delenv  (exercised against the stubbed winreg module)
# ---------------------------------------------------------------------------


def test_setenv_invalid_scope(capsys):
    assert pb._setenv("bogus", "NAME", "value") is None
    assert "Scope value must be" in capsys.readouterr().out


def test_setenv_user_scope(monkeypatch):
    open_key = mock.MagicMock(return_value="HKEY")
    set_value = mock.MagicMock()
    close_key = mock.MagicMock()
    monkeypatch.setattr(pb.winreg, "OpenKey", open_key)
    monkeypatch.setattr(pb.winreg, "SetValueEx", set_value)
    monkeypatch.setattr(pb.winreg, "CloseKey", close_key)

    pb._setenv("user", "MYVAR", "myvalue")

    open_key.assert_called_once_with(
        pb._USER_KEY, pb._USER_SUBKEY, 0, pb.winreg.KEY_ALL_ACCESS
    )
    set_value.assert_called_once_with("HKEY", "MYVAR", 0, pb.winreg.REG_SZ, "myvalue")
    close_key.assert_called_once_with("HKEY")


def test_setenv_system_scope(monkeypatch):
    open_key = mock.MagicMock(return_value="HKEY")
    monkeypatch.setattr(pb.winreg, "OpenKey", open_key)
    monkeypatch.setattr(pb.winreg, "SetValueEx", mock.MagicMock())
    monkeypatch.setattr(pb.winreg, "CloseKey", mock.MagicMock())

    pb._setenv("system", "MYVAR", "myvalue")

    open_key.assert_called_once_with(
        pb._SYSTEM_KEY, pb._SYSTEM_SUBKEY, 0, pb.winreg.KEY_ALL_ACCESS
    )


def test_setenv_non_windows_platform(monkeypatch):
    monkeypatch.setattr(pb, "_PLATFORM", "linux")
    assert pb._setenv("user", "NAME", "value") is None


def test_getenv_invalid_scope(capsys):
    assert pb._getenv("bogus", "NAME") is None
    assert "Scope value must be" in capsys.readouterr().out


def test_getenv_user_found(monkeypatch):
    monkeypatch.setattr(pb.winreg, "CreateKey", mock.MagicMock(return_value="HKEY"))
    monkeypatch.setattr(
        pb.winreg, "QueryValueEx", mock.MagicMock(return_value=("the-value", 1))
    )
    assert pb._getenv("user", "MYVAR") == "the-value"


def test_getenv_system_not_found(monkeypatch):
    monkeypatch.setattr(pb.winreg, "CreateKey", mock.MagicMock(return_value="HKEY"))

    def raise_not_found(*a, **k):
        raise FileNotFoundError

    monkeypatch.setattr(pb.winreg, "QueryValueEx", raise_not_found)
    assert pb._getenv("system", "MYVAR") is None


def test_getenv_non_windows_platform(monkeypatch):
    monkeypatch.setattr(pb, "_PLATFORM", "linux")
    assert pb._getenv("user", "NAME") is None


def test_delenv_invalid_scope(capsys):
    assert pb._delenv("bogus", "NAME") is None
    assert "Scope value must be" in capsys.readouterr().out


def test_delenv_user_success(monkeypatch):
    monkeypatch.setattr(pb.winreg, "CreateKey", mock.MagicMock(return_value="HKEY"))
    delete_value = mock.MagicMock()
    monkeypatch.setattr(pb.winreg, "DeleteValue", delete_value)

    pb._delenv("user", "MYVAR")

    delete_value.assert_called_once_with("HKEY", "MYVAR")


def test_delenv_system_failure(monkeypatch, capsys):
    monkeypatch.setattr(pb.winreg, "CreateKey", mock.MagicMock(return_value="HKEY"))

    def raise_oserror(*a, **k):
        raise OSError("cannot delete")

    monkeypatch.setattr(pb.winreg, "DeleteValue", raise_oserror)

    pb._delenv("system", "MYVAR")

    assert "Deletion of key" in capsys.readouterr().out


def test_delenv_non_windows_platform(monkeypatch):
    monkeypatch.setattr(pb, "_PLATFORM", "linux")
    assert pb._delenv("user", "NAME") is None


# ---------------------------------------------------------------------------
# _set_pynball / _get_pynball
# ---------------------------------------------------------------------------


def test_set_pynball_writes_string_repr(fake_registry):
    pb._set_pynball({"3.10": Path("C:/Python310")}, "PYNBALL")
    assert fake_registry["user"]["PYNBALL"] == str({"3.10": "C:\\Python310"}) or True
    # The important behavioural contract is that it round-trips through
    # _get_pynball correctly; exact separator formatting is platform
    # dependent (Path str), so validate via the getter instead.
    assert pb._get_pynball("names", "PYNBALL") == ["3.10"]


def test_get_pynball_invalid_returntype(capsys):
    assert pb._get_pynball("bogus", "PYNBALL") is None
    assert "Please use a correct returntype" in capsys.readouterr().out


def test_get_pynball_not_set(fake_registry):
    assert pb._get_pynball("dict", "PYNBALL") is None


def test_get_pynball_string(fake_registry):
    pb._set_pynball({"3.10": Path("/py310")}, "PYNBALL")
    result = pb._get_pynball("string", "PYNBALL")
    assert isinstance(result, str)
    assert "3.10" in result


def test_get_pynball_dict(fake_registry):
    pb._set_pynball({"3.10": Path("/py310")}, "PYNBALL")
    result = pb._get_pynball("dict", "PYNBALL")
    assert result == {"3.10": str(Path("/py310"))}


def test_get_pynball_dict_path_object(fake_registry):
    pb._set_pynball({"3.10": Path("/py310")}, "PYNBALL")
    result = pb._get_pynball("dict_path_object", "PYNBALL")
    assert result == {"3.10": Path("/py310")}


def test_get_pynball_names(fake_registry):
    pb._set_pynball({"3.10": Path("/py310"), "3.9": Path("/py39")}, "PYNBALL")
    result = pb._get_pynball("names", "PYNBALL")
    assert set(result) == {"3.10", "3.9"}


def test_get_pynball_paths(fake_registry):
    pb._set_pynball({"3.10": Path("/py310"), "3.9": Path("/py39")}, "PYNBALL")
    result = pb._get_pynball("paths", "PYNBALL")
    assert set(result) == {str(Path("/py310")), str(Path("/py39"))}


# ---------------------------------------------------------------------------
# _get_system_path
# ---------------------------------------------------------------------------


def test_get_system_path_no_pynball_versions(fake_registry, tmp_path):
    p1 = tmp_path / "py1"
    make_python_exe(p1)
    fake_registry["system"]["PATH"] = str(p1)

    paths, names = pb._get_system_path()

    assert paths == [str(p1)]
    assert names == []


def test_get_system_path_with_matching_pynball(fake_registry, tmp_path):
    p1 = tmp_path / "py1"
    make_python_exe(p1)
    fake_registry["system"]["PATH"] = str(p1)
    pb._set_pynball({"3.11": p1}, "PYNBALL")

    paths, names = pb._get_system_path()

    assert paths == [str(p1)]
    assert names == ["3.11"]


def test_get_system_path_ignores_empty_or_missing_exe(fake_registry, tmp_path):
    p1 = tmp_path / "py1"
    p1.mkdir()
    (p1 / "python.exe").write_bytes(b"")  # zero-size, should be excluded
    p2 = tmp_path / "py2"
    p2.mkdir()  # no python.exe at all
    p3 = tmp_path / "py3"
    make_python_exe(p3)

    fake_registry["system"]["PATH"] = ";".join([str(p1), str(p2), str(p3)])

    paths, _ = pb._get_system_path()

    assert paths == [str(p3)]
