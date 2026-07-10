"""Tests for pynball's project management and config import/export commands."""

from __future__ import annotations

import shutil
from pathlib import Path

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


@pytest.fixture(autouse=True)
def reset_config(monkeypatch):
    """pynball.config is a module-level ConfigParser shared across calls.

    Reset it before each test so exportconf/importconf tests don't leak
    sections into one another.
    """
    import configparser

    monkeypatch.setattr(pb, "config", configparser.ConfigParser())


@pytest.fixture()
def venv_dirs(tmp_path, monkeypatch):
    workon = tmp_path / "workon"
    workon.mkdir()
    project = tmp_path / "projects"
    project.mkdir()
    monkeypatch.setattr(pb, "_WORKON_HOME", workon)
    monkeypatch.setattr(pb, "_PROJECT_HOME", project)
    return workon, project


# ---------------------------------------------------------------------------
# mkproject
# ---------------------------------------------------------------------------


def test_mkproject_not_configured(runner, monkeypatch):
    monkeypatch.setattr(pb, "_WORKON_HOME", Path(""))
    monkeypatch.setattr(pb, "_PROJECT_HOME", Path("/x"))
    result = runner.invoke(pb.cli, ["mkproject", "3.10", "myproj"])
    assert "not configured" in result.output


def test_mkproject_version_not_configured(runner, fake_registry, venv_dirs, tmp_path):
    other_path = tmp_path / "other"
    pb._set_pynball({"3.9": other_path}, "PYNBALL")
    result = runner.invoke(pb.cli, ["mkproject", "3.10", "myproj"])
    assert "not configured in Pynball" in result.output


def test_mkproject_success_creates_both_dirs(
    runner, fake_registry, venv_dirs, tmp_path, monkeypatch
):
    workon, project = venv_dirs
    py_path = tmp_path / "py310"
    pb._set_pynball({"3.10": py_path}, "PYNBALL")
    monkeypatch.setattr(pb, "_execute", lambda *a, **k: "ok")

    result = runner.invoke(pb.cli, ["mkproject", "3.10", "myproj"])

    assert result.exit_code == 0
    assert (workon / "myproj").is_dir()
    assert (project / "myproj").is_dir()
    assert (workon / "myproj" / ".project").read_text() == str(project / "myproj")


def test_mkproject_noall_skips_project_dir(
    runner, fake_registry, venv_dirs, tmp_path, monkeypatch
):
    workon, project = venv_dirs
    py_path = tmp_path / "py310"
    pb._set_pynball({"3.10": py_path}, "PYNBALL")
    monkeypatch.setattr(pb, "_execute", lambda *a, **k: "ok")

    result = runner.invoke(pb.cli, ["mkproject", "-n", "3.10", "myproj"])

    assert result.exit_code == 0
    assert (workon / "myproj").is_dir()
    assert not (project / "myproj").exists()


def test_mkproject_file_exists_error(
    runner, fake_registry, venv_dirs, tmp_path, monkeypatch
):
    workon, project = venv_dirs
    (workon / "myproj").mkdir()
    py_path = tmp_path / "py310"
    pb._set_pynball({"3.10": py_path}, "PYNBALL")

    result = runner.invoke(pb.cli, ["mkproject", "3.10", "myproj"])

    assert "already exits" in result.output
    assert not (project / "myproj").exists()


def test_mkproject_file_not_found_error(
    runner, fake_registry, tmp_path, monkeypatch
):
    # WORKON_HOME points at a path whose parent does not exist, so
    # mkdir(parents=False) raises FileNotFoundError.
    workon = tmp_path / "missing_parent" / "workon"
    project = tmp_path / "projects"
    project.mkdir()
    monkeypatch.setattr(pb, "_WORKON_HOME", workon)
    monkeypatch.setattr(pb, "_PROJECT_HOME", project)
    py_path = tmp_path / "py310"
    pb._set_pynball({"3.10": py_path}, "PYNBALL")

    result = runner.invoke(pb.cli, ["mkproject", "3.10", "myproj"])

    assert "has NOT be created" in result.output


# ---------------------------------------------------------------------------
# rmproject
# ---------------------------------------------------------------------------


def test_rmproject_not_configured(runner, monkeypatch):
    monkeypatch.setattr(pb, "_WORKON_HOME", Path(""))
    monkeypatch.setattr(pb, "_PROJECT_HOME", Path("/x"))
    result = runner.invoke(pb.cli, ["rmproject", "myproj"])
    assert "not configured" in result.output


