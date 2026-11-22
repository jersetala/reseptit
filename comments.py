#!/usr/bin/env python3
"""High level functions for interacting with comments."""

from typing import Any
from sqlite3 import IntegrityError
import db
from exceptions import UserInputError, AccessControlError


def get_comments(recipe_id: int) -> Any:
    """Get all comments under the recipe identified by the given recipe_id."""
    sql = """SELECT c.comment_id, c.recipe_id, c.user_id, c.content,
                c.creation_date, c.last_modified, c.score, u.username
             FROM comments c, users u
             WHERE recipe_id = ?
             AND u.user_id = c.user_id"""
    try:
        return db.query(sql, [recipe_id])
    except Exception as e:
        raise UserInputError(f"Recipe ID {recipe_id} does not exist.") from e


def get_comment(comment_id: int) -> Any:
    """Get a comment specified by the given comment_id."""
    sql = """SELECT c.comment_id, c.recipe_id, c.user_id, c.content,
                c.creation_date, c.last_modified, c.score, u.username
             FROM comments c, users u
             WHERE comment_id = ?
             AND u.user_id = c.user_id"""
    try:
        return db.query(sql, [comment_id])[0]
    except Exception as e:
        raise UserInputError(f"Comment ID {comment_id} does not exist.") from e


def add_comment_vote(comment_id: int, user_id: int, vote_type: str) -> None:
    """Add a vote to the given comment. Also updates the score of the comment."""
    if vote_type not in ["upvote", "downvote"]:
        raise UserInputError(f'"{vote_type}" is not upvote or downvote.')

    # What this does is add a vote to the database according to the following rules:
    # 1. If a vote does not exist for that user to that comment, add it.
    # 2. If a vote exists, and the requested vote_type is the same as that, do nothing.
    # 3. If a vote exists, and the requested vote_type is opposite, flip it.
    # The scores are recalculated using sqlite triggers.
    sql = """INSERT INTO comment_votes (comment_id, user_id, vote_type)
             VALUES (?, ?, ?)
             ON CONFLICT (comment_id, user_id)
             DO UPDATE SET
                 vote_type = excluded.vote_type
             WHERE comment_votes.vote_type != excluded.vote_type"""

    try:
        db.execute(sql, [comment_id, user_id, vote_type])
    except IntegrityError as e:
        raise UserInputError("User already voted the recipe.") from e


def add_comment(recipe_id: int, user_id: int, content: str) -> None:
    """Add a comment under the specified recipe."""
    sql = """INSERT INTO comments (
                recipe_id, user_id, content, creation_date, last_modified, score
             )
             VALUES (?, ?, ?, datetime('now'), datetime('now'), 0)"""
    try:
        db.execute(sql, [recipe_id, user_id, content])
    except Exception as e:
        raise UserInputError("Failed making comment with empty content.") from e


def delete_comment(comment_id: int, user_id: int) -> None:
    """Delete the specified comment."""
    __verify_comment_owner(comment_id, user_id)
    sql = """DELETE FROM comments WHERE comment_id = ?"""
    try:
        db.execute(sql, [comment_id])
    except Exception as e:
        raise UserInputError(f"Comment ID {comment_id} does not exist.") from e


def edit_comment(comment_id: int, user_id: int, content: str) -> None:
    """Replace a specified comment with a new one."""
    __verify_comment_owner(comment_id, user_id)
    sql = """UPDATE comments
             SET content = ?
             WHERE comment_id = ?"""
    try:
        db.execute(sql, [content, comment_id, user_id])
    except Exception as e:
        raise UserInputError(
            f'Failed editing comment {comment_id} with content "{content}".'
        ) from e


def __verify_comment_owner(comment_id: int, user_id: int) -> None:
    """Verifies that the comment is owned by the given user."""
    sql = """SELECT user_id FROM comments where comment_id = ?"""
    comment_author = db.query(sql, [comment_id])[0][0]
    if user_id != comment_author:
        raise AccessControlError("Comment is not owned by user.")
