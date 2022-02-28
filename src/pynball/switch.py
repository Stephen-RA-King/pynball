#!/usr/bin/env python3
"""Example Module with Google style docstrings."""

# Core Library modules
import os
import warnings


class ExampleClass:
    """The summary line for a class docstring should fit on one line.

    If the class has public attributes, they may be documented here

    Attributes:
        attr1 (str): Description of `attr1`.
        attr2 (:obj:`int`, optional): Description of `attr2`.

    """

    def __init__(self, param1, param2, param3):
        """Document docstring on the __init__ method.

        The __init__ method may be documented in either the class level
        docstring, or as a docstring on the __init__ method itself.

        Either form is acceptable, but the two should not be mixed. Choose one
        convention to document the __init__ method and be consistent with it.

        Note:
            Do not include the `self` parameter in the ``Args`` section.

        Args:
            param1 (str): Description of `param1`.
            param2 (str): Description of `param21`.
            param3 (list(str)): Description of `param3`.

        """
        self.attr1 = param1
        self.attr2 = param2
        self.attr3 = param3

    def example_method(self, param1, param2):
        """Class methods are similar to regular functions.

        Note:
            Do not include the `self` parameter in the ``Args`` section.

        Args:
            param1: The first parameter.
            param2: The second parameter.

        Returns:
            True if successful, False otherwise.

        """
        return True


def function_with_pep484_type_annotations(param1: int, param2: str) -> bool:
    """Document PEP 484 type annotations.

    Args:
        param1: The first parameter.
        param2: The second parameter.

    Returns:
        The return value. True for success, False otherwise.

    """
    if param1 == param2:
        raise ValueError("param1 may not be equal to param2")
    return True


def module_level_function(param1, param2=None, *args, **kwargs):
    """Document module level function.

    Function parameters should be documented in the ``Args`` section.

    Args:
        param1 (int): The first parameter.
        param2 (:obj:`str`, optional): The second parameter. Defaults to None.
            Second line of description should be indented.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        bool: True if successful, False otherwise.

    Raises:
        AttributeError: The ``Raises`` section is a list of all exceptions
            that are relevant to the interface.
        ValueError: If `param2` is equal to `param1`.

    """
    if param1 == param2:
        raise ValueError("param1 may not be equal to param2")
    return True


def doubleit(num):
    """Given a number, Returns double of the number."""
    if not isinstance(num, (int, float)):
        raise TypeError("Enter an Integer")
    var = num * 2
    return var


def addit(num1, num2):
    """Function return used to test approximation of float addition."""
    var = num1 + num2
    return var


def div_by_zero():
    """Function return will be used to test exceptions."""
    return 1 / 0


def manual_exception():
    """Function return to trigger ValueError in tests."""
    return 10


def check_message(pet):
    """Function return to trigger ValueError in tests."""
    if pet != "cat":
        raise ValueError("pet must be cat")


def lame_function():
    """Function return will be used to test for warnings."""
    warnings.warn("Please stop using this", DeprecationWarning)


def check_output():
    """Function return will be used in capture output tests."""
    print("hello world")


def getssh():
    """Monkeypatch this function in test - this Original function is not changed."""
    return os.path.join(os.path.expanduser("~admin"), "ssh")


def main():
    """Main function. Returns passed."""
    pass


if __name__ == "__main__":
    main()
