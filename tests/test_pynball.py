#!/usr/bin/env python3
"""Tests for package pynball.py"""

# Core Library modules
import ast
import os
import re
import shutil
import sys
import winreg
from pathlib import Path, PurePath, WindowsPath

# Third party modules
import pytest

# First party modules
from pynball.pynball import Pynball

BASE_DIR = Path(__file__).parent
TEST_ENV = BASE_DIR / "test_env"
WORKON_HOME = TEST_ENV / "virtual_env" / "pyvenv"
PROJECT_HOME = TEST_ENV / "virtual_env" / "dev"
# pynball_pyenv = "0"
PYENV_HOME = BASE_DIR / "test_env" / "versions"
PYTHON_DIR = TEST_ENV / "PYTHON"


pb = Pynball()


def create_env():
    pyenv_ver = ["3.8", "3.9.2", "3.10.3"]
    python_ver = [
        ("python3.6", "n"),
        ("python3.7", "y"),
        ("python3.8", "y"),
        ("python3.9", "y"),
        ("python3.10", "y"),
    ]
    TEST_ENV.mkdir()
    ve_dir = TEST_ENV / "virtual_env"
    ve_dir.mkdir()
    WORKON_HOME.mkdir()
    PROJECT_HOME.mkdir()

    PYENV_HOME.mkdir()
    for ver in pyenv_ver:
        (PYENV_HOME / ver).mkdir()

    PYTHON_DIR.mkdir()
    for ver in python_ver:
        name, mkfile = ver
        pyver = PYTHON_DIR / name
        pyver.mkdir()
        if mkfile == "y":
            (pyver / "python.exe").touch()
            (pyver / "python.exe").write_text(f"This is version {name}")


create_env()


def feedback(message, _):
    """A utility method to generate nicely formatted messages"""
    print(f"{message}")


# monkey patch for _setenv(scope, name, value)
def create_file(scope: str, name: str, value: str) -> None:
    filename = "".join([scope, "_", name])
    (BASE_DIR / filename).touch()
    (BASE_DIR / filename).write_text(value)


# monkey patch for _getenv(scope, name)
def read_file(scope: str, name: str) -> str:
    filename = "".join([scope, "_", name])
    with (BASE_DIR / filename).open() as f:
        value = f.read()
        value = value.replace("\\\\", "\\")
        return value


# monkey patch for _delenv(scope, name)
def del_file(scope: str, name: str) -> None:
    filename = "".join([scope, "_", name])
    (BASE_DIR / filename).unlink()


def create_system_path_variable():
    value = (
        r"D:\PYTHON\python3.9\;"
        r"D:\PYTHON\python3.9\Scripts\;"
        r"C:\Program Files (x86)\Common Files\Oracle\Java\javapath;"
        r"C:\WINDOWS\system32;"
        r"C:\WINDOWS;"
    )
    create_file("system", "PATH", value)


def create_pynball_variable():
    value = (
        "{'3.10': 'D:\\PYTHON\\python3.10',"
        "'3.9': 'D:\\PYTHON\\python3.9',"
        "'3.8': 'D:\\PYTHON\\python3.8'}"
    )
    create_file("user", "PYNBALL", value)


# ========================== BEGIN TESTS =====================================
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
    assert result == str(pb._feedback(message, message_type))


def test_help():
    pass


def test_execute():
    pattern = r"\d+.\d+.\d+"
    py_ver_script = "{0.major}.{0.minor}.{0.micro}".format(sys.version_info)
    py_ver_cli = Pynball._execute("python", "--version")
    assert re.findall(pattern, py_ver_script) == re.findall(pattern, py_ver_cli)


@pytest.mark.parametrize(
    "wh, ph, out, err, return_value",
    [
        (Path("C:\\"), Path("C:\\"), "", "", 0),
        (Path(""), Path("C:\\"), "Virtualenv-wrapper is not configured.\n", "", 1),
        (Path("C:\\"), Path(""), "Virtualenv-wrapper is not configured.\n", "", 1),
        (Path(""), Path(""), "Virtualenv-wrapper is not configured.\n", "", 1),
    ],
)
def test_check_virtual_env(capsys, wh, ph, out, err, return_value):
    pb._feedback = feedback
    pb.workon_home = wh
    pb.project_home = ph
    x = pb._check_virtual_env()
    output, error = capsys.readouterr()
    assert output == out
    assert error == err
    assert x == return_value


