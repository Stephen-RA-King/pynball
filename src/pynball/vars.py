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
            self.pynball_versions = ast.literal_eval(self.pynball)  # type: ignore
        except KeyError:
            self.pynball_versions = {}  # type: ignore

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
        """A Windows utility method to delete an environment variable key from the
        named scope. There is No need to open the key as they are one of the
        predefined HKEY_* constants.
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

    def get_pynball(self):
        """Reads the environment variable 'PYNBALL' from the user scope as a string.
        The string is then converted to a dictionary and then the path components are
        converted to pathlib.Path objects
        The dictionary should be the following format:
        {"name: str": "path to version": Path,}.
        """
        try:
            pynball = self.getenv("user", "PYNBALL")
            print(pynball)
            pynball_raw_dict = ast.literal_eval(pynball)
            print(pynball_raw_dict)
            pynball_versions = {
                name: Path(path) for name, path in pynball_raw_dict.items()
            }
        except (KeyError, ValueError):
            pynball_versions = {}
        print(pynball_versions)
        return pynball_versions

    def set_pynball(self, dict_object):
        """Accepts a dictionary object, converts it to a string and then
        writes the string to the 'PYNBALL' environment variable in the user scope.
        The dictionary should be the following format:
        {"name: str": "path to version": Path,}.
        """
        pynball_raw_dict = {name: str(path) for name, path in dict_object.items()}
        pynball = str(pynball_raw_dict)
        self.setenv("user", "PYNBALL", pynball)

    def add_version(self, name, version_path):
        """Adds a friendly name and path of an installation."""
        pynball_versions = self.get_pynball()
        pynball_versions[f"{str(name)}"] = Path(version_path)
        self.set_pynball(pynball_versions)

    def delete_version(self, name):
        """Deletes a friendly name and path of an installation."""
        pynball_versions = self.get_pynball()
        print(pynball_versions)
        pynball_versions.pop(str(name), None)
        print(pynball_versions)
        self.set_pynball(pynball_versions)

    def clear_versions(self):
        """Delete all friendly names and paths"""
        self.deletenv("user", "PYNBALL")

    def version(self):
        """Returns details about the current Python version."""
        print(
            "{0.major}.{0.minor}.{0.micro}  ReleaseLevel: "
            "{0.releaselevel}, Serial: {0.serial}".format(sys.version_info)
        )

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

x.add_version("3.8", r"D:\PYTHON\python3.8")
