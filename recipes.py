#!/usr/bin/env python3
"""High level functions for interacting with recipes."""

from typing import Any
from sqlite3 import IntegrityError
import db
from exceptions import UserInputError, AccessControlError


def add_recipe(content: str, title: str, user_id: int) -> None:
    """Add a recipe to the database."""
    sql = """INSERT INTO recipes (user_id, title, content, creation_date, last_modified, score)
             VALUES (?, ?, ?, datetime('now'), datetime('now'), 0)"""
    try:
        db.execute(sql, [user_id, title, content])
    except Exception as e:
        if content is None or content == "":
            raise UserInputError("Failed creating recipe with empty content.") from e
        if title is None or title == "":
            raise UserInputError("Failed creating recipe with empty title.") from e
        raise UserInputError("Failed creating recipe.") from e


def get_all_recipes() -> Any:
    """Get all recipes from the database."""
    sql = """SELECT r.recipe_id, r.title, u.username, r.score, r.creation_date, u.username
             FROM recipes r, users u
             WHERE r.user_id = u.user_id
             ORDER BY r.creation_date"""
    return db.query(sql)


def get_recipe(recipe_id: int) -> Any:
    """Get recipe identified by the given recipe_id."""
    sql = """SELECT r.recipe_id, r.title, u.username, r.score, r.creation_date,
                r.content, u.username, r.user_id
             FROM recipes r, users u
             WHERE r.user_id = u.user_id
             AND r.recipe_id = ?"""

    try:
        return db.query(sql, [recipe_id])[0]
    except Exception as e:
        raise UserInputError(f"Recipe ID {recipe_id} does not exist.") from e


def delete_recipe(recipe_id: int, user_id: int) -> None:
    """Delete the specified recipe."""
    __verify_recipe_owner(recipe_id, user_id)
    sql = """DELETE FROM recipes WHERE recipe_id = ?"""
    try:
        db.execute(sql, [recipe_id])
    except Exception as e:
        raise UserInputError(f"Recipe ID {recipe_id} does not exist.") from e


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

    try:
        db.execute(sql, [recipe_id, user_id, vote_type])
    except IntegrityError as e:
        raise UserInputError("User already voted recipe.") from e


def edit_recipe(recipe_id: int, user_id: int, content: str, title: str) -> None:
    """Replace a specified recipe with a new one."""
    __verify_recipe_owner(recipe_id, user_id)
    sql = """UPDATE recipes
             SET content = ?, title = ?
             WHERE recipe_id = ?"""
    try:
        db.execute(sql, [content, title, recipe_id])
    except Exception as e:
        if content is None or content == "":
            raise UserInputError("Failed creating recipe with empty content.") from e
        if title is None or title == "":
            raise UserInputError("Failed creating recipe with empty title.") from e
        raise UserInputError("Failed creating recipe.") from e


def search_recipe(query: str) -> Any:
    """Returns recipes matching the given search term."""
    sql = """SELECT * FROM recipes
             WHERE title LIKE ?"""

    # This looks wrong but does not lead to SQL injection.
    return db.query(sql, ["%" + query + "%"])


def __verify_recipe_owner(recipe_id: int, user_id: int) -> None:
    """Verifies that the recipe is owned by the given user."""
    sql = """SELECT user_id FROM recipes WHERE recipe_id = ?"""
    recipe_author = db.query(sql, [recipe_id])[0][0]
    if user_id != recipe_author:
        raise AccessControlError("Recipe is not owned by user.")
