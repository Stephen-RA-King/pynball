#!/usr/bin/env python3
r"""Example CLI module using click package.
"""

# Core Library modules
import os
import subprocess
import sys

# Third party modules
import click

environment = os.name


def execute(*args, supress_exception=False, cwd=None):
    cur_dir = os.getcwd()
    try:
        if cwd:
            os.chdir(cwd)
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = proc.communicate()
        decoded_out = out.decode("utf-8")
        decoded_err = err.decode("utf-8")
        if err and not supress_exception:
            raise Exception(decoded_err)
        else:
            return decoded_out
    finally:
        os.chdir(cur_dir)


@click.group()
def switchto():
    """Creates container info to which other commands can be attached."""
    pass


@switchto.command(help="Display Package Information")
@click.option("-verbose", "--verbose", is_flag=True, help="set the verbosity")
def pkg_info(verbose):
    """Returns details about the package."""
    click.echo("Package Version: 0.1.0")
    click.echo("Author name: Stephen R A King")
    if verbose:
        click.echo("switch")
        click.echo("Utility command line to switch between python versions")


@switchto.command(help="Displays the current Python version")
def version():
    """Returns details about the current Python version."""
    click.echo("{0.major}.{0.minor}.{0.micro}".format(sys.version_info))


@switchto.command(help="Lists the names of the python versions installed")
def versions():
    """Lists the names of the python installs."""


@switchto.command(help="Finds the currently installed versions of python")
def find():
    """Finds installations of python."""


@switchto.command(help="Sets the environment variable PYTHONPATH")
def pythonpath():
    """Sets environment variable."""


@switchto.command(help="Adds the friendly name and path of an installation")
def add():
    """Adds the friendly name and path of an installation."""


@switchto.command(help="Deletes the friendly name and path of an installation")
def delete():
    """Deletes the friendly name and path of an installation."""


@switchto.command(help="Makes a virtual environment from a specific version")
def mkproject():
    """Makes a virtual environment from a specific version."""


if __name__ == "__main__":
    """Creates entry point for the CLI"""
    switchto()
