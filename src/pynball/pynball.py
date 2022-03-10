"""Utility script to help manage Development with different versions of Python
in conjunction with Virtual Environments and pyenv
"""
# Core Library modules
import ast
import configparser
import os
import shutil
import subprocess
import sys
import winreg
from pathlib import Path

# Third party modules
import colorama

config = configparser.ConfigParser()


class Pynball:
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
        try:
            self.pynball_pyenv = os.environ["PYNBALL_PYENV"]
        except KeyError:
            self.pynball_pyenv = "0"
        try:
            self.pyenv_home = Path(os.environ["PYENV_HOME"])
        except KeyError:
            self.pyenv_home = Path("")

    @staticmethod
    def _feedback(message, feedback_type):
        """A utility method to generate nicely formatted messages"""
        if feedback_type == "null":
            print(colorama.Fore.WHITE + f"{message}" + colorama.Style.RESET_ALL)
        elif feedback_type == "nominal":
            print(colorama.Fore.GREEN + f"{message}" + colorama.Style.RESET_ALL)
        elif feedback_type == "warning":
            print(
                colorama.Fore.LIGHTYELLOW_EX
                + colorama.Back.BLACK
                + f"WARNING: {message}"
                + colorama.Style.RESET_ALL
            )
        elif feedback_type == "error":
            print(
                colorama.Fore.RED
                + colorama.Back.BLACK
                + f"ERROR: {message}"
                + colorama.Style.RESET_ALL
            )
        else:
            return "Incorrect feedback type"

    def help(self):
        """Return a short description about each public method"""
        message = """
        include_pyenv:      automatically include the versions installed by pyenv
        add-version:        Adds a Python version to the configuration
        delete-version:     Deletes a Python version from the configuration
        clear-versions:     Clears all versions
        version:            Displays information about current system Python version
        versions:           Displays a list of all configured Python versions
        switchto:           Change the system version of Python
        mkproject:          Creates a virtual environment from a specific Python version
        rmproject:          Deletes a virtual environment
        lsproject:          Lists all virtual environments
        import-config:      Create configuration from a file
        export-config:      Saves configuration to a file
        """
        self._feedback(message, "null")

    @staticmethod
    def _execute(*args, supress_exception=False):
        """A utility method to run command line tools"""
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

    def _check_virtual_env(self):
        if self.workon_home == Path("") or self.project_home == Path(""):
            message = "Virtualenv-wrapper is not configured."
            self._feedback(message, "warning")
            return 1
        return 0

    def _check_pyenv(self):
        if self.pyenv_home == Path(""):
            message = """Pyenv is not configured on you system"""
            self._feedback(message, "warning")
            return 1
        return 0

    def _setenv(self, scope, name, value):
        """Utility method to set an environment variable given a scope,
        variable name and a value.
        """
        if scope != "user" and scope != "system":
            message = "Scope value must be 'user' or 'system'"
            self._feedback(message, "warning")
            return message
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

    def _getenv(self, scope, name):
        """Utility method to set an environment variable given a scope,
        variable name and a value.
        No need to open the key as they are one of the predefined HKEY_* constants.
        """
        if scope != "user" and scope != "system":
            message = "Scope value must be 'user' or 'system'"
            self._feedback(message, "warning")
            return message
        elif scope == "user":
            key = winreg.CreateKey(self.user_key, self.user_subkey)
        elif scope == "system":
            key = winreg.CreateKey(self.system_key, self.system_subkey)
        try:
            value, _ = winreg.QueryValueEx(key, name)  # noqa
        except FileNotFoundError:
            value = None
        return value

    def _delenv(self, scope, name):
        """A utility method to delete an environment variable key from the
        named scope.
        No need to open the key as they are one of the predefined HKEY_* constants.
        """
        if scope != "user" and scope != "system":
            message = "Scope value must be 'user' or 'system'"
            self._feedback(message, "warning")
            return message
        elif scope == "user":
            key = winreg.CreateKey(self.user_key, self.user_subkey)
        elif scope == "system":
            key = winreg.CreateKey(self.system_key, self.system_subkey)
        try:
            winreg.DeleteValue(key, name)  # noqa
        except OSError as e:
            message = f"Deletion of key: '{name}' failed -\n {e}"
            self._feedback(message, "warning")

    def _set_pynball(self, dict_object: dict) -> None:
        """Accepts a dictionary object, converts it to a string and then
        writes the string to the 'PYNBALL' environment variable in the user scope.
        The dictionary should be the following format:
        {"name: str": "path to version": Path,}.
        """
        pynball_raw_dict = {name: str(path) for name, path in dict_object.items()}
        pynball = str(pynball_raw_dict)
        self._setenv("user", "PYNBALL", pynball)

    def _get_pynball(self, returntype):
        """Reads the environment variable 'PYNBALL' from the user scope as a string.
        The string is then converted to the data structure specified by the
        returntype
        """
        names_list = []
        paths_list = []
        returntypes = ("string", "dict", "dict_path_object", "names", "paths")
        if returntype not in returntypes:
            message = f"Please use a correct returntype - {returntypes}"
            self._feedback(message, "warning")
            return
        pynball_var = self._getenv("user", "PYNBALL")
        if pynball_var is None:
            return None
        if returntype == "string":
            return pynball_var
        elif returntype == "dict":
            pynball_raw_dict = ast.literal_eval(pynball_var)
            return pynball_raw_dict
        elif returntype == "dict_path_object":
            pynball_raw_dict = ast.literal_eval(pynball_var)
            pynball_versions = {
                name: Path(path) for name, path in pynball_raw_dict.items()
            }
            return pynball_versions
        elif returntype == "names":
            pynball_raw_dict = ast.literal_eval(pynball_var)
            for name in pynball_raw_dict:
                names_list.append(name)
            return names_list
        else:
            pynball_raw_dict = ast.literal_eval(pynball_var)
            for name in pynball_raw_dict:
                paths_list.append(pynball_raw_dict[name])
            return paths_list

    def _get_system_path(self):
        python_system_paths = []
        pynball_system_names = []
        pynball_versions = self._get_pynball("dict")
        system_path_string: str = self._getenv("system", "PATH")
        system_path_variables = system_path_string.split(";")
        for path in system_path_variables:
            pathobject = Path(path)
            if (pathobject / "python.exe").is_file() and os.path.getsize(
                pathobject / "python.exe"
            ) > 0:
                python_system_paths.append(path)
        if pynball_versions:
            for name, _ in pynball_versions.items():
                pynball_path = "".join([pynball_versions[name], "\\"])
                if pynball_path in python_system_paths:
                    pynball_system_names.append(name)
        return python_system_paths, pynball_system_names

    def add_version(self, name, version_path):
        """Adds a friendly name and path of an installation."""
        sorted_versions = []
        sorted_versions_dict = {}
        pynball_versions = self._get_pynball("dict_path_object")
        pynball_dict = self._get_pynball("dict")

        path_object = Path(version_path)
        if not (path_object / "python.exe").is_file():
            message = f"There is no python executable on path: {version_path}"
            self._feedback(message, "warning")
            return
        if pynball_versions:
            if version_path in self._get_pynball("paths"):
                existing_name = list(pynball_dict.keys())[
                    list(pynball_dict.values()).index(version_path)
                ]
                message = f"{name:8} already added to configuration as {existing_name}"
                self._feedback(message, "warning")
                return
            for version in pynball_versions:
                sorted_versions.append(version)
            sorted_versions.append(str(name))
            sorted_versions.sort(
                reverse=True, key=lambda s: list(map(int, s.split(".")))
            )
            for version in sorted_versions:
                if version == str(name):
                    sorted_versions_dict[version] = path_object
                else:
                    sorted_versions_dict[version] = pynball_versions[version]
        else:
            sorted_versions_dict[name] = path_object
        self._set_pynball(sorted_versions_dict)

    def delete_version(self, name):
        """Deletes a friendly name and path of an installation."""
        pynball_versions = self._get_pynball("dict")
        pynball_versions.pop(str(name), None)
        self._set_pynball(pynball_versions)

    def clear_versions(self):
        """Delete all friendly names and paths"""
        self._delenv("user", "PYNBALL")

    def version(self):
        """Returns details about the current Python version."""
        message = (
            "{0.major}.{0.minor}.{0.micro}  ReleaseLevel: {0.releaselevel}, "
            "Serial: {0.serial}".format(sys.version_info)
        )
        self._feedback(message, "nominal")

    def versions(self):
        """Lists the names of the python installs."""
        system_paths, pynball_names = self._get_system_path()
        pynball_versions = self._get_pynball("dict")
        if not system_paths:
            message = "System Interpreter is not configured"
            self._feedback(message, "warning")
        if not pynball_names and system_paths:
            for path in system_paths:
                message = f"{path} : --> System Interpreter"
                self._feedback(message, "nominal")
        if pynball_versions is None:
            message = "Pynball configuration is empty - use 'add' command"
            self._feedback(message, "warning")
        else:
            for ver in pynball_versions:
                if ver in pynball_names:
                    message = (
                        f"{ver:10}{pynball_versions[ver]} : --> System Interpreter"
                    )
                    self._feedback(message, "nominal")
                else:
                    print(f"{ver:10}{pynball_versions[ver]}")
        if pynball_versions and system_paths and not pynball_names:
            message = "System Interpreter is not in Pynball Configuration"
            self._feedback(message, "warning")

    def switchto(self, name):
        """Changes the system version of python."""
        name = str(name)
        path_new = ""
        pynball_versions = self._get_pynball("dict")
        system_paths, pynball_names = self._get_system_path()
        all_paths: str = self._getenv("system", "PATH")
        if name not in self._get_pynball("names"):
            message = f"{name} is not in Pynballs' configuration"
            self._feedback(message, "warning")
            self.versions()
            return
        if len(system_paths) > 1 or len(pynball_names) > 1:
            message = (
                "Multiple system interpreters have been detected - "
                "There should be only one"
            )
            self._feedback(message, "error")
            self.versions()
            return
        if name in pynball_names:
            message = f"{name} is already configured as the system interpreter"
            self._feedback(message, "warning")
            self.versions()
            return
        pynball_path = "".join([pynball_versions[name], "\\"])
        if system_paths:
            for old_version in system_paths:
                path_new: str = all_paths.replace(old_version, pynball_path)
            self._setenv("system", "PATH", path_new)
        if not system_paths:
            path_patch = "".join(
                [pynball_path, "\\" ";", pynball_path, "\\", "Scripts", "\\", ";"]
            )
            path_new = "".join([path_patch, all_paths])
            self._setenv("system", "PATH", path_new)

    def include_pyenv(self, flag: str):
        if self._check_pyenv() == 1:
            return
        versions = self.pyenv_home / "versions"
        dirs = {e.name: e for e in versions.iterdir() if e.is_dir()}
        if flag.lower() == "y":
            self._setenv("user", "PYNBALL_PYENV", "1")
            self.pynball_pyenv = 1
            for ver in dirs:
                self.add_version(str(ver), str(dirs[ver]))
        elif flag.lower() == "n":
            self._setenv("user", "PYNBALL_PYENV", "0")
            self.pynball_pyenv = 0
            for ver in dirs:
                self.delete_version(str(ver))
        else:
            return

    def mkproject(self, ver: str, project_name):
        """Creates a virtual environment from a specific version."""
        if self.workon_home is None or self.project_home is None:
            message = """Virtualenv-wrapper is not configured on you system:
            Please install Virtualenv and Virtualenv-wrapper and configure
            'WORKON_HOME' and 'PROJECT_HOME' environment variables"""
            self._feedback(message, "warning")
            return
        ver = str(ver)
        version_path = ""
        pynball_versions = self._get_pynball("dict")
        for name in pynball_versions:
            if name == ver:
                version_path = pynball_versions[name]
                break
        if version_path == "":
            message = f"{ver} is not configured in Pynball - Use the 'add' command"
            self._feedback(message, "warning")
            return
        for directory in [self.workon_home, self.project_home]:
            new_path = directory / project_name
            try:
                new_path.mkdir(parents=False, exist_ok=False)
                if directory == self.workon_home:
                    self._execute(
                        "virtualenv",
                        f"-p={version_path}\\python.exe",
                        str(new_path),
                    )
                    (new_path / ".project").touch()
                    (new_path / ".project").write_text(
                        f"{self.project_home / project_name}"
                    )
            except FileNotFoundError:
                message = (
                    f"Project: '{project_name}' has NOT be created - "
                    f"{directory} does not exist"
                )
                self._feedback(message, "warning")
                return
            except FileExistsError:
                message = f"The directory '{new_path}' already exits"
                self._feedback(message, "warning")
                return

    def rmproject(self, project_name):
        """Deletes a virtual environment."""
        if self.workon_home is None or self.project_home is None:
            message = """Virtualenv-wrapper is not configured on you system:
                        Please install Virtualenv and Virtualenv-wrapper and configure
                        'WORKON_HOME' and 'PROJECT_HOME' environment variables"""
            self._feedback(message, "warning")
            return
        for directory in [self.workon_home, self.project_home]:
            del_path = directory / project_name
            if directory == self.project_home:
                x = input("Do you want to delete the Project directory? (y/n)")
                if x.lower() != "y":
                    continue
            try:
                shutil.rmtree(del_path)
            except FileNotFoundError:
                message = f"Project: {project_name} does not exist"
                self._feedback(message, "warning")

    def lsproject(self):
        """Lists all projects"""
        if self._check_virtual_env() == 1:
            return
        dirs = [e.name for e in self.workon_home.iterdir() if e.is_dir()]
        for virt in dirs:
            print(virt)

    def export_config(self):
        """Creates a configuration file backup"""
        config["PYNBALL"] = {}
        config["PYNBALL"]["PYNBALL"] = self._get_pynball("string")
        config["PYNBALL"]["PYNBALL_PYENV"] = self.pynball_pyenv
        with open("pynball.ini", "w") as configfile:
            config.write(configfile)

    def import_config(self, config_path: str):
        """Creates a configuration file backup"""
        config_path_object = Path(config_path)
        file_name = config_path_object.name
        config.read(config_path)
        try:
            pynball: str = config["PYNBALL"]["PYNBALL"]
            pynball_pyenv: str = config["PYNBALL"]["PYNBALL_PYENV"]
        except KeyError:
            message = f"There is a problem with file: {file_name}"
            self._feedback(message, "warning")
            return
        self._setenv("user", "PYNBALL", pynball)
        self._setenv("user", "PYNBALL_PYENV", pynball_pyenv)


# z = Pynball()
# z.add_version("3.5", "C:\\Users\\conta\\.pyenv\\pyenv-win\\versions\\3.5.2")
# z.add_version("3.6", "D:\\PYTHON\\python3.6\\")
# print(z.get_system_path())
# z.switchto("3.9")
# z.rmproject("")
# z.mkproject("3.5", "deletethis")
# z.include_pyenv("n")
# z.include_pyenv("y")
# z.versions()
# z.help()
# z.lsproject()
# z.rmproject("deletethis")
# z.export_config()
# z.import_config("pynball.ini")
# print(z._get_pynball("dict"))
# print(z._get_pynball("dict_path_object"))
