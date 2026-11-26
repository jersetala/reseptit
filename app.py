#!/usr/bin/env python3
"""The entire application. Contains the routes of the app."""

import sys
from functools import wraps
from typing import Any, Callable, cast

from flask import Flask, abort, flash, redirect, render_template, request, session
from flask.typing import ResponseReturnValue
from markupsafe import escape

import comments
import db
import recipes
from config import SECRET_KEY
from exceptions import UserInputError
from recipes import get_all_categories, get_all_recipes
from users import check_login, create_user

app = Flask(__name__)
app.secret_key = SECRET_KEY

# This allows the use of a zip filter like
# {% for val1, val2 in list1|zip(list2) %}
# which translates to
# for val1, val2 in zip(list1, list2):
# This is used at least once to combine recipes and categories.
app.jinja_env.filters["zip"] = zip

# Test if database exists.
try:
    with open("database.db", "rb") as file:
        ...
except FileNotFoundError as e:
    print("Database not found. Create a database at {e.filename}")
    print("You can do this by running in console:")
    print(f"sqlite3 {e.filename} < schema.sql")
    sys.exit()

db.init_app(app)


def require_login(f: Callable[..., Any]) -> Callable[..., Any]:
    """Wraps the given route such that the user must be logged in to access it."""

    @wraps(f)
    def decorated_function(*args: Any, **kwargs: Any) -> Any:
        if session.get("user_id") is None:
            flash("FAILURE: Login required!")
            return redirect("/")
        return f(*args, **kwargs)

    return decorated_function


@app.route("/")
def index() -> str:
    """Return the index of the webapp."""
    recipes_, categories = get_all_recipes()
    return render_template(
        "index.html",
        recipes=recipes_,
        all_categories=get_all_categories(),
        categories=categories,
    )


@app.route("/recipe/<int:recipe_id>")
def show_recipe(recipe_id: int) -> str:
    "Return detailed information about a recipe."
    recipe, categories = recipes.get_recipe(recipe_id)
    if not recipe:
        flash("FAILUREL: No such recipe found!")
    comment_list = comments.get_comments(recipe_id)
    return render_template(
        "recipe.html",
        recipe=recipe,
        comments=comment_list,
        recipe_categories=categories,
        all_categories=get_all_categories(),
    )


@app.route("/register", methods=["GET", "POST"])
def register() -> ResponseReturnValue:
    """Handle user registration. If accessed with GET, render the form.
    If accessed with POST, do the database operation to register."""
    if request.method == "GET":
        return render_template("register.html")
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        flash("FAILURE: Passwords do not match!")
        return redirect("/register")

    username = username.strip()

    if len(username) > 32:
        flash("FAILURE: Username is too long!")
        return redirect("/register")

    if len(username) < 4:
        flash("FAILURE: Username is too short!")
        return redirect("/register")

    try:
        create_user(username, password1)
    except UserInputError:
        flash("FAILURE: Username is taken!")
        return redirect("/register")

    flash("SUCCESS: User registered!")
    return redirect("/")


@app.route("/login", methods=["POST"])
def login() -> ResponseReturnValue:
    """Log the user in by adding their user_id to the session if
    the username and password match."""
    username = escape(request.form["username"])
    password = request.form["password"]

    if user_id := check_login(username, password):
        session["username"] = username
        session["user_id"] = user_id
    else:
        flash("FAILURE: Wrong username or password!")
        return redirect("/")

    flash("SUCCESS: User logged in!")
    return redirect("/")


@app.route("/create_recipe", methods=["POST"])
@require_login
def create_recipe() -> ResponseReturnValue:
    """Takes a form and creates a recipe from the form."""
    content = escape(request.form["content"]).strip()
    title = escape(request.form["title"]).strip()
    user_id = get_user_id()
    categories = request.form.getlist("categories[]")

    if len(title) < 4:
        flash("FAILURE: Title is too short!")
        return redirect("/")

    if len(content) < 4:
        flash("FAILURE: Content is too short!")
        return redirect("/")

    recipes.add_recipe(content, title, user_id, categories)
    flash("SUCCESS: Recipe created!")
    return redirect("/")


@app.route("/logout")
@require_login
def logout() -> ResponseReturnValue:
    """Clear the session."""
    session.clear()
    return redirect("/")


@app.route("/new_comment", methods=["POST"])
@require_login
def new_comment() -> ResponseReturnValue:
    """Add a comment under a recipe according to a form."""
    try:
        recipe_id = int(request.form["recipe_id"])
    except ValueError:
        flash("ERROR: Invalid recipe ID.")
        return redirect(request.referrer or "/")
    recipe, _ = recipes.get_recipe(recipe_id)
    if not recipe:
        flash("ERROR: Invalid recipe ID.")
        return redirect(request.referrer or "/")

    content = request.form["content"]
    user_id = get_user_id()

    comments.add_comment(recipe_id, user_id, content)
    return redirect(f"/recipe/{recipe_id}")


