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
import click

config = configparser.ConfigParser()


_idlemode = 1 if "idlelib.run" in sys.modules else 0
_env_variables = os.environ
_environment = os.name
_user_key = winreg.HKEY_CURRENT_USER
_user_subkey = "Environment"
_system_key = winreg.HKEY_LOCAL_MACHINE
_system_subkey = r"System\CurrentControlSet\Control\Session Manager\Environment"
try:
    _workon_home = Path(os.environ["WORKON_HOME"])
except KeyError:
    _workon_home = Path("")
try:
    _project_home = Path(os.environ["PROJECT_HOME"])
except KeyError:
    _project_home = Path("")

try:
    _pynball = os.environ["PYNBALL"]
    _pynball_versions = ast.literal_eval(_pynball)  # type: ignore
except KeyError:
    _pynball_versions = {}  # type: ignore
try:
    _pyenv_home = Path(os.environ["PYENV_HOME"])
except KeyError:
    _pyenv_home = Path("")


@click.group()
def cli():
    pass


def _feedback(message, feedback_type):
    """A utility method to generate nicely formatted messages"""
    if _idlemode == 1:
        click.echo(message)
    else:
        if feedback_type == "null":
            click.secho(f"{message}", fg="LIGHTWHITE_EX")
        elif feedback_type == "nominal":
            click.secho(f"{message}", fg="LIGHTGREEN_EX")
        elif feedback_type == "warning":
            click.secho(f"WARNING: {message}", fg="LIGHTYELLOW_EX", bg="BLACK")
        elif feedback_type == "error":
            click.secho(f"ERROR: {message}", fg="LIGHTRED_EX", bg="BLACK")
        else:
            return "Incorrect feedback type"


@cli.command()
def commands():
    """Return a short description about each public method"""
    message = """add:            Add a Python version to the configuration
delete:         Delete a Python version from the configuration
clear:          Clear all Configuration versions
version:        Display current system Python version
versions:       Display a list of all configured Python versions
switchto:       Change the system version of Python
mkproject:      Create a virtual environment from a Python version
rmproject:      Delete a virtual environment
lsproject:      List all virtual environments
pyenv:          Automatically include the pyenv versions
importconf:     Create configuration from a file
exportconf:     Save configuration to a file"""
    _feedback(message, "null")


def _execute(*args, supress_exception=False):
    """A utility method to run command line tools"""
    try:
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        decoded_out = out.decode("utf-8")
        decoded_err = err.decode("utf-8")
        if err and not supress_exception:
            raise Exception(decoded_err)
        else:
            return decoded_out
    except OSError as e:
        print(e)


def _check_virtual_env():
    if _workon_home == Path("") or _project_home == Path(""):
        message = "Virtualenv-wrapper is not configured."
        _feedback(message, "warning")
        return 1
    return 0


def _check_pyenv():
    if _pyenv_home == Path(""):
        message = """Pyenv is not configured."""
        _feedback(message, "warning")
        return 1
    return 0


def _setenv(scope, name, value):
    """Utility method to set an environment variable given a scope,
    variable name and a value.
    """
    if scope != "user" and scope != "system":
        message = "Scope value must be 'user' or 'system'"
        _feedback(message, "warning")
        return message
    if scope == "user":
        key = winreg.OpenKey(_user_key, _user_subkey, 0, winreg.KEY_ALL_ACCESS)
    elif scope == "system":
        key = winreg.OpenKey(_system_key, _system_subkey, 0, winreg.KEY_ALL_ACCESS)
    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)  # noqa
    winreg.CloseKey(key)


def _getenv(scope, name):
    """Utility method to set an environment variable given a scope,
    variable name and a value.
    No need to open the key as they are one of the predefined HKEY_* constants.
    """
    if scope != "user" and scope != "system":
        message = "Scope value must be 'user' or 'system'"
        _feedback(message, "warning")
        return message
    elif scope == "user":
        key = winreg.CreateKey(_user_key, _user_subkey)
    elif scope == "system":
        key = winreg.CreateKey(_system_key, _system_subkey)
    try:
        value, _ = winreg.QueryValueEx(key, name)  # noqa
    except FileNotFoundError:
        value = None
    return value


def _delenv(scope, name):
    """A utility method to delete an environment variable key from the
    named scope.
    No need to open the key as they are one of the predefined HKEY_* constants.
    """
    if scope != "user" and scope != "system":
        message = "Scope value must be 'user' or 'system'"
        _feedback(message, "warning")
        return message
    elif scope == "user":
        key = winreg.CreateKey(_user_key, _user_subkey)
    elif scope == "system":
        key = winreg.CreateKey(_system_key, _system_subkey)
    try:
        winreg.DeleteValue(key, name)  # noqa
    except OSError as e:
        message = f"Deletion of key: '{name}' failed -\n {e}"
        _feedback(message, "warning")


