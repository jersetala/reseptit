#!/usr/bin/env python3

from werkzeug.security import generate_password_hash, check_password_hash
from reseptit import db

DUMMY_HASH = generate_password_hash("0")

def create_user(username: str, password: str) -> None:
    password_hash = generate_password_hash(password)
    sql = 'INSERT INTO users (username, password_hash) VALUES (?, ?)'
    db.execute(sql, [username, password_hash])

def check_login(username: str, password: str) -> int|None:
    sql = 'SELECT user_id, password_hash FROM users WHERE username = ?'
    result = db.query(sql, [username])
    if len(result) == 1:
        user_id, password_hash = result[0]
        if check_password_hash(password_hash, password):
            return user_id
    else:
        # We check the password against a dummy hash to
        # make it harder to enumerate users by a timing attack.
        check_password_hash(DUMMY_HASH, password)
        return None
