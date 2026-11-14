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
       recipe_id INTEGER references recipes(recipe_id),
       user_id INTEGER references users(user_id),
       content TEXT NOT NULL,
       creation_date TIMESTAMP NOT NULL,
       last_modified TIMESTAMP NOT NULL,
       score INTEGER
);
