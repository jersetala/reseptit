#!/usr/bin/env python3
"""Functions for low-level interaction with the database."""
import sqlite3
from sqlite3 import Connection
from typing import Any, cast
from flask import Flask, g


def get_connection() -> Connection:
    """Return a database connection. Manages exactly one connection per request."""
    con = g.get("DATABASE")

    if con is None:
        con = sqlite3.connect("database.db")
        con.execute("PRAGMA foreign_keys = ON")
        con.row_factory = sqlite3.Row
        g.DATABASE = con

    # g.DATABASE is assigned to here.
    # It will never not be a Connection so this is fine.
    return cast(Connection, g.DATABASE)


def execute(sql: str, params: list[Any]) -> None:
    """Executes an sql statement done with statement `sql` and parameters `params`."""
    con = get_connection()
    result = con.execute(sql, params)
    con.commit()
    g.last_insert_id = result.lastrowid


def init_app(app: Flask) -> None:
    """Attaches a cleanup function to a provided `Flask` that removes a connection after
    an appcontext gets torn down."""
    @app.teardown_appcontext
    def close_connection(e: BaseException | None = None) -> None:
        con = g.pop("DATABASE", None)

        if e is not None:
            print("WARN: Connection closed due to an exception.")
        if con is not None:
            con.close()


def last_insert_id() -> int:
    """Get the row id of the last changed row."""
    # g.last_insert_id is only mutated in execute.
    # Using a cast is fine.
    return cast(int, g.last_insert_id)


def query(sql: str, params: list[Any] | None = None) -> list[Any]:
    """Return the result of a database query done with statement `sql` and parameters `params`.
    Unsafe if using INSERT, UPDATE, or DELETE operations."""
    if params is None:
        params = []
    con = get_connection()
    result = con.execute(sql, params).fetchall()
    return result