def test_rmproject_default_only_deletes_venv(runner, fake_registry, venv_dirs):
    workon, project = venv_dirs
    (workon / "myproj").mkdir()
    (project / "myproj").mkdir()

    result = runner.invoke(pb.cli, ["rmproject", "myproj"])

    assert "(virtualenv files) have been deleted" in result.output
    assert not (workon / "myproj").exists()
    assert (project / "myproj").exists()


def test_rmproject_all_deletes_both(runner, fake_registry, venv_dirs):
    workon, project = venv_dirs
    (workon / "myproj").mkdir()
    (project / "myproj").mkdir()

    result = runner.invoke(pb.cli, ["rmproject", "-a", "myproj"])

    assert "(virtualenv files) have been deleted" in result.output
    assert "(project files) have been deleted" in result.output
    assert not (workon / "myproj").exists()
    assert not (project / "myproj").exists()


def test_rmproject_file_not_found(runner, fake_registry, venv_dirs):
    result = runner.invoke(pb.cli, ["rmproject", "doesnotexist"])
    assert "does not exist" in result.output


def test_rmproject_permission_error(runner, fake_registry, venv_dirs, monkeypatch):
    workon, project = venv_dirs
    (workon / "myproj").mkdir()

    def raise_permission_error(*a, **k):
        raise PermissionError

    monkeypatch.setattr(pb.shutil, "rmtree", raise_permission_error)

    result = runner.invoke(pb.cli, ["rmproject", "myproj"])

    assert "Insufficient permissions" in result.output


# ---------------------------------------------------------------------------
# lsproject
# ---------------------------------------------------------------------------


def test_lsproject_not_configured(runner, monkeypatch):
    monkeypatch.setattr(pb, "_WORKON_HOME", Path(""))
    monkeypatch.setattr(pb, "_PROJECT_HOME", Path("/x"))
    result = runner.invoke(pb.cli, ["lsproject"])
    assert "not configured" in result.output


def test_lsproject_lists_projects(runner, venv_dirs):
    workon, project = venv_dirs

    # 1. Project with pattern1-style pyvenv.cfg and a pyenv version file.
    proj1 = workon / "proj1"
    proj1.mkdir()
    (proj1 / "pyvenv.cfg").write_text("version_info = 3.10.5\nother = 1\n")
    (project / "proj1").mkdir()
    (project / "proj1" / ".python-version").write_text("3.10.5\n")

    # 2. Project with pattern2-style pyvenv.cfg, no .python-version file.
    proj2 = workon / "proj2"
    proj2.mkdir()
    (proj2 / "pyvenv.cfg").write_text("version = 3.9.7\n")

    # 3. Project with pyvenv.cfg that matches neither pattern.
    proj3 = workon / "proj3"
    proj3.mkdir()
    (proj3 / "pyvenv.cfg").write_text("nothing useful here\n")

    # 4. Project missing pyvenv.cfg entirely.
    proj4 = workon / "proj4"
    proj4.mkdir()

    result = runner.invoke(pb.cli, ["lsproject"])

    assert result.exit_code == 0
    assert "proj1" in result.output
    assert "3.10.5" in result.output
    assert "proj2" in result.output
    assert "3.9.7" in result.output
    assert "proj3" in result.output
    assert "proj4" in result.output
    assert "missing virtual configuration" in result.output


# ---------------------------------------------------------------------------
# mvproject
# ---------------------------------------------------------------------------


def test_mvproject_missing_pyvenv_cfg_exits(runner, fake_registry, venv_dirs):
    workon, project = venv_dirs
    (project / "oldname").mkdir()
    (workon / "oldname").mkdir()  # no pyvenv.cfg inside

    result = runner.invoke(pb.cli, ["mvproject", "oldname", "newname"])

    assert result.exit_code == 1
    assert "Cannot ascertain existing python version" in result.output


def test_mvproject_unmatched_pyvenv_cfg_exits(runner, fake_registry, venv_dirs):
    workon, project = venv_dirs
    (project / "oldname").mkdir()
    venv = workon / "oldname"
    venv.mkdir()
    (venv / "pyvenv.cfg").write_text("nothing to match\n")

    result = runner.invoke(pb.cli, ["mvproject", "oldname", "newname"])

    assert result.exit_code == 1
    assert "Cannot ascertain existing python version" in result.output


