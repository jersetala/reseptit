CREATE TABLE IF NOT EXISTS users (
       user_id INTEGER PRIMARY KEY AUTOINCREMENT,
       username TEXT NOT NULL UNIQUE CHECK(length(username) <= 32),
       password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS recipes (
       recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
       recipe_user INTEGER REFERENCES users(user_id),
       title TEXT NOT NULL,
       content TEXT NOT NULL,
       creation_date TIMESTAMP NOT NULL,
       last_modified TIMESTAMP NOT NULL,
       score INTEGER
);

CREATE TABLE IF NOT EXISTS comments (
       comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
       recipe_id INTEGER REFERENCES recipes(recipe_id),
       user_id INTEGER REFERENCES users(user_id),
       content TEXT NOT NULL,
       creation_date TIMESTAMP NOT NULL,
       last_modified TIMESTAMP NOT NULL,
       score INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS comment_votes (
       vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
       comment_id INTEGER REFERENCES comments(comment_id),
       user_id INTEGER REFERENCES users(user_id),
       vote_type TEXT CHECK (vote_type in ('upvote', 'downvote')),
       UNIQUE (comment_id, user_id)
);

CREATE TRIGGER IF NOT EXISTS comment_vote_insert
AFTER INSERT ON comment_votes
BEGIN
    UPDATE comments
    SET score = score +
        CASE NEW.vote_type
             WHEN 'upvote' THEN 1
             WHEN 'downvote' THEN -1
        END
    WHERE comment_id = NEW.comment_id;
END;

CREATE TRIGGER IF NOT EXISTS comment_vote_update
AFTER UPDATE OF vote_type ON comment_votes
BEGIN
    UPDATE comments
    SET score = score
        - CASE OLD.vote_type
            WHEN 'upvote' THEN 1
            WHEN 'downvote' THEN -1
          END
        + CASE NEW.vote_type
            WHEN 'upvote' THEN 1
            WHEN 'downvote' THEN -1
          END
    WHERE comment_id = NEW.comment_id;
END;

CREATE TRIGGER IF NOT EXISTS comment_vote_delete
AFTER DELETE ON comment_votes
BEGIN
    UPDATE comments
    SET score = score -
        CASE OLD.vote_type
             WHEN 'upvote' THEN 1
             WHEN 'downvote' THEN -1
        END
    WHERE comment_id = OLD.comment_id;
END;
