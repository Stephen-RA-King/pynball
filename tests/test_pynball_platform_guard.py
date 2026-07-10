"""Covers the module-level "unsupported platform" guard at the top of
pynball/pynball.py, which can only be exercised by importing the module
fresh under a non-"win32" `sys.platform` - something that must happen in an
isolated subprocess since the main test session has already imported (and
cached) the real module under a spoofed win32 platform. It's also spoofed
here even when running on real Windows, since `sys.platform` would
otherwise genuinely already be "win32" and never trigger the guard.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap


def test_platform_guard_exits_on_non_windows():
    script = textwrap.dedent(
        """
        import sys
        import types

        # Same lightweight stubs as conftest.py, but this time we do NOT
        # spoof sys.platform to win32 - we want the module's own guard to
        # fire, so we force it to a non-Windows value instead (even on a
        # real Windows machine, sys.platform would otherwise genuinely be
        # "win32" already).
        sys.platform = "linux"

        winreg_stub = types.ModuleType("winreg")
        winreg_stub.HKEY_CURRENT_USER = 1
        winreg_stub.HKEY_LOCAL_MACHINE = 2
        sys.modules["winreg"] = winreg_stub

        magic_stub = types.ModuleType("magic")
        magic_stub.Magic = lambda mime=True: None
        sys.modules["magic"] = magic_stub

        from pynball import pynball  # should print a message and sys.exit(1)
        """
    )
    import os

    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(sys.path)
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        env=env,
    )
    assert result.returncode == 1
    assert "not supported" in result.stdout

