# Core Library modules
from pathlib import Path, PurePath, WindowsPath

# Third party modules
import pytest
from click.testing import CliRunner

# First party modules
from pynball import pynball


def test_add(mock_get_env):
    runner = CliRunner()
    new_path = str(pytest.PYTHON_DIR / "3.8.10")
    result = runner.invoke(pynball.version)
    assert result.exit_code == 0
    assert result.output == "3.9.10  ReleaseLevel: final, Serial: 0\n"
