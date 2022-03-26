# Core Library modules
import re
import sys

# First party modules
from pynball import pynball


def test_execute():
    pattern = r"\d+.\d+.\d+"
    py_ver_script = "{0.major}.{0.minor}.{0.micro}".format(sys.version_info)
    py_ver_cli = pynball._execute("python", "--version")
    assert re.findall(pattern, py_ver_script) == re.findall(pattern, py_ver_cli)