@app.route("/delete_comment/<int:comment_id>", methods=["POST"])
@require_login
def delete_comment(comment_id: int) -> ResponseReturnValue:
    """Delete the given comment."""
    user_id = get_user_id()
    comment = comments.get_comment(comment_id)

    if not comment:
        flash("FAILURE: No such comment!")
        return redirect(request.referrer or "/")
    if user_id != comment["user_id"]:
        flash("FAILURE: No access!")
        return redirect(request.referrer or "/")

    comments.delete_comment(comment_id)
    return redirect(request.referrer or "/")


@app.route("/vote_comment/<int:comment_id>", methods=["POST"])
@require_login
def vote_comment(comment_id: int) -> ResponseReturnValue:
    """Either upvote or downvote the given comment according to a form."""
    vote_type = request.form["vote"]
    user_id = get_user_id()
    comments.add_comment_vote(comment_id, user_id, vote_type)

    return redirect(request.referrer or "/")


@app.route("/delete_recipe/<int:recipe_id>", methods=["POST"])
@require_login
def delete_recipe(recipe_id: int) -> ResponseReturnValue:
    """Delete the given recipe."""
    user_id = get_user_id()
    recipe, _ = recipes.get_recipe(recipe_id)
    if not recipe:
        flash("FAILURE: No such recipe found!")
    if user_id != recipe["user_id"]:
        flash("FAILURE: No accesss!")
        return redirect(request.referrer)

    recipes.delete_recipe(recipe_id)
    flash("SUCCESS: Recipe deleted.")
    return redirect("/")


@app.route("/vote_recipe/<int:recipe_id>", methods=["POST"])
@require_login
def vote_recipe(recipe_id: int) -> ResponseReturnValue:
    """Either upvote or downvote the given recipe according to a form."""
    vote_type = request.form["vote"]
    user_id = get_user_id()
    try:
        recipes.add_recipe_vote(recipe_id, user_id, vote_type)
    except UserInputError:
        flash(f"FAILURE: No such vote type {vote_type}!")
    return redirect(request.referrer or "/")


@app.route("/edit_comment/<int:comment_id>", methods=["GET", "POST"])
@require_login
def edit_comment(comment_id: int) -> ResponseReturnValue:
    """If the request method is GET, render a form for editing a comment.
    If the method is POST replace the given comment by a new one given by the form."""
    comment = comments.get_comment(comment_id)
    if comment is None:
        flash("FAILURE: No such comment!")
        return redirect(request.referrer or "/")

    user_id = get_user_id()
    if request.method == "GET":
        if user_id != comment["user_id"]:
            flash("FAILURE: No access!")
            return redirect(request.referrer or "/")
        return render_template("edit_comment.html", comment=comment)

    content = request.form["content"].strip()

    if content == "":
        flash("FAILURE: Comment is empty!")
        return redirect(request.referrer or "/")

    comments.edit_comment(comment_id, content)
    comment_recipe = comment["recipe_id"]
    return redirect(f"/recipe/{comment_recipe}")


@app.route("/edit_recipe/<int:recipe_id>", methods=["GET", "POST"])
@require_login
def edit_recipe(recipe_id: int) -> ResponseReturnValue:
    """If the request method is GET, render a form for editing a recipe.
    If the method is POST replace the given recipe by a new one given by the form."""

    recipe, categories = recipes.get_recipe(recipe_id)
    user_id = get_user_id()

    if not recipe:
        flash("FAILURE: No such recipe!")
        return redirect(request.referrer or "/")

    if user_id != recipe["user_id"]:
        flash("FAILURE: No access!")
        return redirect(request.referrer or "/")

    if request.method == "GET":
        return render_template(
            "edit_recipe.html",
            recipe=recipe,
            recipe_categories=categories,
            all_categories=recipes.get_all_categories(),
        )

    content = request.form["content"].strip()
    title = request.form["title"].strip()
    if len(title) < 4:
        flash("FAILURE: Title is too short!")
    if len(content) < 4:
        flash("FAILURE: Content is too short!")
    categories = request.form.getlist("categories[]")
    recipes.edit_recipe(recipe_id, content, title, categories)

    return redirect(f"/recipe/{recipe_id}")


@app.route("/search", methods=["GET"])
def search() -> str:
    """Display search results for recipes with a query given by a request argument."""
    # will abort() if doesn't exist
    query = request.args.get("q", "")
    categories = request.args.getlist("categories")
    recipes_, categories_ = recipes.search_recipe(query, categories)
    # This is just so we can show something if the search returns nothing.
    have_searched = request.args.get("have_searched") is not None

    return render_template(
        "search.html",
        recipes=recipes_,
        all_categories=get_all_categories(),
        categories=categories_,
        have_searched=have_searched,
    )


def get_user_id() -> int:
    """Return the current user id from the session."""
    user_id = session.get("user_id")
    if user_id is None:
        abort(403)
    return cast(int, user_id)