def _set_pynball(dict_object: dict) -> None:
    """Accepts a dictionary object, converts it to a string and then
    writes the string to the 'PYNBALL' environment variable in the user scope.
    The dictionary should be the following format:
    {"name: str": "path to version": Path,}.
    """
    pynball_raw_dict = {name: str(path) for name, path in dict_object.items()}
    pynball = str(pynball_raw_dict)
    _setenv("user", "PYNBALL", pynball)


def _get_pynball(returntype):
    """Reads the environment variable 'PYNBALL' from the user scope as a string.
    The string is then converted to the data structure specified by the
    returntype
    """
    names_list = []
    paths_list = []
    returntypes = ("string", "dict", "dict_path_object", "names", "paths")
    if returntype not in returntypes:
        message = f"Please use a correct returntype - {returntypes}"
        _feedback(message, "warning")
        return
    pynball_var = _getenv("user", "PYNBALL")
    if pynball_var is None:
        return None
    if returntype == "string":
        return pynball_var
    elif returntype == "dict":
        pynball_raw_dict = ast.literal_eval(pynball_var)
        return pynball_raw_dict
    elif returntype == "dict_path_object":
        pynball_raw_dict = ast.literal_eval(pynball_var)
        pynball_versions = {name: Path(path) for name, path in pynball_raw_dict.items()}
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


def _get_system_path():
    python_system_paths = []
    pynball_system_names = []
    pynball_versions = _get_pynball("dict")
    system_path_string: str = _getenv("system", "PATH")
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


@cli.command()
@click.argument("name")
@click.argument("version_path", type=click.Path())
def add(name, version_path):
    """Adds a friendly name and path of an installation."""
    sorted_versions = []
    sorted_versions_dict = {}
    pynball_versions = _get_pynball("dict_path_object")
    pynball_dict = _get_pynball("dict")

    path_object = Path(version_path)
    if not (path_object / "python.exe").is_file():
        message = "There is no python executable on that path"
        _feedback(message, "warning")
        return
    if pynball_versions:
        if version_path in _get_pynball("paths"):
            existing_name = list(pynball_dict.keys())[
                list(pynball_dict.values()).index(version_path)
            ]
            message = f"{name:8} already added to configuration as {existing_name}"
            _feedback(message, "warning")
            return
        for ver in pynball_versions:
            sorted_versions.append(ver)
        sorted_versions.append(str(name))
        sorted_versions.sort(reverse=True, key=lambda s: list(map(int, s.split("."))))
        for ver in sorted_versions:
            if ver == str(name):
                sorted_versions_dict[ver] = path_object
            else:
                sorted_versions_dict[ver] = pynball_versions[ver]
    else:
        sorted_versions_dict[name] = path_object
    _set_pynball(sorted_versions_dict)
    versions()


@cli.command()
@click.argument("name")
def delete(name):
    """Deletes a friendly name and path of an installation."""
    pynball_versions = _get_pynball("dict")
    _, sys_ver = _get_system_path()
    if name in sys_ver:
        message = "Cannot delete System Interpreter"
        _feedback(message, "warning")
        versions()
        return
    else:
        pynball_versions.pop(str(name), None)
        _set_pynball(pynball_versions)
        versions()


@cli.command()
def clear():
    """Delete all friendly names and paths"""
    _delenv("user", "PYNBALL")


@cli.command()
def version():
    """Returns details about the system Python version."""
    message = (
        "{0.major}.{0.minor}.{0.micro}  ReleaseLevel: {0.releaselevel}, "
        "Serial: {0.serial}".format(sys.version_info)
    )
    _feedback(message, "nominal")


@cli.command()
def versions():
    """Lists the names of the python installs."""
    system_paths, pynball_names = _get_system_path()
    pynball_versions = _get_pynball("dict")
    if not system_paths:
        message = "System Interpreter is not configured"
        _feedback(message, "warning")
    if not pynball_names and system_paths:
        for path in system_paths:
            message = f"{path} : --> System Interpreter"
            _feedback(message, "nominal")
    if pynball_versions is None:
        message = "Pynball configuration is empty - use 'add' command"
        _feedback(message, "warning")
    else:
        for ver in pynball_versions:
            if ver in pynball_names:
                message = f"{ver:10}{pynball_versions[ver]} : --> System Interpreter"
                _feedback(message, "nominal")
            else:
                print(f"{ver:10}{pynball_versions[ver]}")
    if pynball_versions and system_paths and not pynball_names:
        message = "System Interpreter is not in Pynball Configuration"
        _feedback(message, "warning")


