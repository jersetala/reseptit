#!/usr/bin/env python3

import db


def add_recipe(content: str, title: str, user_id: int):
    sql = """INSERT INTO recipes (recipe_user, title, content, creation_date, last_modified, score)
             VALUES (?, ?, ?, datetime('now'), datetime('now'), 0)"""
    db.execute(sql, [user_id, title, content])


def get_all_recipes():
    sql = """SELECT r.recipe_id, r.title, u.username, r.score, r.creation_date, u.username
             FROM recipes r, users u
             WHERE r.recipe_user = u.user_id
             ORDER BY r.creation_date"""
    return db.query(sql)


def get_recipe(recipe_id: int):
    sql = """SELECT r.recipe_id, r.title, u.username, r.score, r.creation_date,
                r.content, u.username, r.recipe_user
             FROM recipes r, users u
             WHERE r.recipe_user = u.user_id
             AND r.recipe_id = ?"""

    return db.query(sql, [recipe_id])[0]


def get_comments(recipe_id: int):
    sql = """SELECT c.comment_id, c.recipe_id, c.user_id, c.content,
                c.creation_date, c.last_modified, c.score, u.username
             FROM comments c, users u
             WHERE recipe_id = ?
             AND u.user_id = c.user_id"""
    return db.query(sql, [recipe_id])


def get_comment(comment_id: int):
    sql = """SELECT c.comment_id, c.recipe_id, c.user_id, c.content,
                c.creation_date, c.last_modified, c.score, u.username
             FROM comments c, users u
             WHERE comment_id = ?
             AND u.user_id = c.user_id"""
    return db.query(sql, [comment_id])[0]


def add_comment_vote(comment_id: int, user_id: int, vote_type: str):
    if vote_type not in ["upvote", "downvote"]:
        raise ValueError

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

    db.execute(sql, [comment_id, user_id, vote_type])


def add_comment(recipe_id: int, user_id: int, content: str):
    sql = """INSERT INTO comments (
                recipe_id, user_id, content, creation_date, last_modified, score
             )
             VALUES (?, ?, ?, datetime('now'), datetime('now'), 0)"""
    db.execute(sql, [recipe_id, user_id, content])


def delete_comment(comment_id: int, user_id: int):
    __verify_comment_owner(comment_id, user_id)
    sql = """DELETE FROM comments WHERE comment_id = ?"""
    db.execute(sql, [comment_id])


def delete_recipe(recipe_id: int, user_id: int):
    __verify_recipe_owner(recipe_id, user_id)
    sql = """DELETE FROM recipes WHERE recipe_id = ?"""
    print(recipe_id)
    print(user_id)
    db.execute(sql, [recipe_id])


def add_recipe_vote(recipe_id: int, user_id: int, vote_type: str):
    # This is one-to-one to add_comment_vote
    if vote_type not in ["upvote", "downvote"]:
        raise ValueError

    sql = """INSERT INTO recipe_votes (recipe_id, user_id, vote_type)
             VALUES (?, ?, ?)
             ON CONFLICT (recipe_id, user_id)
             DO UPDATE SET
                 vote_type = excluded.vote_type
             WHERE recipe_votes.vote_type != excluded.vote_type"""

    db.execute(sql, [recipe_id, user_id, vote_type])


def edit_comment(comment_id: int, user_id: int, content: str):
    __verify_comment_owner(comment_id, user_id)
    sql = """UPDATE comments
             SET content = ?
             WHERE comment_id = ?"""
    db.execute(sql, [content, comment_id])


def edit_recipe(recipe_id: int, user_id: int, content: str, title: str):
    __verify_recipe_owner(recipe_id, user_id)
    sql = """UPDATE recipes
             SET content = ?, title = ?
             WHERE recipe_id = ?"""
    db.execute(sql, [content, title, recipe_id])


def search_recipe(query: str):
    sql = """SELECT * FROM recipes
             WHERE title LIKE ?"""

    # This looks wrong but does not lead to SQL injection.
    return db.query(sql, ["%" + query + "%"])


def __verify_comment_owner(comment_id: int, user_id: int):
    sql = """SELECT user_id FROM comments where comment_id = ?"""
    comment_author = db.query(sql, [comment_id])[0][0]
    if user_id != comment_author:
        raise ValueError


def __verify_recipe_owner(recipe_id: int, user_id: int):
    sql = """SELECT recipe_user FROM recipes WHERE recipe_id = ?"""
    recipe_author = db.query(sql, [recipe_id])[0][0]
    if user_id != recipe_author:
        raise ValueError