@pytest.mark.parametrize(
    "ph, out, err, return_value",
    [
        (Path("C:\\"), "", "", 0),
        (Path(""), "Pyenv is not configured.\n", "", 1),
    ],
)
def test_check_pyenv(capsys, ph, out, err, return_value):
    pb._feedback = feedback
    pb.pyenv_home = ph
    x = pb._check_pyenv()
    output, error = capsys.readouterr()
    assert output == out
    assert error == err
    assert x == return_value


def test_set_get_del_env():
    """Test case to check environmental variable getter and setter methods"""
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


def test_set_pynball1():
    pb._setenv = create_file  # monkey patch method
    dict_object = {"3.6": Path("D:\\Python\\python3.6")}
    pb._set_pynball(dict_object)
    assert read_file("user", "PYNBALL") == "{'3.6': 'D:\\Python\\python3.6'}"
    del_file("user", "PYNBALL")


def test_get_pynball(capsys):
    pb._feedback = feedback
    pb._getenv = read_file  # monkey patch method
    create_pynball_variable()
    """
    value = (
        "{'3.10': 'D:\\PYTHON\\python3.10','3.9': 'D:\\PYTHON\\python3.9',"
        "'3.8': 'D:\\PYTHON\\python3.8','3.7': 'D:\\PYTHON\\python3.7',"
        "'3.6': 'D:\\PYTHON\\python3.6'}"
    )
    create_file("user", "PYNBALL", value)
    """

    pb._get_pynball("nosuchthing")
    captured = capsys.readouterr()
    assert (
        captured.out == "Please use a correct returntype - "
        "('string', 'dict', 'dict_path_object', 'names', 'paths')\n"
    )
    # assert captured.err == ""

    assert (
        pb._get_pynball("string") == ""
        "{'3.10': 'D:\\PYTHON\\python3.10',"
        "'3.9': 'D:\\PYTHON\\python3.9',"
        "'3.8': 'D:\\PYTHON\\python3.8',"
        "'3.7': 'D:\\PYTHON\\python3.7',"
        "'3.6': 'D:\\PYTHON\\python3.6'}"
    )
    assert pb._get_pynball("dict") == {
        "3.10": "D:\\PYTHON\\python3.10",
        "3.9": "D:\\PYTHON\\python3.9",
        "3.8": "D:\\PYTHON\\python3.8",
        "3.7": "D:\\PYTHON\\python3.7",
        "3.6": "D:\\PYTHON\\python3.6",
    }
    assert pb._get_pynball("dict_path_object") == {
        "3.10": WindowsPath("D:/PYTHON/python3.10"),
        "3.9": WindowsPath("D:/PYTHON/python3.9"),
        "3.8": WindowsPath("D:/PYTHON/python3.8"),
        "3.7": WindowsPath("D:/PYTHON/python3.7"),
        "3.6": WindowsPath("D:/PYTHON/python3.6"),
    }
    assert pb._get_pynball("names") == ["3.10", "3.9", "3.8", "3.7", "3.6"]
    assert pb._get_pynball("paths") == [
        "D:\\PYTHON\\python3.10",
        "D:\\PYTHON\\python3.9",
        "D:\\PYTHON\\python3.8",
        "D:\\PYTHON\\python3.7",
        "D:\\PYTHON\\python3.6",
    ]
    del_file("user", "PYNBALL")


def test_get_system_path():
    pb._getenv = read_file  # monkey patch method
    create_system_path_variable()
    create_pynball_variable()
    sys_path, pynball_name = pb._get_system_path()
    assert sys_path == ["D:\\PYTHON\\python3.9\\"]
    assert pynball_name == ["3.9"]
    del_file("system", "PATH")
    del_file("user", "PYNBALL")


@pytest.mark.parametrize(
    "name, path, out, err",
    [
        ("3.6", "python3.6", "There is no python executable on that path\n", ""),
        ("3.8", "python3.8", "3.8  already added to configuration as 3.8\n", ""),
    ],
)
def test_add_version(capsys, name, path, out, err):
    pb._feedback = feedback
    pb._getenv = read_file  # monkey patch method
    pb._setenv = create_file
    pb._delenv = del_file
    create_system_path_variable()
    create_pynball_variable()

    verpath = str(PurePath(PYTHON_DIR, path))
    pb.add("name", verpath)
    output, error = capsys.readouterr()
    assert output == out
    assert error == err
    del_file("system", "PATH")
    del_file("user", "PYNBALL")


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


def test_include_pyenv():
    pass


def test_mkproject():
    pass


def test_rmproject():
    pass


def test_lsproject():
    pass


def test_export_config():
    pass


def test_import_config():
    pass


# shutil.rmtree((BASE_DIR / "test_env"))


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
