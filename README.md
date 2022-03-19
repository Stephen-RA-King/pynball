# Pynball

> Centralized management and utilization of all your Python Installations.

[![pre-commit][pre-commit-image]][pre-commit-url]
[![Imports: isort][isort-image]][isort-url]
[![Code style: black][black-image]][black-url]
[![Checked with mypy][mypy-image]][mypy-url]
[![security: bandit][bandit-image]][bandit-url]
[![licence: mit][mit-license-image]][mit-license-url]

![](header.png)

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

```sh
pipx install pynball
```

Windows:

```sh
pipx install pynball
```

## Usage example

A few motivating and useful examples of how your product can be used. Spice this up with code blocks and potentially more screenshots.

_For more examples and usage, please refer to the [Wiki][wiki]._

## Release History

- v 0.1.0
  - Work in progress

## Meta

Stephen R A King : stephen.ra.king@gmail.com

Distributed under the MIT License. See `LICENSE` for more information.

[https://github.com/stephen-ra-king/pynball](https://github.com/stephen-ra-king/pynball)

## Contributing

1. Fork it (<https://github.com/stephen-ra-king/pynball/fork>)
2. Create your feature branch (`git checkout -b feature/fooBar`)
3. Commit your changes (`git commit -am 'Add some fooBar'`)
4. Push to the branch (`git push origin feature/fooBar`)
5. Create a new Pull Request

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
