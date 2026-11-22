#!/usr/bin/env python3
"""Define exception classes to be used to represent invalid inputs."""


class UserInputError(Exception):
    """Exception representing an invalid user input.
    For example, a nonexisting recipe id is an invalid input."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class AccessControlError(Exception):
    """Exception representing an access control violation."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)
