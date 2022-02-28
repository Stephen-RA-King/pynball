#!/usr/bin/env python3
"""Tests for package pynball.py"""

# Core Library modules
import os
import sqlite3
import sys
import warnings

# Third party modules
import pytest

# First party modules
from src.pynball import pynball

# ******************FIXTURES ***************************
# fixture moved to conftest


@pytest.fixture(name="cursor")
def db_setup():
    """pytest fixture to create a DB in memory and add a record."""
    db = sqlite3.connect(":memory:")
    cursor = db.cursor()
    cursor.execute(
        """CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT, email TEXT unique)"""
    )
    cursor.execute(
        """INSERT INTO users(name, email)
                      VALUES(?,?)""",
        ("Stephen R A King", "stephen.ra.king@gmail.com"),
    )
    db.commit()
    yield cursor
    db.close()


# Inbuilt fixture - tmpdir_factory
@pytest.fixture(scope="session")
def text_file(tmpdir_factory):
    """pytest fixture for tmpdir_factory feature."""
    fn = tmpdir_factory.mktemp("data").join("bigfile.txt")
    fn.write("content")
    return fn


# Inbuilt fixture - request (Parametrized fixture)
data = [(3, "cat"), (3, "dog"), (7, "hamster"), (6, "gerbil")]


@pytest.fixture(params=data)
def gen_data(request):
    """pytest fixture for request Parametrized data feature."""
    return request.param


# ======= START PYTEST FIXTURES TESTS ================================================


def test_get_db_record(cursor):
    """Pytest test to assert name & email from DB created by fixture."""
    cursor.execute("""SELECT name, email FROM users""")
    user1 = cursor.fetchone()
    assert user1 == ("Stephen R A King", "stephen.ra.king@gmail.com")


# Inbuilt fixture - tmpdir
def test_create_file(tmpdir):
    """pytest test to assert contents of a file using tmpdir pytest feature."""
    p = tmpdir.mkdir("sub").join("hello.txt")
    p.write("content")
    assert p.read() == "content"
    assert len(tmpdir.listdir()) == 1


# Inbuilt fixture - tmpdir_factory
def test_create_file2(text_file):
    """pytest test to assert contents of a file using tmpdir_factory pytest feature."""
    assert text_file.read() == "content"


# Inbuilt fixture - request
def test_func(gen_data):
    """pytest test to assert request Parametrized data pytest feature."""
    assert gen_data[0] == len(gen_data[1])


# Inbuilt fixture -  capsys
def test_output(capsys):
    """pytest test to assert capsys pytest feature."""
    pynball.check_output()
    captured = capsys.readouterr()
    assert captured.out == "hello world\n"
    assert captured.err == ""


# Inbuilt fixture - recwarn
def test_lame_function(recwarn):
    """pytest test to assert recwarn pytest feature."""
    pynball.lame_function()
    assert len(recwarn) == 1
    w = recwarn.pop()
    assert w.category == DeprecationWarning
    assert str(w.message) == "Please stop using this"


# ======= MONKEY PATCHING ============================================================
# Original function may call a real API or access the network, or access a
# real database etc. Monkey patching is useful for replacing this behaviour
# with a mock behaviour that is non-invasive


# def getssh():  # monkeypatch this function - this Original function is not changed
#     return os.path.join(os.path.expanduser("~admin"), "ssh")


# Inbuilt fixture - monkeypatch
def test_mytest(monkeypatch):
    """Pytest test to assert monkeypatch pytest feature."""
    # 1 - set up the mock that will be used instead of the actual function
    def mockreturn(object):
        return "\\abc"

    # 2 - Redirect actual function to mock function
    monkeypatch.setattr(os.path, "expanduser", mockreturn)

    # 3 - now test the actual function
    x = pynball.getssh()
    assert x == "\\abc\\ssh"


# ======= START BASIC TESTS ==========================================================
def test_doubleit():
    """Assert package pynball function return."""
    assert pynball.doubleit(10) == 20


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
