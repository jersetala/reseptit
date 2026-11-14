#!/usr/bin/env python3

from reseptit import db

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
    sql = 'SELECT recipe_id, recipe_user, title, content, creation_date, score FROM recipes WHERE recipe_id = ?'
    item = db.query(sql, [recipe_id])[0]
    print(item['recipe_id'])
    return db.query(sql, [recipe_id])[0]

def get_comments(recipe_id: int):
    sql = """SELECT c.comment_id, c.recipe_id, c.user_id, c.content, c.creation_date, c.last_modified, c.score, u.username
             FROM comments c, users u
             WHERE recipe_id = ?
             AND u.user_id = c.user_id"""
    return db.query(sql, [recipe_id])

def add_comment_vote(comment_id: int, user_id: int, vote_type: str):
    if vote_type not in ['upvote', 'downvote']:
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
    sql = """INSERT INTO comments (recipe_id, user_id, content, creation_date, last_modified, score)
             VALUES (?, ?, ?, datetime('now'), datetime('now'), 0)"""
    db.execute(sql, [recipe_id, user_id, content])

def delete_comment(comment_id: int, user_id: int):
    sql = """SELECT user_id FROM comments where comment_id = ?"""
    comment_author = db.query(sql, [comment_id])[0][0]
    if user_id != comment_author:
        raise ValueError

    sql = """DELETE FROM comments WHERE comment_id = ?"""
    db.execute(sql, [comment_id])
