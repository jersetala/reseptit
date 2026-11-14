#!/usr/bin/env python3

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
def create_recipe():
    content = escape(request.form['content'])
    title = escape(request.form['title'])
    user_id = session['user_id']

    recipes.add_recipe(content, title, user_id)
    flash("SUCCESS: Recipe created!")
    return redirect('/')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect('/')

@app.route('/new_comment', methods = ['POST'])
def new_comment():
    try:
        recipe_id = int(request.form['recipe_id'])
    except:
        flash('ERROR: Invalid recipe ID.')
        return redirect('/')
    content = escape(request.form['content'])
    user_id = session['user_id']

    recipes.add_comment(recipe_id, user_id, content)
    return redirect(f"/recipe/{recipe_id}")

@app.route('/delete_comment/<int:comment_id>', methods = ['POST', 'GET'])
def delete_comment(comment_id: int):
    user_id = session['user_id']
    try:
        recipes.delete_comment(comment_id, user_id)
    except:
        flash("FAILURE: Failed to remove comment!")
        return redirect('/')
    return redirect(request.referrer or '/')

@app.route('/vote_comment/<int:comment_id>', methods = ['POST'])
def vote_comment(comment_id: int):
    vote_type = request.form['vote']
    user_id = session['user_id']
    try:
        recipes.add_comment_vote(comment_id, user_id, vote_type)
    except Exception as e:
        flash(f"FAILURE: Failed to vote.")
        return redirect(request.referrer or '/')

    return redirect(request.referrer or '/')
