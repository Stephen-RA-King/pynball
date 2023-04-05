# Pynball

> Centralized management and utilization of all your Python versions, installations and virtual environments.

[![PyPI][pypi-image]][pypi-url]
[![Downloads][downloads-image]][downloads-url]
[![Status][status-image]][pypi-url]
[![Python Version][python-version-image]][pypi-url]
[![Format][format-image]][pypi-url]
[![tests][tests-image]][tests-url]
[![Codecov][codecov-image]][codecov-url]
[![CodeFactor][codefactor-image]][codefactor-url]
[![Codeclimate][codeclimate-image]][codeclimate-url]
[![CodeQl][codeql-image]][codeql-url]
[![readthedocs][readthedocs-image]][readthedocs-url]
[![pre-commit][pre-commit-image]][pre-commit-url]
[![Imports: isort][isort-image]][isort-url]
[![Code style: black][black-image]][black-url]
[![Checked with mypy][mypy-image]][mypy-url]
[![security: bandit][bandit-image]][bandit-url]
[![Commitizen friendly][commitizen-image]][commitizen-url]
[![Conventional Commits][conventional-commits-image]][conventional-commits-url]
[![DeepSource][deepsource-image]][deepsource-url]
[![license][license-image]][license-url]

![](assets/header.png)

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

1. Python 3.8+
2. [**pipx**][pipx-url]
3. [**Virtualenv**][virtualenv-url] (which has benefits over venv)
4. [**Virtualenvwrapper**][virtualenvwrapper-url]

#### For Maximum Benefits additionally install the following:

1. [**pyenv**][pyenv-url]

## Installation

OS X & Linux:

Will be supported in version 2

Windows:

```sh
pipx install pynball
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
  lsproject   Displays all Virtual Environment projects (with versions: native, tox and pyenv)
  mkproject   Creates a Virtual Environment from a specific Python version.
  mvproject   Renames a Virtual Environment (optionally updates GitHub and git)
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
Project Name             Native Version           Pyenv Versions        Tox Versions
============             ==============           ==============        ============
hobgoblin                3.8.10                   -                     3.8, 3.9, 3.10
organizer                3.9.10                   -                     -
pizazz                   3.9.10                   -                     -
template                 3.9.10                   -                     -
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

_For more information, please refer to the wiki_

## [Wiki][wiki]

## Documentation

[**Read the Docs**](https://pynball.readthedocs.io/en/latest/?)

## Meta

[![](assets/linkedin.png)](https://www.linkedin.com/in/sr-king)
[![](assets/github.png)](https://github.com/Stephen-RA-King)
[![](assets/pypi.png)](https://pypi.org/project/pynball)
[![](assets/www.png)](https://www.justpython.tech)
[![](assets/email.png)](mailto:sking.github@gmail.com)

Author: Stephen R A King

Distributed under the MIT License. See `LICENSE` for more information.

<!-- Markdown link & img dfn's -->

[bandit-image]: https://img.shields.io/badge/security-bandit-yellow.svg
[bandit-url]: https://github.com/PyCQA/bandit
[black-image]: https://img.shields.io/badge/code%20style-black-000000.svg
[black-url]: https://github.com/psf/black
[cc_template-url]: https://github.com/Stephen-RA-King/cc_template
[codeclimate-image]: https://api.codeclimate.com/v1/badges/9543c409696e9976a987/maintainability
[codeclimate-url]: https://codeclimate.com/github/Stephen-RA-King/pynball/maintainability
[codecov-image]: https://codecov.io/gh/Stephen-RA-King/pynball/branch/main/graph/badge.svg
[codecov-url]: https://app.codecov.io/gh/Stephen-RA-King/pynball
[codefactor-image]: https://www.codefactor.io/repository/github/Stephen-RA-King/pynball/badge
[codefactor-url]: https://www.codefactor.io/repository/github/Stephen-RA-King/pynball
[codeql-image]: https://github.com/Stephen-RA-King/pynball/actions/workflows/github-code-scanning/codeql/badge.svg
[codeql-url]: https://github.com/Stephen-RA-King/pynball/actions/workflows/github-code-scanning/codeql
[commitizen-image]: https://img.shields.io/badge/commitizen-friendly-brightgreen.svg
[commitizen-url]: http://commitizen.github.io/cz-cli/
[conventional-commits-image]: https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg?style=flat-square
[conventional-commits-url]: https://conventionalcommits.org
[deepsource-image]: https://static.deepsource.io/deepsource-badge-light-mini.svg
[deepsource-url]: https://deepsource.io/gh/Stephen-RA-King/pynball/?ref=repository-badge
[downloads-image]: https://static.pepy.tech/personalized-badge/pynball?period=total&units=international_system&left_color=black&right_color=orange&left_text=Downloads
[downloads-url]: https://pepy.tech/project/pynball
[format-image]: https://img.shields.io/pypi/format/pynball
[isort-image]: https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336
[isort-url]: https://github.com/pycqa/isort/
[lgtm-alerts-image]: https://img.shields.io/lgtm/alerts/g/Stephen-RA-King/pynball.svg?logo=lgtm&logoWidth=18
[lgtm-alerts-url]: https://lgtm.com/projects/g/Stephen-RA-King/pynball/alerts/
[lgtm-quality-image]: https://img.shields.io/lgtm/grade/python/g/Stephen-RA-King/pynball.svg?logo=lgtm&logoWidth=18
[lgtm-quality-url]: https://lgtm.com/projects/g/Stephen-RA-King/pynball/context:python
[license-image]: https://img.shields.io/pypi/l/pynball
[license-url]: https://github.com/Stephen-RA-King/pynball/blob/main/LICENSE
[mypy-image]: http://www.mypy-lang.org/static/mypy_badge.svg
[mypy-url]: http://mypy-lang.org/
[pip-tools-url]: https://github.com/jazzband/pip-tools/
[pre-commit-image]: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
[pre-commit-url]: https://github.com/pre-commit/pre-commit
[pre-commit.ci-image]: https://results.pre-commit.ci/badge/github/Stephen-RA-King/pynball/main.svg
[pre-commit.ci-url]: https://results.pre-commit.ci/latest/github/Stephen-RA-King/pynball/main
[pypi-url]: https://pypi.org/project/pynball/
[pypi-image]: https://img.shields.io/pypi/v/pynball.svg
[python-version-image]: https://img.shields.io/pypi/pyversions/pynball
[readthedocs-image]: https://readthedocs.org/projects/pynball/badge/?version=latest
[readthedocs-url]: https://pynball.readthedocs.io/en/latest/?badge=latest
[status-image]: https://img.shields.io/pypi/status/pynball.svg
[tests-image]: https://github.com/Stephen-RA-King/pynball/actions/workflows/tests.yml/badge.svg
[tests-url]: https://github.com/Stephen-RA-King/pynball/actions/workflows/tests.yml
[wiki]: https://github.com/Stephen-RA-King/pynball/wiki
