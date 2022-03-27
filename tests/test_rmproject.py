# Core Library modules
from pathlib import Path, PurePath, WindowsPath

# Third party modules
import pytest
from click.testing import CliRunner

# First party modules
from pynball import pynball


def test_rmproject_nove(monkeypatch, create_env, mock_get_env):
    runner = CliRunner()
    monkeypatch.setattr(pynball, "_WORKON_HOME", Path(""))
    monkeypatch.setattr(pynball, "_PROJECT_HOME", pytest.PROJECT_HOME)

    result = runner.invoke(pynball.rmproject, ["project2"])
    assert result.exit_code == 0
    assert result.output == (
        "WARNING: Virtualenv-wrapper is not configured on your system:\n"
        "        Please install Virtualenv and Virtualenv-wrapper and configure\n"
        "        'WORKON_HOME' and 'PROJECT_HOME' environment variables\n"
    )


def test_rmproject_noproject(monkeypatch, create_env, mock_get_env):
    runner = CliRunner()
    monkeypatch.setattr(pynball, "_WORKON_HOME", pytest.WORKON_HOME)
    monkeypatch.setattr(pynball, "_PROJECT_HOME", pytest.PROJECT_HOME)

    result = runner.invoke(pynball.rmproject, ["project3"])
    assert result.output == "WARNING: Project: 'project3' does not exist\n"


def test_rmproject_delvenv(monkeypatch, create_env, mock_get_env):
    """test deletion of venv directory"""
    pass


def test_rmproject_deldev(monkeypatch, create_env, mock_get_env):
    """test deletion of venv and dev directories"""
    pass
