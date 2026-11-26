#!/usr/bin/env python3
"""Provide high level functions for handling users."""

from sqlite3 import IntegrityError
from typing import cast

from werkzeug.security import check_password_hash, generate_password_hash

import db
from exceptions import UserInputError

DUMMY_HASH = generate_password_hash("0")


def create_user(username: str, password: str) -> None:
    "Create a new user."
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    try:
        db.execute(sql, [username, password_hash])
    except IntegrityError as e:
        raise UserInputError("Failed creating user.") from e


def delete_user(user_id: int) -> None:
    """Delete the specified user."""
    db.execute("DELETE FROM users WHERE user_id = ?", [user_id])


def check_login(username: str, password: str) -> int | None:
    "Check whether a user has the given password. Returns the user_id if true."
    sql = "SELECT user_id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])
    if len(result) == 1:
        user_id, password_hash = result[0]
        if check_password_hash(password_hash, password):
            return cast(int, user_id)
        return None
    # We check the password against a dummy hash to
    # make it harder to enumerate users by a timing attack.
    check_password_hash(DUMMY_HASH, password)
    return None
