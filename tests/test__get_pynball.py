# Core Library modules
from pathlib import WindowsPath

# Third party modules
import pytest

# First party modules
from pynball import pynball

BASE = WindowsPath(__file__).resolve().parents[3]
VERSIONS = ["3.6.8", "3.7.9", "3.9.10"]


def test_get_pynball_notype(capsys, mock_get_env) -> None:
    pynball._get_pynball("nosuchthing", "PYNBALL")
    captured = capsys.readouterr()
    assert (
        captured.out == "WARNING: Please use a correct returntype - "
        "('string', 'dict', 'dict_path_object', 'names', 'paths')\n"
    )


def test_get_pynball_string(mock_get_env) -> None:
    """generated string should look similar to the following
    pynball._get_pynball("string", "PYNBALL") == (
        "{'3.6.8': 'D:\\\\PYTHON "
        "PROJECT\\\\PROJECTS\\\\DEV\\\\pynball\\\\pynball\\\\env\\\\PYTHON\\\\3.6.8', "
        "'3.7.9': 'D:\\\\PYTHON "
        "PROJECT\\\\PROJECTS\\\\DEV\\\\pynball\\\\pynball\\\\env\\\\PYTHON\\\\3.7.9', "
        "'3.9.10': 'D:\\\\PYTHON "
        "PROJECT\\\\PROJECTS\\\\DEV\\\\pynball\\\\pynball\\\\env\\\\PYTHON\\\\3.9.10'}"
    )
    """
    get_str = pynball._get_pynball("string", "PYNBALL")
    for ver in VERSIONS:
        assert f"pynball\\\\pynball\\\\env\\\\PYTHON\\\\{ver}" in get_str


def test_get_pynball_dict(mock_get_env) -> None:
    """Generated dictionary should look similar to the following
    pynball._get_pynball("dict", "PYNBALL") == {
        "3.6.8": "D:\\PYTHON "
        "PROJECT\\PROJECTS\\DEV\\pynball\\pynball\\env\\PYTHON\\3.6.8",
        "3.7.9": "D:\\PYTHON "
        "PROJECT\\PROJECTS\\DEV\\pynball\\pynball\\env\\PYTHON\\3.7.9",
        "3.9.10": "D:\\PYTHON "
        "PROJECT\\PROJECTS\\DEV\\pynball\\pynball\\env\\PYTHON\\3.9.10",
    }
    """
    get_dict = pynball._get_pynball("dict", "PYNBALL")
    for ver in VERSIONS:
        assert f"pynball\\pynball\\env\\PYTHON\\{ver}" in get_dict[f"{ver}"]


def test_get_pynball_object(mock_get_env) -> None:
    """Generated dictionary should look similar to the following:
    pynball._get_pynball("dict_path_object", "PYNBALL") == {
        "3.6.8": WindowsPath(
            "D:/PYTHON PROJECT/PROJECTS/DEV/pynball/pynball/env/PYTHON/3.6.8"
        ),
        "3.7.9": WindowsPath(
            "D:/PYTHON PROJECT/PROJECTS/DEV/pynball/pynball/env/PYTHON/3.7.9"
        ),
        "3.9.10": WindowsPath(
            "D:/PYTHON PROJECT/PROJECTS/DEV/pynball/pynball/env/PYTHON/3.9.10"
        ),
    }
    """
    path_object_dict = pynball._get_pynball("dict_path_object", "PYNBALL")
    for ver in VERSIONS:
        assert str(WindowsPath(f"pynball/pynball/env/PYTHON/{ver}")) in str(
            path_object_dict[f"{ver}"]
        )


def test_get_pynball_names(mock_get_env) -> None:
    assert pynball._get_pynball("names", "PYNBALL") == ["3.6.8", "3.7.9", "3.9.10"]


def test_get_pynball_paths(mock_get_env) -> None:
    """Generated list should look similar to the following
    assert pynball._get_pynball("paths", "PYNBALL") == [
        "D:\\PYTHON PROJECT\\PROJECTS\\DEV\\pynball\\pynball\\env\\PYTHON\\3.6.8",
        "D:\\PYTHON PROJECT\\PROJECTS\\DEV\\pynball\\pynball\\env\\PYTHON\\3.7.9",
        "D:\\PYTHON PROJECT\\PROJECTS\\DEV\\pynball\\pynball\\env\\PYTHON\\3.9.10",
    ]
    """
    paths_list = pynball._get_pynball("paths", "PYNBALL")
    for index, ver in enumerate(VERSIONS):
        assert f"pynball\\pynball\\env\\PYTHON\\{ver}" in paths_list[index]
