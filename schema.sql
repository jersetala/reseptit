-- Local Variables:
-- sql-product: sqlite
-- End:

-- Tables
CREATE TABLE IF NOT EXISTS users (
       user_id INTEGER PRIMARY KEY AUTOINCREMENT,
       username TEXT NOT NULL UNIQUE CHECK(length(username) <= 32),
       password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS recipes (
       recipe_id INTEGER PRIMARY KEY AUTOINCREMENT,
       user_id INTEGER,
       title TEXT NOT NULL,
       content TEXT NOT NULL,
       creation_date TIMESTAMP NOT NULL,
       last_modified TIMESTAMP NOT NULL,
       score INTEGER,
       cook_time INTEGER,
       category INTEGER,
       yield INTEGER,
       diet INTEGER,
       FOREIGN KEY (user_id) REFERENCES users(user_id)
           ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS diets (
       diet_id INTEGER PRIMARY KEY AUTOINCREMENT,
       diet_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS recipe_categories (
       category_id INTEGER PRIMARY KEY AUTOINCREMENT,
       category_name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS recipe_categoy_assignments (
       recipe_id INTEGER NOT NULL,
       category_id INTEGER NOT NULL,
       FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id),
       FOREIGN KEY (category_id) REFERENCES recipe_categories(category_id),
       UNIQUE (recipe_id, category_id)
);

CREATE TABLE IF NOT EXISTS recipe_votes (
       vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
       recipe_id INTEGER NOT NULL,
       user_id INTEGER NOT NULL,
       vote_type TEXT CHECK (vote_type in ('upvote', 'downvote')),
       FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id)
           ON DELETE CASCADE,
       FOREIGN KEY (user_id) REFERENCES users(user_id)
           ON DELETE CASCADE,
       UNIQUE (recipe_id, user_id)
);

CREATE TABLE IF NOT EXISTS comments (
       comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
       recipe_id INTEGER NOT NULL,
       user_id INTEGER NOT NULL,
       content TEXT NOT NULL,
       creation_date TIMESTAMP NOT NULL,
       last_modified TIMESTAMP NOT NULL,
       score INTEGER NOT NULL DEFAULT 0,
       FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id)
           ON DELETE CASCADE,
       FOREIGN KEY (user_id) REFERENCES users(user_id)
           ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comment_votes (
       vote_id INTEGER PRIMARY KEY AUTOINCREMENT,
       comment_id INTEGER NOT NULL,
       user_id INTEGER NOT NULL,
       vote_type TEXT CHECK (vote_type in ('upvote', 'downvote')),
       FOREIGN KEY (comment_id) REFERENCES comments(comment_id)
           ON DELETE CASCADE,
       FOREIGN KEY (user_id) REFERENCES users(user_id)
           ON DELETE CASCADE,
       UNIQUE (comment_id, user_id)
);

-- Triggers
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

CREATE TRIGGER IF NOT EXISTS recipe_vote_insert
AFTER INSERT ON recipe_votes
BEGIN
    UPDATE recipes
    SET score = score +
        CASE NEW.vote_type
             WHEN 'upvote' THEN 1
             WHEN 'downvote' THEN -1
        END
    WHERE recipe_id = NEW.recipe_id;
END;

CREATE TRIGGER IF NOT EXISTS recipe_vote_update
AFTER UPDATE OF vote_type ON recipe_votes
BEGIN
    UPDATE recipes
    SET score = score
        - CASE OLD.vote_type
            WHEN 'upvote' THEN 1
            WHEN 'downvote' THEN -1
          END
        + CASE NEW.vote_type
            WHEN 'upvote' THEN 1
            WHEN 'downvote' THEN -1
          END
    WHERE recipe_id = NEW.recipe_id;
END;

CREATE TRIGGER IF NOT EXISTS recipe_vote_delete
AFTER DELETE ON recipe_votes
BEGIN
    UPDATE recipes
    SET score = score -
        CASE OLD.vote_type
             WHEN 'upvote' THEN 1
             WHEN 'downvote' THEN -1
        END
    WHERE recipe_id = OLD.recipe_id;
END;