@cli.command()
@click.argument("name")
def switchto(name):
    """Changes the system version of python."""
    name = str(name)
    path_new = ""
    pynball_versions = _get_pynball("dict")
    system_paths, pynball_names = _get_system_path()
    all_paths: str = _getenv("system", "PATH")
    if name not in _get_pynball("names"):
        message = f"{name} is not in Pynballs' configuration"
        _feedback(message, "warning")
        versions()
        return
    if len(system_paths) > 1 or len(pynball_names) > 1:
        message = (
            "Multiple system interpreters have been detected - "
            "There should be only one"
        )
        _feedback(message, "error")
        versions()
        return
    if name in pynball_names:
        message = f"{name} is already configured as the system interpreter"
        _feedback(message, "warning")
        versions()
        return
    pynball_path = "".join([pynball_versions[name], "\\"])
    if system_paths:
        for old_version in system_paths:
            path_new: str = all_paths.replace(old_version, pynball_path)
        _setenv("system", "PATH", path_new)
    if not system_paths:
        path_patch = "".join(
            [pynball_path, "\\" ";", pynball_path, "\\", "Scripts", "\\", ";"]
        )
        path_new = "".join([path_patch, all_paths])
        _setenv("system", "PATH", path_new)


@cli.command()
@click.argument("flag")
def pyenv(flag: str):
    if _check_pyenv() == 1:
        return
    vers = _pyenv_home / "versions"
    dirs = {e.name: e for e in vers.iterdir() if e.is_dir()}
    if flag.lower() == "y":
        _setenv("user", "PYNBALL_PYENV", "1")
        for ver in dirs:
            add(str(ver), str(dirs[ver]))
    elif flag.lower() == "n":
        _setenv("user", "PYNBALL_PYENV", "0")
        for ver in dirs:
            delete(str(ver))
    else:
        return


@cli.command()
@click.argument("name")
@click.argument("project_name")
def mkproject(ver: str, project_name):
    """Creates a virtual environment from a specific version."""
    if _workon_home is None or _project_home is None:
        message = """Virtualenv-wrapper is not configured on you system:
        Please install Virtualenv and Virtualenv-wrapper and configure
        'WORKON_HOME' and 'PROJECT_HOME' environment variables"""
        _feedback(message, "warning")
        return
    ver = str(ver)
    version_path = ""
    pynball_versions = _get_pynball("dict")
    for name in pynball_versions:
        if name == ver:
            version_path = pynball_versions[name]
            break
    if version_path == "":
        message = f"{ver} is not configured in Pynball - Use the 'add' command"
        _feedback(message, "warning")
        return
    for directory in [_workon_home, _project_home]:
        new_path = directory / project_name
        try:
            new_path.mkdir(parents=False, exist_ok=False)
            if directory == _workon_home:
                _execute(
                    "virtualenv",
                    f"-p={version_path}\\python.exe",
                    str(new_path),
                )
                (new_path / ".project").touch()
                (new_path / ".project").write_text(f"{_project_home / project_name}")
        except FileNotFoundError:
            message = (
                f"Project: '{project_name}' has NOT be created - "
                f"{directory} does not exist"
            )
            _feedback(message, "warning")
            return
        except FileExistsError:
            message = f"The directory '{new_path}' already exits"
            _feedback(message, "warning")
            return


@cli.command()
@click.argument("project_name")
def rmproject(project_name):
    """Deletes a virtual environment."""
    if _workon_home is None or _project_home is None:
        message = """Virtualenv-wrapper is not configured on you system:
                    Please install Virtualenv and Virtualenv-wrapper and configure
                    'WORKON_HOME' and 'PROJECT_HOME' environment variables"""
        _feedback(message, "warning")
        return
    for directory in [_workon_home, _project_home]:
        del_path = directory / project_name
        if directory == _project_home:
            x = input("Do you want to delete the Project directory? (y/n)")
            if x.lower() != "y":
                continue
        try:
            shutil.rmtree(del_path)
        except FileNotFoundError:
            message = f"Project: {project_name} does not exist"
            _feedback(message, "warning")


@cli.command()
def lsproject():
    """Lists all projects"""
    if _check_virtual_env() == 1:
        return
    dirs = [e.name for e in _workon_home.iterdir() if e.is_dir()]
    for virt in dirs:
        print(virt)


@cli.command()
def exportconf():
    """Creates a configuration file backup"""
    config["PYNBALL"] = {}
    config["PYNBALL"]["PYNBALL"] = _get_pynball("string")
    with open("_pynball.ini", "w") as configfile:
        config.write(configfile)


@cli.command()
@click.argument("config_path", type=click.Path())
def importconf(config_path: str):
    """Creates a configuration file backup"""
    config_path_object = Path(config_path)
    file_name = config_path_object.name
    config.read(config_path)
    try:
        pynball: str = config["PYNBALL"]["PYNBALL"]
        pynball_pyenv: str = config["PYNBALL"]["PYNBALL_PYENV"]
    except KeyError:
        message = f"There is a problem with file: {file_name}"
        _feedback(message, "warning")
        return
    _setenv("user", "PYNBALL", pynball)
    _setenv("user", "PYNBALL_PYENV", pynball_pyenv)
