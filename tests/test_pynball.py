#!/usr/bin/env python3
"""Tests for package pynball.py"""

# Core Library modules
import os
import re
import sys
import winreg

# Third party modules
import pytest

# First party modules
from src.pynball.pynball import Pynball

pb = Pynball()


PYNBALL_BACKUP = os.environ["PYNBALL"]
PATH_BACKUP = getenv("system", "PATH")
WORKON_HOME_BACKUP = os.environ["WORKON_HOME"]
PROJECT_HOME_BACKUP = os.environ["PROJECT_HOME"]
HOMEPATH = os.environ["HOMEPATH"]


def test_execute():
    pattern = r"\d+.\d+.\d+"
    py_ver_script = "{0.major}.{0.minor}.{0.micro}".format(sys.version_info)
    py_ver_cli = Pynball._execute("python", "--version")
    assert re.findall(pattern, py_ver_script) == re.findall(pattern, py_ver_cli)


@pytest.mark.parametrize(
    "message, message_type, result",
    [
        ("this is a null message", "null", "None"),
        ("this is a nominal message", "nominal", "None"),
        ("this is a warning message", "warning", "None"),
        ("this is an error message", "error", "None"),
        ("this is an error message", "wrong", "Incorrect feedback type"),
    ],
)
def test_feedback(message, message_type, result):
    """Pytest test to assert mark parametrize pytest feature."""
    assert result == str(Pynball._feedback(message, message_type))


def test_set_get_del_env():
    """Test case to check environmental variable getter and setter mkethods"""
    # Setter
    assert "Scope value must be 'user' or 'system'" == pb._setenv(
        "unknown", "DELETEKEY", "deletevalue"
    )
    assert None is pb._setenv("user", "DELETEKEY", "deletevalue")
    assert None is pb._setenv("system", "DELETEKEY", "deletevalue")
    # Getter
    assert "Scope value must be 'user' or 'system'" == pb._getenv(
        "unknown", "DELETEKEY"
    )
    assert "deletevalue" == pb._getenv("user", "DELETEKEY")
    assert "deletevalue" == pb._getenv("system", "DELETEKEY")
    # Deleter
    assert "Scope value must be 'user' or 'system'" == pb._delenv(
        "unknown", "DELETEKEY"
    )
    assert None is pb._delenv("user", "DELETEKEY")
    assert None is pb._delenv("system", "DELETEKEY")


def test_set_pynball():
    pass


def test_get_pynball():
    pass


def test_get_system_path():
    pass


def test_add_version():
    pass


def test_delete_version():
    pass


def test_clear_versions():
    pass


def test_version():
    pass


def test_versions():
    pass


def test_switchto():
    pass


def test_pypath():
    pass


def test_mkproject():
    pass


'''
# ======= START PYTEST FUNCTIONS =====================================================
# pytest.raises
def test_doubleit_except_type():
    """Pytest test to assert raises pytest feature."""
    with pytest.raises(TypeError):
        pynball.doubleit("hello")


# pytest.raises
def test_doubleit_except_message():
    """Pytest test to assert raises pytest feature."""
    with pytest.raises(TypeError, match="Enter an Integer"):
        pynball.doubleit("hello")


# pytest.warns - Alternative way to check warnings
def test_lame_function_warns():
    """Pytest test to assert warns pytest feature."""
    with pytest.warns(DeprecationWarning, match=".*Please stop using this.*"):
        pynball.lame_function()


# pytest.approx
def test_approx():
    """Pytest test to assert approx pytest feature."""
    assert pynball.addit(0.1, 0.2) == pytest.approx(0.3)


# ======= START EXCEPTION TESTS ======================================================
def test_div_by_zero():
    """Pytest test to assert raises pytest feature."""
    with pytest.raises(ZeroDivisionError):
        pynball.div_by_zero()


def test_check_message():
    """Pytest test to assert raises pytest feature"""
    with pytest.raises(ValueError) as excinfo:
        pynball.check_message("dog")
    exception_msg = excinfo.value.args[0]
    assert exception_msg == "pet must be cat"


def test_manual_exc():
    """Pytest test to assert raises pytest feature."""
    with pytest.raises(ValueError):
        if pynball.manual_exception() > 5:
            raise ValueError("value must be <= 5")


# ======= START MARKING TESTS ========================================================
@pytest.mark.skip(reason="misunderstood the API")
def test_ignore_this():
    """Pytest test to assert mark skip pytest feature."""
    assert 1 == 2


@pytest.mark.skipif("0.1.0" < "0.3.0", reason="not supported until version 0.3.0")
def test_ignore_this2():
    """Pytest test to assert mark skip if pytest feature."""
    assert 1 == 2


# skip imperatively during test execution
def test_if_not_windows():
    """Pytest test to skip imperatively during test execution."""
    if sys.platform.startswith("win"):
        pytest.skip("skipping windows-only tests")


@pytest.mark.xfail(reason="not supported until version 0.3.0")
def test_expected_fail_and_fails():
    """Pytest test to assert mark xfail pytest feature."""
    assert 1 == 2


@pytest.mark.parametrize(
    "length, pet",
    [
        (3, "cat"),
        (3, "dog"),
        (7, "hamster"),
        (6, "gerbil"),
    ],
)
def test_param_example(length, pet):
    """Pytest test to assert mark parametrize pytest feature."""
    assert length == len(pet)


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_userwarning():
    """Pytest test to assert mark filterwarnings pytest feature."""
    warnings.warn("this is a warning", UserWarning)
'''
