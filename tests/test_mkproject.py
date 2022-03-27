# Core Library modules
from pathlib import Path, PurePath, WindowsPath

# Third party modules
import pytest
from click.testing import CliRunner

# First party modules
from pynball import pynball


def test_mkproject_nove(monkeypatch, create_env, mock_get_env):
    runner = CliRunner()
    monkeypatch.setattr(pynball, "_WORKON_HOME", Path(""))
    monkeypatch.setattr(pynball, "_PROJECT_HOME", pytest.PROJECT_HOME)

    result = runner.invoke(pynball.mkproject, ["3.6.8", "project2"])
    assert result.exit_code == 0
    assert result.output == (
        "WARNING: Virtualenv-wrapper is not configured on you system:\n"
        "        Please install Virtualenv and Virtualenv-wrapper and configure\n"
        "        'WORKON_HOME' and 'PROJECT_HOME' environment variables\n"
    )


def test_mkproject_existing(monkeypatch, create_env, mock_get_env):
    runner = CliRunner()
    monkeypatch.setattr(pynball, "_WORKON_HOME", pytest.WORKON_HOME)
    monkeypatch.setattr(pynball, "_PROJECT_HOME", pytest.PROJECT_HOME)

    result = runner.invoke(pynball.mkproject, ["3.6.8", "project2"])
    assert result.exit_code == 0
    assert result.output == "WARNING: The directory 'project2' already exits\n"


def test_mkproject_noversion(monkeypatch, create_env, mock_get_env):
    runner = CliRunner()
    monkeypatch.setattr(pynball, "_WORKON_HOME", pytest.WORKON_HOME)
    monkeypatch.setattr(pynball, "_PROJECT_HOME", pytest.PROJECT_HOME)

    result = runner.invoke(pynball.mkproject, ["1.1.1", "project3"])
    assert result.exit_code == 0
    assert (
        result.output
        == "WARNING: 1.1.1 is not configured in Pynball - Use the 'add' command\n"
    )
