#!/usr/bin/env python3

from functools import wraps
from glob import escape
import datetime
from flask import Flask, render_template, request, flash, redirect, g, session
from reseptit.config import secret_key
from sqlite3 import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
import reseptit.db as db
from reseptit.recipes import add_recipe, get_all_recipes
from reseptit.users import create_user, check_login
from markupsafe import escape

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user_id') is None:
            flash("FAILURE: Login required!")
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():
    return render_template('index.html', recipes=get_all_recipes())

@app.route('/recipe/<int:recipe_id>')
def show_recipe(recipe_id: int):
    recipe = recipes.get_recipe(recipe_id)
    comments = recipes.get_comments(recipe_id)
    return render_template('recipe.html', recipe=recipe, comments=comments)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    username = escape(request.form['username'])
    password1 = escape(request.form['password1'])
    password2 = request.form['password2']
    if password1 != password2:
        flash("FAILURE: Passwords do not match!")
        return redirect('/register')

    try:
        create_user(username, password1)
    except IntegrityError:
        flash("FAILURE: Username is taken!")
        return redirect('/register')

    flash("SUCCESS: User registered!")
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    username = escape(request.form['username'])
    password = request.form['password']

    if user_id := check_login(username, password):
        session['username'] = username
        session['user_id'] = user_id
    else:
        flash('FAILURE: Wrong username or password!')
        return redirect('/')

    flash('SUCCESS: User logged in!')
    return redirect('/')

@app.route('/create_recipe', methods = ['POST'])
@require_login
def create_recipe():
    content = escape(request.form['content'])
    title = escape(request.form['title'])
    user_id = get_user_id()

    recipes.add_recipe(content, title, user_id)
    flash("SUCCESS: Recipe created!")
    return redirect('/')

@app.route('/logout')
@require_login
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect('/')

@app.route('/new_comment', methods = ['POST'])
@require_login
def new_comment():
    try:
        recipe_id = int(request.form['recipe_id'])
    except:
        flash('ERROR: Invalid recipe ID.')
        return redirect('/')
    content = escape(request.form['content'])
    user_id = get_user_id()

    recipes.add_comment(recipe_id, user_id, content)
    return redirect(f"/recipe/{recipe_id}")

@app.route('/delete_comment/<int:comment_id>', methods = ['POST'])
@require_login
def delete_comment(comment_id: int):
    user_id = get_user_id()
    try:
        recipes.delete_comment(comment_id, user_id)
    except:
        flash("FAILURE: Failed to remove comment!")
        return redirect('/')
    return redirect(request.referrer or '/')

@app.route('/vote_comment/<int:comment_id>', methods = ['POST'])
@require_login
def vote_comment(comment_id: int):
    vote_type = request.form['vote']
    user_id = get_user_id()
    try:
        recipes.add_comment_vote(comment_id, user_id, vote_type)
    except Exception as e:
        flash(f"FAILURE: Failed to vote.")
        return redirect(request.referrer or '/')

    return redirect(request.referrer or '/')

@app.route('/delete_recipe/<int:recipe_id>')
@require_login
def delete_recipe(recipe_id: int):
    user_id = get_user_id()
    try:
        recipes.delete_recipe(recipe_id, user_id)
    except:
        flash('FAILURE: Failed to vote.')
        return redirect(request.referrer or '/')

    flash('SUCCESS: Recipe deleted')
    return redirect('/')

@app.route('/vote_recipe/<int:recipe_id>', methods = ['POST'])
@require_login
def vote_recipe(recipe_id: int):
    vote_type = request.form['vote']
    user_id = get_user_id()
    try:
        recipes.add_recipe_vote(recipe_id, user_id, vote_type)
    except Exception as e:
        flash(f"FAILURE: Failed to vote.")
        return redirect(request.referrer or '/')

    return redirect(request.referrer or '/')

@app.route('/edit_comment/<int:comment_id>', methods = ['GET', 'POST'])
@require_login
def edit_comment(comment_id: int):
    comment = recipes.get_comment(comment_id)
    if request.method == 'GET':
        return render_template('edit_comment.html', comment=comment)
    user_id = get_user_id()
    content = request.form['content']
    try:
        recipes.edit_comment(comment_id, user_id, content)
    except:
        flash("FAILURE: Failed to edit comment!")

    comment_recipe = comment['recipe_id']
    return redirect(f"/recipe/{comment_recipe}")

@app.route('/edit_recipe/<int:recipe_id>', methods = ['GET', 'POST'])
@require_login
def edit_recipe(recipe_id: int):
    recipe = recipes.get_recipe(recipe_id)
    if request.method == 'GET':
        return render_template('edit_recipe.html', recipe=recipe)
    user_id = get_user_id()
    content = request.form['content']
    title = request.form['title']
    try:
        recipes.edit_recipe(recipe_id, user_id, content, title)
    except:
        flash("FAILURE: Failed to edit comment!")

    return redirect(request.referrer or f"/recipe/{recipe_id}")

@app.route('/search', methods = ['GET'])
def search():
    # will abort() if doesn't exist
    query = request.args['q']
    results = recipes.search_recipe(query)
    return render_template("search.html", recipes=results)

def get_user_id() -> int:
    return session.get('user_id')
