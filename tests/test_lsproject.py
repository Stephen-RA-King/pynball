# Core Library modules
from pathlib import Path, PurePath, WindowsPath

# Third party modules
import pytest
from click.testing import CliRunner

# First party modules
from pynball import pynball


def test_lsproject(monkeypatch, create_env, mock_get_env):
    runner = CliRunner()
    monkeypatch.setattr(pynball, "_WORKON_HOME", pytest.WORKON_HOME)
    monkeypatch.setattr(pynball, "_PROJECT_HOME", pytest.PROJECT_HOME)

    result = runner.invoke(pynball.lsproject)
    assert result.exit_code == 0
    assert result.output == (
        "Project Name             System Version           Pyenv Versions\n"
        "============             ==============           ==============\n"
        "project1                 3.9.10                   3.8.10, 3.9.10\n"
        "project2                 3.9.10                   3.8.10, 3.9.10\n"
    )
