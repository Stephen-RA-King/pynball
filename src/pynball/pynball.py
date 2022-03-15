"""Utility script to help manage Development with various versions of Python
in conjunction with Virtual Environments and the pyenv module.
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
    """A simple command line tool to help consolidate development with various manual
    installations of Python , pyenv and virtualenvwrapper"""


def _feedback(message: str, feedback_type: str) -> None:
    """A utility method to generate formatted messages

    Args:
        message: Text to be echoed.
        feedback_type: identifies type of message to display.
    """
    if feedback_type not in ["null", "nominal", "warning", "error"]:
        return
    if _idlemode == 1:
        click.echo(message)
    else:
        if feedback_type == "null":
            click.secho(f"{message}", fg="bright_white")
        elif feedback_type == "nominal":
            click.secho(f"{message}", fg="bright_green")
        elif feedback_type == "warning":
            click.secho(f"WARNING: {message}", fg="bright_yellow", bg="black")
        elif feedback_type == "error":
            click.secho(f"ERROR: {message}", fg="bright_red", bg="black")


def _execute(*args, supress_exception=False):
    """A utility method to run command line tools

    Args:
        *args:  The commands typically entered at the command line.
                e.g. "virtualenv", f"-p={version_path}\\python.exe", str(new_path)

    Returns:
        The return value. True for success, False otherwise.
    """
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
    """Check if Virtual Environment Wrapper is configured by checking environment
    variables.

    Returns:
        1:  Indicates virtualenvwrapper is not configured
        0:  Indicates virtualenvwrapper is configured correctly
    """
    if _workon_home == Path("") or _project_home == Path(""):
        message = "Virtualenv-wrapper is not configured."
        _feedback(message, "warning")
        return 1
    return 0


def _check_pyenv():
    """Check if pyenv is configured by checking environment variables.

    Returns:
        1:  Indicates pyenv is not configured
        0:  Indicates pyenv is configured correctly
    """
    if _pyenv_home == Path(""):
        message = """Pyenv is not configured."""
        _feedback(message, "warning")
        return 1
    return 0


def _setenv(scope, name, value):
    """sets an environment variable given a scope, variable name and a value.

    Args:
        scope:  Must be either 'user' or 'system'.
        name:   The registry key name.
        value:  The registry key value.

    Returns:
        error:  message if scope is neither 'user' nor 'system'.
        None:   If registry write is successful.
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
    """Gets an environment variable given a scope and key name.

    Note:
        No need to open the key as they are one of the predefined HKEY_* constants.

    Args:
        scope:  Must be either 'user' or 'system'
        name:   The registry key name

    Returns:
        error:  Message if scope is neither 'user' nor 'system'.
        value:  Registry key value on successful read
        None:   Read failed.

    Raises:
        FileNotFoundError:  When the key is not found
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
    """A utility method to delete an environment variable key from the named scope.

    Note:
        No need to open the key as they are one of the predefined HKEY_* constants.

    Args:
        scope:  Must be either 'user' or 'system'.
        name:   The registry key name.

    Returns:
        error:  Message if scope is neither 'user' nor 'system'.

    Raises:
        OSError:  If the deletion failed.
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
    """Accepts and converts a dictionary object, then writes to the registry.

    Args:
        dict_object:  The dictionary. Format: {"name: str": "path to version": Path,}
    """
    pynball_raw_dict = {name: str(path) for name, path in dict_object.items()}
    pynball = str(pynball_raw_dict)
    _setenv("user", "PYNBALL", pynball)


