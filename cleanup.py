#!/usr/bin/env python3
"""Uninstalls modules associated with cookiecutter package."""

# Core Library modules
import os
import subprocess
import sys


def execute(*args, supress_exception=False, cwd=None):
    """Execute command line apps with arguments."""
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


def remove_modules(module_list):
    """Checks installed modules for modules listed to be removed."""
    current_list = execute(sys.executable, "-m", "pip", "freeze", "-q", "-l")
    for module in module_list:
        if module in current_list:
            execute(
                sys.executable,
                "-m",
                "pip",
                "uninstall",
                "-y",
                "-q",
                module,
            )


if __name__ == "__main__":
    remove_these_modules = [
        "arrow",
        "binaryornot",
        "chardet",
        "cookiecutter",
        "jinja2-time",
        "poyo",
        "python-dateutil",
        "python-slugify",
        "text-unidecode",
    ]
    remove_modules(remove_these_modules)
