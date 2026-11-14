#!/usr/bin/env python3

from sqlite3 import IntegrityError
from werkzeug.security import generate_password_hash
from flask import render_template, request, flash, redirect
import reseptit.db as db
from reseptit import app

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/create', methods=['POST'])
def create():
    username = request.form['username']
    password1 = request.form['password1']
    password2 = request.form['password2']
    if password1 != password2:
        flash("FAILURE: Passwords do not match!")
        return redirect('/create')
    password_hash = generate_password_hash(password1)

    try:
        sql = 'INSERT INTO users (username, password_hash) VALUES (?, ?)'
        db.execute(sql, [username, password_hash])
    except IntegrityError:
        flash("FAILURE: Username is taken!")

    return "User created"
