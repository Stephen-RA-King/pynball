# Core Library modules
from pathlib import WindowsPath

# Third party modules
import pytest

# First party modules
from pynball import pynball


def test_get_pynball_notype(capsys, mock_get_env):
    pynball._get_pynball("nosuchthing", "PYNBALL")
    captured = capsys.readouterr()
    assert (
        captured.out == "WARNING: Please use a correct returntype - "
        "('string', 'dict', 'dict_path_object', 'names', 'paths')\n"
    )


def test_get_pynball_string(mock_get_env):
    assert pynball._get_pynball("string", "PYNBALL") == (
        "{'3.6.8': 'D:\\\\PYTHON "
        "PROJECT\\\\PROJECTS\\\\DEV\\\\pynball\\\\pynball\\\\env\\\\PYTHON\\\\3.6.8', "
        "'3.7.9': 'D:\\\\PYTHON "
        "PROJECT\\\\PROJECTS\\\\DEV\\\\pynball\\\\pynball\\\\env\\\\PYTHON\\\\3.7.9', "
        "'3.9.10': 'D:\\\\PYTHON "
        "PROJECT\\\\PROJECTS\\\\DEV\\\\pynball\\\\pynball\\\\env\\\\PYTHON\\\\3.9.10'}"
    )


def test_get_pynball_dict(mock_get_env):
    assert pynball._get_pynball("dict", "PYNBALL") == {
        "3.6.8": "D:\\PYTHON "
        "PROJECT\\PROJECTS\\DEV\\pynball\\pynball\\env\\PYTHON\\3.6.8",
        "3.7.9": "D:\\PYTHON "
        "PROJECT\\PROJECTS\\DEV\\pynball\\pynball\\env\\PYTHON\\3.7.9",
        "3.9.10": "D:\\PYTHON "
        "PROJECT\\PROJECTS\\DEV\\pynball\\pynball\\env\\PYTHON\\3.9.10",
    }


def test_get_pynball_object(mock_get_env):
    assert pynball._get_pynball("dict_path_object", "PYNBALL") == {
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


def test_get_pynball_names(mock_get_env):
    assert pynball._get_pynball("names", "PYNBALL") == ["3.6.8", "3.7.9", "3.9.10"]


def test_get_pynball_paths(mock_get_env):
    assert pynball._get_pynball("paths", "PYNBALL") == [
        "D:\\PYTHON PROJECT\\PROJECTS\\DEV\\pynball\\pynball\\env\\PYTHON\\3.6.8",
        "D:\\PYTHON PROJECT\\PROJECTS\\DEV\\pynball\\pynball\\env\\PYTHON\\3.7.9",
        "D:\\PYTHON PROJECT\\PROJECTS\\DEV\\pynball\\pynball\\env\\PYTHON\\3.9.10",
    ]
