"""Test configuration.

pynball.py is a Windows-only tool (it imports `winreg` unconditionally and
exits at import time if `sys.platform != "win32"`). To unit test it on any
platform, we:

1. Install lightweight stub modules for `winreg` and `magic` (python-magic,
   which needs the libmagic shared library) into sys.modules *before*
   pynball is imported anywhere.
2. Temporarily pretend to be "win32" for the duration of the import so the
   module-level platform guard passes and `_PLATFORM` gets set correctly.

Every test then interacts with the real `pynball` module, but registry and
libmagic calls go through mocks that individual tests configure via
monkeypatch.
"""

from __future__ import annotations

import sys
import types
from unittest import mock

import pytest


def _install_winreg_stub() -> types.ModuleType:
    stub = types.ModuleType("winreg")
    stub.HKEY_CURRENT_USER = 1
    stub.HKEY_LOCAL_MACHINE = 2
    stub.KEY_ALL_ACCESS = 0xF003F
    stub.REG_SZ = 1
    stub.OpenKey = mock.MagicMock(name="OpenKey")
    stub.CreateKey = mock.MagicMock(name="CreateKey")
    stub.SetValueEx = mock.MagicMock(name="SetValueEx")
    stub.QueryValueEx = mock.MagicMock(name="QueryValueEx", return_value=("", 1))
    stub.CloseKey = mock.MagicMock(name="CloseKey")
    stub.DeleteValue = mock.MagicMock(name="DeleteValue")
    return stub


def _install_magic_stub() -> types.ModuleType:
    stub = types.ModuleType("magic")

    class _FakeMagic:
        def __init__(self, mime: bool = True) -> None:
            self.mime = mime

        def from_file(self, path: str) -> str:
            return "text/plain"

    stub.Magic = _FakeMagic
    return stub


def _install_msvcrt_stub() -> types.ModuleType:
    stub = types.ModuleType("msvcrt")
    stub.get_osfhandle = mock.MagicMock(name="get_osfhandle")
    return stub


sys.modules.setdefault("winreg", _install_winreg_stub())
sys.modules.setdefault("magic", _install_magic_stub())
sys.modules.setdefault("msvcrt", _install_msvcrt_stub())

# Import click under the *real* platform first. click's own import picks a
# different internal codepath on win32 (touching ctypes.windll, which does
# not exist off Windows); pre-importing it here means pynball's later
# `import click` just reuses this already-initialised, Linux-safe module.
import click  # noqa: E402,F401

_original_platform = sys.platform
sys.platform = "win32"
try:
    from pynball import pynball  # noqa: E402
finally:
    sys.platform = _original_platform


@pytest.fixture()
def pb():
    """Return the imported pynball module for convenience."""
    return pynball
