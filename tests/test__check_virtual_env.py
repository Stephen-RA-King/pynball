# Core Library modules
from pathlib import Path

# Third party modules
import pytest

# First party modules
from pynball import pynball


def feedback(message, _):
    """A utility method to generate nicely formatted messages"""
    print(f"{message}")


@pytest.mark.parametrize(
    "wh, ph, out, err, return_value",
    [
        (Path("C:\\"), Path("C:\\"), "", "", 0),
        (
            Path(""),
            Path("C:\\"),
            "WARNING: Virtualenv-wrapper is not configured.\n",
            "",
            1,
        ),
        (
            Path("C:\\"),
            Path(""),
            "WARNING: Virtualenv-wrapper is not configured.\n",
            "",
            1,
        ),
        (Path(""), Path(""), "WARNING: Virtualenv-wrapper is not configured.\n", "", 1),
    ],
)
def test_check_virtual_env(capsys, wh, ph, out, err, return_value):
    # pb._feedback = feedback
    pynball._WORKON_HOME = wh
    pynball._PROJECT_HOME = ph
    x = pynball._check_virtual_env()
    output, error = capsys.readouterr()
    assert output == out
    assert error == err
    assert x == return_value
