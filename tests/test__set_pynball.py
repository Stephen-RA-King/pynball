# Core Library modules
from pathlib import Path

# Third party modules
import pytest

# First party modules
from pynball import pynball


def test_set_pynball1(capsys, mock_set_env_output):
    dict_object = {"3.6": Path("D:\\Python\\python3.6")}
    pynball._set_pynball(dict_object)
    output, error = capsys.readouterr()
    assert output == "{'3.6': 'D:\\\\Python\\\\python3.6'}\n"
    assert error == ""
