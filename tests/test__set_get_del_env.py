# Third party modules
import pytest

# First party modules
from pynball import pynball


@pytest.mark.dependency()
def test_set_env(capsys):
    """Test case to check environmental variable getter and setter methods"""
    # Setter
    pynball._setenv("unknown", "DELETEKEY", "deletevalue")
    output, error = capsys.readouterr()
    assert output == "WARNING: Scope value must be 'user' or 'system'\n"
    assert error == ""
    pynball._setenv("user", "DELETEKEY", "deletevalue")
    output, error = capsys.readouterr()
    assert output == ""
    assert error == ""
    pynball._setenv("system", "DELETEKEY", "deletevalue")
    output, error = capsys.readouterr()
    assert output == ""
    assert error == ""


@pytest.mark.dependency(depends=["test_set_env"])
def test_get_env(capsys):
    pynball._getenv("unknown", "DELETEKEY")
    output, error = capsys.readouterr()
    assert output == "WARNING: Scope value must be 'user' or 'system'\n"
    assert error == ""
    pynball._getenv("user", "DELETEKEY")
    output, error = capsys.readouterr()
    assert output == ""
    assert error == ""
    pynball._getenv("system", "DELETEKEY")
    output, error = capsys.readouterr()
    assert output == ""
    assert error == ""


@pytest.mark.dependency(depends=["test_set_env"])
def test_del_env(capsys):
    pynball._delenv("unknown", "DELETEKEY")
    output, error = capsys.readouterr()
    assert output == "WARNING: Scope value must be 'user' or 'system'\n"
    assert error == ""
    pynball._delenv("user", "DELETEKEY")
    output, error = capsys.readouterr()
    assert output == ""
    assert error == ""
    pynball._delenv("system", "DELETEKEY")
    output, error = capsys.readouterr()
    assert output == ""
    assert error == ""