def _get_pynball(returntype):
    """Reads the environment variable 'PYNBALL' from the user scope as a string.

    The string is then converted to the data structure specified by the
    returntype

    Args:
        returntype: The data structure and values to be returned

    Returns:
        error:  If the returntype is not recognised.
        str:    If returntype is 'string'
        dict:   If return type is 'dict' or 'dict_path_object'
        list:   if return type is 'names' or 'paths'
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
    """Returns Python system Interpreter if set and corresponding Pynball 'name' if set.

    Returns:
        System Interpreter: list, Pynball 'name': list
    """
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
    """Adds a name / path of an installation of Python.

    \b
    Args:
        name:           Friendly name of a python installation. Can be any string.
                        e.g. 3.6
        version_path:   The path to the python interpreter
                        e.g. /PYTHON/python3.6
    """
    sorted_versions = []
    sorted_versions_dict = {}
    pynball_versions = _get_pynball("dict_path_object")
    pynball_dict = _get_pynball("dict")

    path_object = Path(version_path)
    if not (path_object / "python.exe").is_file():
        message = "There is no Python Interpreter on that path"
        _feedback(message, "warning")
        return
    if pynball_versions:
        if version_path in _get_pynball("paths"):
            existing_name = list(pynball_dict.keys())[
                list(pynball_dict.values()).index(version_path)
            ]
            message = f"'{name}' already added to configuration as '{existing_name}'"
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


@cli.command()
@click.argument("name")
def delete(name):
    """Deletes a name / path of an installation of Python.

    \b
    Note:
        This only deletes the name / path in the Pynball configuration.
        It does not delete the Python installation.

    \b
    Args:
        name:   Friendly name of a python installation configured in Pynball.
                e.g. 3.6
    """
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


@cli.command()
def clear():
    """Deletes all names / paths"""
    _delenv("user", "PYNBALL")


@cli.command()
def version():
    """Display details about the system Python Interpreter."""
    message = (
        "{0.major}.{0.minor}.{0.micro}  ReleaseLevel: {0.releaselevel}, "
        "Serial: {0.serial}".format(sys.version_info)
    )
    _feedback(message, "nominal")


@cli.command()
def versions():
    """Lists the names / paths of the configured Python installations"""
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
    """Changes the system Python Interpreter version.

    \b
    Args:
        name:  The Pynball friendly name of the Python Installation
    """
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
@click.option("--use", type=click.Choice(["y", "n"], case_sensitive=False), prompt=True)
@click.pass_context
def pyenv(ctx, use):
    """Automatically include the pyenv versions in Pynball

    \b
    Args:
        use:    The commands typically entered at the command line.
        \f
        ctx:    The click context - Implementation detail that enables this command
                to call another click command.
    """
    if _check_pyenv() == 1:
        return
    vers = _pyenv_home / "versions"
    dirs = {e.name: e for e in vers.iterdir() if e.is_dir()}
    if use.lower() == "y":
        for ver in dirs:
            ctx.invoke(add, name=str(ver), version_path=str(dirs[ver]))
    elif use.lower() == "n":
        for ver in dirs:
            ctx.invoke(delete, name=str(ver))
    else:
        return


@cli.command()
@click.argument("name")
@click.argument("project_name")
def mkproject(name: str, project_name):
    """Creates a Virtual Environment from a specific Python version.

    \b
    Args:
        name:           The Pynball friendly version name.
        project_name:   The project name only. Not the path.
    """
    if _workon_home is None or _project_home is None:
        message = """Virtualenv-wrapper is not configured on you system:
        Please install Virtualenv and Virtualenv-wrapper and configure
        'WORKON_HOME' and 'PROJECT_HOME' environment variables"""
        _feedback(message, "warning")
        return
    ver = str(name)
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
@click.option("--noall", "delete_all", flag_value="n", default=True)
@click.option("-a", "--all", "delete_all", flag_value="y")
@click.argument("project_name")
def rmproject(delete_all, project_name):
    """Deletes a Virtual Environment.

    \b
    Options:
        -a, --all:      Delete both the 'DEV' and 'VENV' directories

    \b
    Args:
        project_name:   The project name to be deleted.  This is not the path.
        \f
        delete_all:     Determines whether the 'dev' directory gets deleted.
    """
    if _workon_home is None or _project_home is None:
        message = """Virtualenv-wrapper is not configured on your system:
                    Please install Virtualenv and Virtualenv-wrapper and configure
                    'WORKON_HOME' and 'PROJECT_HOME' environment variables"""
        _feedback(message, "warning")
        return
    for directory in [_workon_home, _project_home]:
        del_path = directory / project_name
        if directory == _project_home and delete_all != "y":
            continue
        try:
            shutil.rmtree(del_path)
        except FileNotFoundError:
            message = f"Project: '{del_path}' does not exist"
            _feedback(message, "warning")


@cli.command()
def lsproject():
    """Displays all Virtual Environment projects"""
    if _check_virtual_env() == 1:
        return
    dirs = [e.name for e in _workon_home.iterdir() if e.is_dir()]
    for virt in dirs:
        print(virt)


@cli.command()
def exportconf():
    """Creates a configuration file backup

    \f
    Returns:
        The return value. True for success, False otherwise.
    """
    config["PYNBALL"] = {}
    config["PYNBALL"]["PYNBALL"] = _get_pynball("string")
    with open("pynball.ini", "w") as configfile:
        config.write(configfile)


@cli.command()
@click.argument("config_path", type=click.Path())
def importconf(config_path: str):
    """Creates a configuration from a file backup

    Args:
        config_path:  The commands typically entered at the command line.

    \f
    Returns:
        The return value. True for success, False otherwise.
    """
    config_path_object = Path(config_path)
    file_name = config_path_object.name
    config.read(config_path)
    try:
        pynball: str = config["PYNBALL"]["PYNBALL"]
    except KeyError:
        message = f"There is a problem with file: {file_name}"
        _feedback(message, "warning")
        return
    _setenv("user", "PYNBALL", pynball)
