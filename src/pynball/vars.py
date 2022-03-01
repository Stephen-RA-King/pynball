# Core Library modules
import ast
import os
import subprocess
import sys
import winreg
from pathlib import Path


class VarControl:
    def __init__(self):
        self.env_variables = os.environ
        self.environment = os.name
        self.user_key = winreg.HKEY_CURRENT_USER
        self.user_subkey = "Environment"
        self.system_key = winreg.HKEY_LOCAL_MACHINE
        self.system_subkey = (
            r"System\CurrentControlSet\Control\Session Manager\Environment"
        )
        try:
            self.workon_home = Path(os.environ["WORKON_HOME"])
        except KeyError:
            self.workon_home = Path("")
        try:
            self.project_home = Path(os.environ["PROJECT_HOME"])
        except KeyError:
            self.project_home = Path("")
        try:
            self.pynball = os.environ["PYNBALL"]
            self.versions = ast.literal_eval(self.pynball)  # type: ignore
        except KeyError:
            self.versions = {}  # type: ignore

    @staticmethod
    def _execute(*args, supress_exception=False):
        print(args)
        try:
            proc = subprocess.Popen(
                args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            out, err = proc.communicate()
            decoded_out = out.decode("utf-8")
            decoded_err = err.decode("utf-8")
            if err and not supress_exception:
                raise Exception(decoded_err)
            else:
                return decoded_out
        except OSError as e:
            print(e)

    def setenv(self, scope, name, value):
        if scope != "user" and scope != "system":
            print("Scope value must be 'user' or 'system'")
            return
        if scope == "user":
            key = winreg.OpenKey(
                self.user_key, self.user_subkey, 0, winreg.KEY_ALL_ACCESS
            )
        elif scope == "system":
            key = winreg.OpenKey(
                self.system_key, self.system_subkey, 0, winreg.KEY_ALL_ACCESS
            )
        winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)  # noqa
        winreg.CloseKey(key)

    def getenv(self, scope, name):
        """No need to open the key as they are one of the predefined
        HKEY_* constants.
        """
        if scope != "user" and scope != "system":
            print("Scope value must be 'user' or 'system'")
            return
        elif scope == "user":
            key = winreg.CreateKey(self.user_key, self.user_subkey)
        elif scope == "system":
            key = winreg.CreateKey(self.system_key, self.system_subkey)
        try:
            value, _ = winreg.QueryValueEx(key, name)  # noqa
        except FileNotFoundError:
            value = None
        return value

    def deletenv(self, scope, name):
        """No need to open the key as they are one of the predefined
        HKEY_* constants.
        """
        if scope != "user" and scope != "system":
            print("Scope value must be 'user' or 'system'")
            return
        elif scope == "user":
            key = winreg.CreateKey(self.user_key, self.user_subkey)
        elif scope == "system":
            key = winreg.CreateKey(self.system_key, self.system_subkey)
        try:
            winreg.DeleteValue(key, name)  # noqa
        except OSError as e:
            print(f"Deletion of key: '{name}' failed -\n {e}")

    def add_version(self, name, version_path):
        """Adds a friendly name and path of an installation."""

        pass

    def delete_version(self):
        """Deletes a friendly name and path of an installation."""
        pass

    def clear_versions(self):
        """Delete all friendly names and paths"""

    def version(self):
        """Returns details about the current Python version."""
        print("{0.major}.{0.minor}.{0.micro}".format(sys.version_info))
        pass

    def versions(self):
        """Lists the names of the python installs."""
        pass

    def switchto(self):
        """Changes the version of python."""
        pass

    def find(self):
        """Finds installations of python."""
        pass

    def pythonpath(self):
        """Sets environment variable."""
        pass

    def mkproject(self, ver, project_name):
        """Makes a virtual environment from a specific version."""
        if self.workon_home is None or self.project_home is None:
            print(
                """Virtualenv-wrapper is not configured on you system:
            Please install Virtualenv and Virtualenv-wrapper and configure
            'WORKON_HOME' and 'PROJECT_HOME' environment variables"""
            )
            return
        for directory in [self.workon_home, self.project_home]:
            new_path = directory / project_name
            try:
                new_path.mkdir(parents=False, exist_ok=False)
                if directory == self.workon_home:
                    self._execute(
                        "virtualenv",
                        r"-p=D:\PYTHON\python3.8\python.exe",
                        str(new_path),
                    )
                    (new_path / ".project").touch()
                    (new_path / ".project").write_text(
                        f"{self.project_home / project_name}"
                    )
            except FileNotFoundError:
                print(
                    f"Project: '{project_name}' has NOT be created - {directory} "
                    f"does not exist"
                )
                return
            except FileExistsError:
                print(f"""The directory '{new_path}' already exits""")
                return

    def rmproject(self, ver, project_name):
        """Deletes a virtual environment from a specific version."""
        pass

    def export_config_file(self):
        """Creates a configuration file backup"""
        pass

    def import_config_file(self):
        """Creates a configuration file backup"""
        pass


x = VarControl()
"""
x.setenv("system", "STEVE", "123")
x.setenv("user", "STEVE", "456")
print(x.getenv("system", "STEVE"))
print(x.getenv("user", "STEVE"))
x.deletenv("system", "STEVE")
x.deletenv("user", "STEVE")
"""

x.mkproject(3, "steve")
