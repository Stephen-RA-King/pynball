# Core Library modules
from pathlib import Path, PurePath, WindowsPath

# Third party modules
import pytest
from click.testing import CliRunner

# First party modules
from pynball import pynball


def test_delete(create_env, mock_get_env, mock_set_env):
    runner = CliRunner()
    result = runner.invoke(pynball.delete, ["3.6.8"])
    assert result.exit_code == 0
    assert result.output == ""


def test_delete_noentry(create_env, mock_get_env, mock_set_env):
    runner = CliRunner()
    result = runner.invoke(pynball.delete, ["3.5.3"])
    assert result.exit_code == 0
    assert result.output == ""


def test_delete_system(create_env, mock_get_env, mock_set_env):
    runner = CliRunner()
    result = runner.invoke(pynball.delete, ["3.9.10"])
    assert result.exit_code == 0
    assert result.output == "WARNING: Cannot delete System Interpreter\n"
