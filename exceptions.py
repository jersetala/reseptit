#!/usr/bin/env python3

class UserInputError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class AccessControlError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
