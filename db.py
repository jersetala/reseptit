#!/usr/bin/env python3

from typing import Any
from flask.app import T_teardown
from flask import g, Flask
import sqlite3
from sqlite3 import Connection

app = Flask(__name__)


def get_connection() -> Connection:
    if "DATABASE" not in g:
        con = sqlite3.connect("database.db")
        con.execute("PRAGMA foreign_keys = ON")
        con.row_factory = sqlite3.Row
        g.DATABASE = con

    return g.DATABASE


def execute(sql: str, params: list[Any]) -> None:
    con = get_connection()
    result = con.execute(sql, params)
    con.commit()
    g.last_insert_id = result.lastrowid


@app.teardown_appcontext
def close_connection(e=None) -> None:
    con = g.pop("DATABASE", None)

    if con is not None:
        con.close()


def last_insert_id():
    return g.last_insert_id


def query(sql: str, params: list[Any] = []) -> list[Any]:
    con = get_connection()
    result = con.execute(sql, params).fetchall()
    return result
