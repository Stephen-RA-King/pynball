# Core Library modules
from pathlib import Path

# Third party modules
import pytest

# First party modules
from pynball import pynball


@pytest.mark.parametrize(
    "ph, out, err, return_value",
    [
        (Path("C:\\"), "", "", 0),
        (Path(""), "WARNING: Pyenv is not configured.\n", "", 1),
    ],
)
def test_check_pyenv(capsys, ph, out, err, return_value):
    pynball._PYENV_HOME = ph
    x = pynball._check_pyenv()
    output, error = capsys.readouterr()
    assert output == out
    assert error == err
    assert x == return_value
