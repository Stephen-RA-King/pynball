# Core Library modules
from pathlib import Path, PurePath, WindowsPath

# Third party modules
import pytest
from click.testing import CliRunner

# First party modules
from pynball import pynball


def test_add(create_env, mock_get_env, mock_set_env):
    runner = CliRunner()
    new_path = str(pytest.PYTHON_DIR / "3.8.10")
    result = runner.invoke(pynball.add, ["3.8.10", new_path])
    assert result.exit_code == 0
    assert result.output == "'3.8.10' Successfully added to configuration\n"


def test_add_noexe(create_env, mock_get_env, mock_set_env):
    runner = CliRunner()
    new_path = str(pytest.PYTHON_DIR / "3.6.8")
    result = runner.invoke(pynball.add, ["3.6.8", new_path])
    assert result.exit_code == 0
    assert result.output == "WARNING: There is no Python Interpreter on that path\n"


def test_add_exists(create_env, mock_get_env, mock_set_env):
    runner = CliRunner()
    new_path = str(pytest.PYTHON_DIR / "3.7.9")
    result = runner.invoke(pynball.add, ["3.7.9", new_path])
    assert result.exit_code == 0
    assert (
        result.output == "WARNING: '3.7.9' already added to configuration as '3.7.9'\n"
    )
