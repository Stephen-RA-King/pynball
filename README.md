# Pynball

> Centralized management and utilization of all your Python Installations.

[![pre-commit][pre-commit-image]][pre-commit-url]
[![Imports: isort][isort-image]][isort-url]
[![Code style: black][black-image]][black-url]
[![Checked with mypy][mypy-image]][mypy-url]
[![security: bandit][bandit-image]][bandit-url]
[![licence: mit][mit-license-image]][mit-license-url]

![](https://github.com/Stephen-RA-King/pynball/raw/main/header.png)

You may have a requirement for development on various versions of Python.
Or you may have a mixture of installations including pyenv, custom installations,
system installations etc. Pynball can make leveraging such environments a lot easier.

## Features

- Consolidates all Python installations including [**pyenv**][pyenv-url] into one management system
- Easily create Virtual Environments using any Python version.
- Track which virtual environments have which Python versions and tox versions.
- Quickly change the System interpreter

## Pre Installation Requirements

#### Minimum Requirements

1. Python 3.7, 3.8, 3.9 or 3.10
2. [**pipx**][pipx-url]

#### For Maximum Benefits additionally install the following:

3. [**Virtualenv**][virtualenv-url] (which has benefits over venv)
4. [**Virtualenvwrapper**][virtualenvwrapper-url]
5. [**pyenv**][pyenv-url]

## Installation

OS X & Linux:

Will be supported in version 2

Windows:

```sh
pipx install pynball
pipx inject pynball click
```

## Usage example

### View Available commands

```sh
pynball
Usage: pynball [OPTIONS] COMMAND [ARGS]...

  Utility script to help manage development with various versions of Python in
  conjunction with Virtual Environments and optionally the pyenv module

Options:
  --help  Show this message and exit.

Commands:
  add         Adds a name / path of an installation of Python.
  addall      Add all versions to the Pynball configuration.
  delete      Deletes a name / path of an installation of Python.
  exportconf  Creates a configuration file backup.
  importconf  Creates a configuration from a file backup
  lsproject   Displays all Virtual Environment projects
  mkproject   Creates a Virtual Environment from a specific Python version.
  pyenv       Automatically include the pyenv versions in Pynball
  reset       Deletes all names / paths
  rmproject   Deletes a Virtual Environment.
  system      Changes the system Python Interpreter version.
  version     Display details about the system Python Interpreter.
  versions    Lists the names / paths of the configured Python installations
```

### Add a Python version to the config

```sh
pynball versions
D:\PYTHON\3.9.10 : --> System Interpreter
WARNING: Pynball configuration is empty - use 'add' command
```

```sh
pynball add 3.8.10 D:\PYTHON\3.8.10
'3.8.10' Successfully added to configuration
```

```sh
pynball versions
D:\PYTHON\3.9.10 : --> System Interpreter
3.8.10    D:\PYTHON\3.8.10
WARNING: System Interpreter is not in Pynball Configuration
```

### Add all manually installed Python versions to the config

```sh
pynball addall
'3.10.4' Successfully added to configuration
'3.5.4' Successfully added to configuration
'3.6.8' Successfully added to configuration
'3.7.9' Successfully added to configuration
WARNING: '3.8.10' already added to configuration as '3.8.10'
'3.9.10' Successfully added to configuration
```

```sh
pynball versions
3.10.4    D:\PYTHON\3.10.4
3.9.10    D:\PYTHON\3.9.10 : --> System Interpreter
3.8.10    D:\PYTHON\3.8.10
3.7.9     D:\PYTHON\3.7.9
3.6.8     D:\PYTHON\3.6.8
3.5.4     D:\PYTHON\3.5.4
```

### Add pyenv Python versions (if any) to the config

```sh
pynball pyenv -u
'3.10.2' Successfully added to configuration
'3.5.2' Successfully added to configuration
'3.8.0' Successfully added to configuration
3.10.4    D:\PYTHON\3.10.4
3.10.2    C:\Users\conta\.pyenv\pyenv-win\versions\3.10.2
3.9.10    D:\PYTHON\3.9.10 : --> System Interpreter
3.8.10    D:\PYTHON\3.8.10
3.8.0     C:\Users\conta\.pyenv\pyenv-win\versions\3.8.0
3.7.9     D:\PYTHON\3.7.9
3.6.8     D:\PYTHON\3.6.8
3.5.4     D:\PYTHON\3.5.4
3.5.2     C:\Users\conta\.pyenv\pyenv-win\versions\3.5.2
```

```sh
pynball versions
3.10.4    D:\PYTHON\3.10.4
3.10.2    C:\Users\conta\.pyenv\pyenv-win\versions\3.10.2
3.9.10    D:\PYTHON\3.9.10 : --> System Interpreter
3.8.10    D:\PYTHON\3.8.10
3.8.0     C:\Users\conta\.pyenv\pyenv-win\versions\3.8.0
3.7.9     D:\PYTHON\3.7.9
3.6.8     D:\PYTHON\3.6.8
3.5.4     D:\PYTHON\3.5.4
3.5.2     C:\Users\conta\.pyenv\pyenv-win\versions\3.5.2
```

### Create a virtual environment using a version in the config

```sh
pynball mkproject 3.8.10 hobgoblin
```

### List all the virtual environments

```sh
pynball lsproject
Project Name             System Version           Pyenv Versions
============             ==============           ==============
hobgoblin                3.8.10                   -
organizer                3.9.10                   -
pizazz                   3.9.10                   -
template                 3.9.10                   -
```

### Change system interpreter

```sh
pynball system 3.6.8
```

```sh
pynball versions
3.10.4    D:\PYTHON\3.10.2
3.10.2    C:\Users\conta\.pyenv\pyenv-win\versions\3.10.2
3.9.10    D:\PYTHON\3.9.10
3.8.10    D:\PYTHON\3.8.10
3.8.0     C:\Users\conta\.pyenv\pyenv-win\versions\3.8.0
3.7.9     D:\PYTHON\3.7.9
3.6.8     D:\PYTHON\3.6.8 : --> System Interpreter
3.5.4     D:\PYTHON\3.5.4
3.5.2     C:\Users\conta\.pyenv\pyenv-win\versions\3.5.2
```

_For more examples and usage, please refer to the [Wiki][wiki]._

## Release History

- v 1.0.2
  - Work in progress

<!-- Markdown link & img dfn's -->

[virtualenvwrapper-url]: https://pypi.org/project/virtualenvwrapper/
[virtualenv-url]: https://github.com/pypa/virtualenv
[pipx-url]: https://github.com/pypa/pipx
[pyenv-url]: https://github.com/pyenv/pyenv
[pre-commit-image]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
[pre-commit-url]: https://github.com/pre-commit/pre-commit
[isort-image]: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336
[isort-url]: https://pycqa.github.io/isort/
[black-image]: https://img.shields.io/badge/code%20style-black-000000.svg
[black-url]: https://github.com/psf/black
[bandit-image]: https://img.shields.io/badge/security-bandit-yellow.svg
[bandit-url]: https://github.com/PyCQA/bandit
[mypy-image]: http://www.mypy-lang.org/static/mypy_badge.svg
[mypy-url]: http://mypy-lang.org/
[mit-license-image]: https://img.shields.io/badge/license-MIT-blue
[mit-license-url]: https://choosealicense.com/licenses/mit/
[wiki]: https://github.com/stephen-ra-king/pynball/wiki
