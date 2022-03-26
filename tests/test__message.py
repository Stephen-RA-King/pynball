# Core Library modules
from pathlib import Path, PurePath, WindowsPath

# Third party modules
import pytest
from click.testing import CliRunner

# First party modules
from pynball import pynball


@pytest.mark.parametrize(
    "message, message_type, result",
    [
        ("this is a null message", "null", "None"),
        ("this is a nominal message", "nominal", "None"),
        ("this is a warning message", "warning", "None"),
        ("this is an error message", "error", "None"),
        ("this is an error message", "wrong", "None"),
    ],
)
def test_feedback(message, message_type, result):
    """Pytest test to assert mark parametrize pytest feature."""
    assert result == str(pynball._feedback(message, message_type))
