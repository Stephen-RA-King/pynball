# Core Library modules
import shutil
from pathlib import Path

# Third party modules
import pytest

# First party modules
from pynball import pynball

BASE_DIR = Path(__file__).parents[1]
TEST_ENV = BASE_DIR / "env"
WORKON_HOME = TEST_ENV / "virtual_env" / "pyvenv"
PROJECT_HOME = TEST_ENV / "virtual_env" / "dev"
PYENV_HOME = TEST_ENV / "versions"
PYTHON_DIR = TEST_ENV / "PYTHON"


def pytest_configure():
    pytest.BASE_DIR = Path(__file__).parents[1]
    pytest.TEST_ENV = BASE_DIR / "env"
    pytest.WORKON_HOME = TEST_ENV / "virtual_env" / "pyvenv"
    pytest.PROJECT_HOME = TEST_ENV / "virtual_env" / "dev"
    pytest.PYENV_HOME = TEST_ENV / "versions"
    pytest.PYTHON_DIR = TEST_ENV / "PYTHON"


path1 = str(PYTHON_DIR / "3.9.10")
path2 = str(PYTHON_DIR / "3.9.10" / "Scripts")
path_env = "".join(
    ["Path=", path1, "\\", ";", path2, "\\", ";", r"C:\WINDOWS\system32;C:\WINDOWS"]
)


newdict = {}
for vers in ["3.6.8", "3.7.9", "3.9.10"]:
    penv = PYTHON_DIR / vers
    newdict[vers] = penv
pynball_raw_dict = {name: str(path) for name, path in newdict.items()}
pynball_env = str(pynball_raw_dict)


@pytest.fixture()
def create_env(monkeypatch):
    pyenv_ver = ["3.5.4", "3.9.10", "3.10.3"]
    python_ver = [
        ("3.6.8", "n"),
        ("3.7.9", "y"),
        ("3.8.10", "y"),
        ("3.9.10", "y"),
        ("3.10.2", "y"),
    ]
    TEST_ENV.mkdir()
    ve_dir = TEST_ENV / "virtual_env"
    ve_dir.mkdir()
    WORKON_HOME.mkdir()
    PROJECT_HOME.mkdir()
    for project in ["project1", "project2"]:
        (WORKON_HOME / project).mkdir()
        (WORKON_HOME / project / "pyvenv.cfg").touch()
        (WORKON_HOME / project / "pyvenv.cfg").write_text("version_info = 3.9.10")
        (PROJECT_HOME / project).mkdir()
        (PROJECT_HOME / project / ".python-version").touch()
        (PROJECT_HOME / project / ".python-version").write_text("3.8.10\n3.9.10")

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

    yield
    shutil.rmtree(TEST_ENV)


@pytest.fixture
def mock_check_pyenv(monkeypatch):
    def mock_checkpyenv(*args, **kwargs):
        return 1

    monkeypatch.setattr(pynball, "_check_pyenv", mock_checkpyenv)


@pytest.fixture
def mock_get_env(monkeypatch):
    def mock_getenv(scope, name):
        if scope == "user" and name == "PYNBALL":
            return pynball_env
        elif scope == "system" and name == "PATH":
            return path_env
        else:
            return

    monkeypatch.setattr(pynball, "_getenv", mock_getenv)


@pytest.fixture
def mock_set_env(monkeypatch):
    def mock_setenv(scope, name, value):
        if scope == "user" and name == "PYNBALL":
            return
        elif scope == "system" and name == "PATH":
            return
        else:
            return

    monkeypatch.setattr(pynball, "_setenv", mock_setenv)


@pytest.fixture
def mock_set_env_output(monkeypatch):
    def mock_setenv(scope, name, value):
        if scope == "user" and name == "PYNBALL":
            print(value)
        elif scope == "system" and name == "PATH":
            print(value)
        else:
            return

    monkeypatch.setattr(pynball, "_setenv", mock_setenv)
