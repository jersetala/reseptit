#!/usr/bin/env python3

from reseptit import db

def add_recipe(content: str, title: str, user_id: int):
    sql = """INSERT INTO recipes (recipe_user, title, content, creation_date, last_modified, score)
             VALUES (?, ?, ?, datetime('now'), datetime('now'), 0)"""
    db.execute(sql, [user_id, title, content])
