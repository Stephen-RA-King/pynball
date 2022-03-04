# Core Library modules
import ast
import os
import subprocess
import sys
import winreg
from pathlib import Path

# Third party modules
import colorama


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
    def feedback(message, feedback_type):
        if feedback_type == "nominal":
            print(colorama.Fore.GREEN + f"{message}" + colorama.Style.RESET_ALL)
        if feedback_type == "warning":
            print(
                colorama.Fore.LIGHTYELLOW_EX
                + colorama.Back.BLACK
                + f"WARNING: {message}"
                + colorama.Style.RESET_ALL
            )
        if feedback_type == "error":
            print(
                colorama.Fore.RED
                + colorama.Back.BLACK
                + f"ERROR: {message}"
                + colorama.Style.RESET_ALL
            )

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

    def get_pynball(self, returntype):
        """Reads the environment variable 'PYNBALL' from the user scope as a string.
        The string is then converted to a dictionary and then the path components are
        converted to pathlib.Path objects
        The dictionary should be the following format:
        {"name: str": "path to version": Path,}.
        """
        names_list = []
        paths_list = []
        returntypes = ("string", "dict", "dict_path_object", "names", "paths")
        if returntype not in returntypes:
            print("Please use a correct returntype")
        pynball_var = self.getenv("user", "PYNBALL")
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

    def set_pynball(self, dict_object):
        """Accepts a dictionary object, converts it to a string and then
        writes the string to the 'PYNBALL' environment variable in the user scope.
        The dictionary should be the following format:
        {"name: str": "path to version": Path,}.
        """
        pynball_raw_dict = {name: str(path) for name, path in dict_object.items()}
        pynball = str(pynball_raw_dict)
        self.setenv("user", "PYNBALL", pynball)

    def get_system_path(self):
        python_system_paths = []
        pynball_system_names = []
        pynball_versions = self.get_pynball("dict")
        system_path_string: str = self.getenv("system", "PATH")
        system_path_variables = system_path_string.split(";")
        for path in system_path_variables:
            pathobject = Path(path)
            if (pathobject / "python.exe").is_file() and os.path.getsize(
                pathobject / "python.exe"
            ) > 0:
                python_system_paths.append(path)
        if pynball_versions:
            for name, path in pynball_versions.items():
                if path in python_system_paths:
                    pynball_system_names.append(name)
        return python_system_paths, pynball_system_names

    def set_system_path(self, path_list):
        """Takes a list of python path details and writes this to the exiting
        system path variable
        """
        pass

    def add_version(self, name, version_path):
        """Adds a friendly name and path of an installation."""
        sorted_versions = []
        sorted_versions_dict = {}
        pynball_versions = self.get_pynball("dict_path_object")

        path_object = Path(version_path)
        if not (path_object / "python.exe").is_file():
            message = f"There is no python executable on path: {version_path}"
            self.feedback(message, "warning")
            return
        if pynball_versions:
            if version_path in self.get_pynball("paths"):
                message = "Python version already added to configuration"
                self.feedback(message, "warning")
                return
            for version in pynball_versions:
                sorted_versions.append(version)
            sorted_versions.append(str(name))
            sorted_versions.sort(key=lambda x: float(x))
            for version in sorted_versions:
                if version == str(name):
                    sorted_versions_dict[version] = path_object
                else:
                    sorted_versions_dict[version] = pynball_versions[version]
        else:
            sorted_versions_dict[name] = path_object
        self.set_pynball(sorted_versions_dict)

    def delete_version(self, name):
        """Deletes a friendly name and path of an installation."""
        pynball_versions = self.get_pynball("dict")
        pynball_versions.pop(str(name), None)
        self.set_pynball(pynball_versions)

    def clear_versions(self):
        """Delete all friendly names and paths"""
        self.deletenv("user", "PYNBALL")

    @staticmethod
    def version():
        """Returns details about the current Python version."""
        print(
            "{0.major}.{0.minor}.{0.micro}  ReleaseLevel: "
            "{0.releaselevel}, Serial: {0.serial}".format(sys.version_info)
        )

    def versions(self):
        """Lists the names of the python installs."""
        system_paths, pynball_names = self.get_system_path()
        pynball_versions = self.get_pynball("dict")
        if not system_paths:
            message = "System Interpreter is not configured"
            self.feedback(message, "warning")
        if not pynball_names and system_paths:
            for path in system_paths:
                message = f"{path} : --> System Interpreter"
                self.feedback(message, "nominal")
        if pynball_versions is None:
            message = "Pynball configuration is empty - use 'add' command"
            self.feedback(message, "warning")
        else:
            for ver in pynball_versions:
                if ver in pynball_names:
                    message = (
                        f"{ver:10}{pynball_versions[ver]} : --> System Interpreter"
                    )
                    self.feedback(message, "nominal")
                else:
                    print(f"{ver:10}{pynball_versions[ver]}")
        if pynball_versions and system_paths and not pynball_names:
            message = "System Interpreter is not in Pynball Configuration"
            self.feedback(message, "warning")

    def switchto(self, name):
        """Changes the system version of python."""
        name = str(name)
        path_new = ""
        pynball_versions = self.get_pynball("dict")
        system_paths, pynball_names = self.get_system_path()
        all_paths: str = self.getenv("system", "PATH")
        if name not in self.get_pynball("names"):
            message = f"{name} is not in Pynballs' configuration"
            self.feedback(message, "warning")
            self.versions()
            return
        if len(system_paths) > 1 or len(pynball_names) > 1:
            message = (
                "Multiple system interpreters have been detected - "
                "There should be only one"
            )
            self.feedback(message, "error")
            self.versions()
            return
        if name in pynball_names:
            message = f"{name} is already configured as the system interpreter"
            self.feedback(message, "warning")
            self.versions()
            return
        pynball_path = pynball_versions[name]
        if system_paths:
            for old_version in system_paths:
                path_new: str = all_paths.replace(old_version, pynball_path)
            print(path_new)
        if not system_paths:
            # add pynball name - path to position 1
            path_patch = "".join(
                [pynball_path, "/" ";", pynball_path, "/", "scripts", "/", ";"]
            )
            path_new = "".join([path_patch, all_paths])
            print(path_new)

    def pythonpath(self):
        """Sets environment variable."""
        pass

    def mkproject(self, ver: str, project_name):
        """Makes a virtual environment from a specific version."""
        if self.workon_home is None or self.project_home is None:
            print(
                """Virtualenv-wrapper is not configured on you system:
            Please install Virtualenv and Virtualenv-wrapper and configure
            'WORKON_HOME' and 'PROJECT_HOME' environment variables"""
            )
            return
        ver = str(ver)
        version_path = ""
        pynball_versions = self.get_pynball("dict")
        for name in pynball_versions:
            if name == ver:
                version_path = pynball_versions[name]
                break
        if version_path == "":
            message = f"{ver} is not configured in Pynball - Use the 'add' command"
            self.feedback(message, "warning")
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


z = VarControl()
# z.add_version("3.6", "D:\\PYTHON\\python3.6")
# print(z.get_system_path())
z.switchto("3.10")
