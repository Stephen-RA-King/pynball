# Core Library modules
from pathlib import Path, PurePath, WindowsPath

# Third party modules
import pytest
from click.testing import CliRunner

# First party modules
from pynball import pynball


def test_versions(mock_get_env):
    runner = CliRunner()
    result = runner.invoke(pynball.versions)
    assert result.exit_code == 0
    assert result.output == (
        "WARNING: System Interpreter is not configured\n"
        "3.6.8     D:\\PYTHON "
        "PROJECT\\PROJECTS\\DEV\\pynball\\pynball\\env\\PYTHON\\3.6.8\n"
        "3.7.9     D:\\PYTHON "
        "PROJECT\\PROJECTS\\DEV\\pynball\\pynball\\env\\PYTHON\\3.7.9\n"
        "3.9.10    D:\\PYTHON "
        "PROJECT\\PROJECTS\\DEV\\pynball\\pynball\\env\\PYTHON\\3.9.10\n"
    )