def test_mvproject_success_renames_and_recreates(
    runner, fake_registry, venv_dirs, tmp_path, monkeypatch
):
    workon, project = venv_dirs

    proj_root = project / "oldname"
    proj_root.mkdir()
    (proj_root / "readme.txt").write_text("oldname is great, visit oldname often")
    (proj_root / "oldname_config.ini").write_text("[config]\nkey=oldname\n")
    subdir = proj_root / "subdir_oldname"
    subdir.mkdir()
    (subdir / "inner.txt").write_text("inner file, refers to oldname too")

    venv = workon / "oldname"
    venv.mkdir()
    (venv / "pyvenv.cfg").write_text("home = /usr\nversion_info = 3.10.5\n")

    py_path = tmp_path / "py310"
    pb._set_pynball({"3.10.5": py_path}, "PYNBALL")
    monkeypatch.setattr(pb, "_execute", lambda *a, **k: "ok")

    result = runner.invoke(pb.cli, ["mvproject", "oldname", "newname"])

    assert result.exit_code == 0, result.output

    # old virtualenv removed, new one created (mkproject with create_all="n")
    assert not venv.exists()
    assert (workon / "newname").is_dir()
    assert (workon / "newname" / ".project").exists()

    # project directory itself renamed
    assert not proj_root.exists()
    new_root = project / "newname"
    assert new_root.is_dir()

    # nested directory renamed too
    assert (new_root / "subdir_newname").is_dir()
    assert (new_root / "subdir_newname" / "inner.txt").exists()

    # filename containing old_name renamed
    assert (new_root / "newname_config.ini").exists()

    # file content replaced
    readme_text = (new_root / "readme.txt").read_text()
    assert "newname is great, visit newname often" == readme_text


def test_mvproject_rmtree_file_not_found(
    runner, fake_registry, venv_dirs, tmp_path, monkeypatch
):
    workon, project = venv_dirs
    proj_root = project / "oldname"
    proj_root.mkdir()
    venv = workon / "oldname"
    venv.mkdir()
    (venv / "pyvenv.cfg").write_text("version_info = 3.10.5\n")

    py_path = tmp_path / "py310"
    pb._set_pynball({"3.10.5": py_path}, "PYNBALL")
    monkeypatch.setattr(pb, "_execute", lambda *a, **k: "ok")

    def raise_fnf(*a, **k):
        raise FileNotFoundError

    monkeypatch.setattr(pb.shutil, "rmtree", raise_fnf)

    result = runner.invoke(pb.cli, ["mvproject", "oldname", "newname"])

    assert result.exit_code == 0
    assert "does not exist" in result.output


def test_mvproject_rmtree_permission_error(
    runner, fake_registry, venv_dirs, tmp_path, monkeypatch
):
    workon, project = venv_dirs
    proj_root = project / "oldname"
    proj_root.mkdir()
    venv = workon / "oldname"
    venv.mkdir()
    (venv / "pyvenv.cfg").write_text("version_info = 3.10.5\n")

    py_path = tmp_path / "py310"
    pb._set_pynball({"3.10.5": py_path}, "PYNBALL")
    monkeypatch.setattr(pb, "_execute", lambda *a, **k: "ok")

    def raise_perm(*a, **k):
        raise PermissionError

    monkeypatch.setattr(pb.shutil, "rmtree", raise_perm)

    result = runner.invoke(pb.cli, ["mvproject", "oldname", "newname"])

    assert result.exit_code == 0
    assert "Insufficient permissions" in result.output


# ---------------------------------------------------------------------------
# exportconf / importconf
# ---------------------------------------------------------------------------


def test_exportconf_writes_ini(runner, fake_registry, tmp_path):
    pb._set_pynball({"3.10": Path("/py310")}, "PYNBALL")

    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(pb.cli, ["exportconf"])
        assert result.exit_code == 0
        content = Path("pynball.ini").read_text()
        assert "[PYNBALL]" in content
        assert "3.10" in content


def test_importconf_success(runner, fake_registry, tmp_path):
    ini_path = tmp_path / "backup.ini"
    ini_path.write_text("[PYNBALL]\nPYNBALL = {'3.10': '/py310'}\n\n")

    result = runner.invoke(pb.cli, ["importconf", str(ini_path)])

    assert result.exit_code == 0
    assert fake_registry["user"]["PYNBALL"] == "{'3.10': '/py310'}"


def test_importconf_bad_file(runner, fake_registry, tmp_path):
    ini_path = tmp_path / "bad.ini"
    ini_path.write_text("[SOMETHINGELSE]\nfoo = bar\n")

    result = runner.invoke(pb.cli, ["importconf", str(ini_path)])

    assert result.exit_code == 0
    assert "problem with file" in result.output
    assert "PYNBALL" not in fake_registry["user"]
