#!/usr/bin/env python3
"""High level functions for interacting with recipes."""

from typing import Any, cast
import db
from exceptions import UserInputError


def get_all_categories() -> Any:
    """Get list of all categoris specified in the database."""
    sql = """SELECT category_name, category_title FROM recipe_categories"""
    res = db.query(sql)
    categories = {}
    for name, title in res:
        categories[name] = title

    return cast(dict[str, str], categories)


def get_recipe_categories(recipe_id: int) -> Any:
    """Get a list of category names related to a specified recipe."""
    sql = """SELECT c.category_name
             FROM recipe_categories AS c
             JOIN recipe_category_assignments AS a
                 ON a.category_id = c.category_id
             WHERE a.recipe_id = ?
             ORDER BY c.category_title"""
    return db.query(sql, [recipe_id])


def add_recipe(content: str, title: str, user_id: int, categories: list[str]) -> None:
    """Add a recipe to the database."""
    sql_add_recipe = """INSERT INTO recipes (
                            user_id, title, content, creation_date, last_modified, score
                        )
                        VALUES (?, ?, ?, datetime('now'), datetime('now'), 0)"""
    sql_add_category = """INSERT INTO recipe_category_assignments (recipe_id, category_id)
                          SELECT ?, category_id
                          FROM recipe_categories
                          WHERE category_name = ?
                          ON CONFLICT(recipe_id, category_id) DO NOTHING"""

    all_categories = get_all_categories()
    # This is impossible to do atomically without managing a transaction
    # outside of functions provided by db.py or it would be very complicated.
    con = db.get_connection()
    # Only include unique categories.
    categories = list(set(categories))
    with con:
        cursor = con.cursor()
        cursor.execute(sql_add_recipe, (user_id, title, content))
        recipe_id = cursor.lastrowid

        for category in categories:
            if category not in all_categories:
                continue
            cursor.execute(sql_add_category, (recipe_id, category))


def get_all_recipes() -> Any:
    """Get all recipes from the database."""
    sql = """SELECT r.recipe_id, r.title, u.username, r.score, r.creation_date, u.username
             FROM recipes r, users u
             WHERE r.user_id = u.user_id
             ORDER BY r.creation_date"""

    recipes = db.query(sql)
    categories = []
    for recipe in recipes:
        categories.append(get_recipe_categories(recipe["recipe_id"]))
    return (recipes, categories)


def get_recipe(recipe_id: int) -> tuple[Any, Any]:
    """Get recipe identified by the given recipe_id."""
    sql = """SELECT r.recipe_id, r.title, u.username, r.score, r.creation_date,
                r.content, u.username, r.user_id
             FROM recipes r, users u
             WHERE r.user_id = u.user_id
             AND r.recipe_id = ?"""

    result = db.query(sql, [recipe_id])

    if result:
        recipe = result[0]
        categories = get_recipe_categories(recipe["recipe_id"])
    else:
        categories = []
        recipe = None

    return (recipe, categories)


def delete_recipe(recipe_id: int) -> None:
    """Delete the specified recipe."""
    sql = """DELETE FROM recipes WHERE recipe_id = ?"""
    db.execute(sql, [recipe_id])


def add_recipe_vote(recipe_id: int, user_id: int, vote_type: str) -> None:
    """Add a vote under the specified recipe. Also calculates the new score."""
    # This is one-to-one to comments:add_comment_vote
    if vote_type not in ["upvote", "downvote"]:
        raise UserInputError(f'"{vote_type}" is not upvote or downvote.')

    sql = """INSERT INTO recipe_votes (recipe_id, user_id, vote_type)
             VALUES (?, ?, ?)
             ON CONFLICT (recipe_id, user_id)
             DO UPDATE SET
                 vote_type = excluded.vote_type
             WHERE recipe_votes.vote_type != excluded.vote_type"""

    db.execute(sql, [recipe_id, user_id, vote_type])


def edit_recipe(
    recipe_id: int, content: str, title: str, categories: list[str]
) -> None:
    """Replace a specified recipe with a new one."""
    sql_update_recipe = """UPDATE recipes
                        SET content = ?, title = ?, last_modified = datetime('now')
                        WHERE recipe_id = ?"""
    sql_delete_categories = """DELETE FROM recipe_category_assignments
                               WHERE recipe_id = ?"""
    sql_add_category = """INSERT INTO recipe_category_assignments (recipe_id, category_id)
                          SELECT ?, category_id
                          FROM recipe_categories
                          WHERE category_name = ?
                          ON CONFLICT(recipe_id, category_id) DO NOTHING"""

    all_categories = get_all_categories()
    con = db.get_connection()
    categories = list(set(categories))
    with con:
        cursor = con.cursor()
        cursor.execute(sql_update_recipe, (content, title, recipe_id))
        cursor.execute(sql_delete_categories, (recipe_id,))

        for category in categories:
            if category not in all_categories:
                continue
            cursor.execute(sql_add_category, (recipe_id, category))


def search_recipe(query: str, categories: list[str]) -> Any:
    """Returns recipes that match the given search term
    and contain at least one of the categories."""
    if categories:
        placeholders = ",".join("?" for _ in categories)
        sql = f"""SELECT DISTINCT r.*
              FROM recipes AS r
              JOIN recipe_category_assignments AS a
                  ON a.recipe_id = r.recipe_id
              JOIN recipe_categories AS c
                  ON c.category_id = a.category_id
              WHERE c.category_name IN ({placeholders})
                  AND r.title LIKE ?"""

        recipes = db.query(sql, [*categories, "%" + query + "%"])
    else:
        sql = """SELECT * FROM recipes AS r
                 WHERE r.title LIKE ?"""
        recipes = db.query(sql, ["%" + query + "%"])

    cats = []
    for recipe in recipes:
        cats.append(get_recipe_categories(recipe["recipe_id"]))
    return (recipes, cats)


def get_user_recipes(user_id: int) -> Any:
    """Get all recipes authored by a specified user."""
    sql = """SELECT * FROM recipes
             WHERE user_id = ?"""
    result = db.query(sql, [user_id])

    if result:
        recipes = result
        categories = []
        for recipe in recipes:
            categories.append(get_recipe_categories(recipe["recipe_id"]))
    else:
        recipes = []
        categories = []

    return (recipes, categories)
