# ----------------- IMPORTS ----------------- #

from flask import Flask, render_template, request, redirect, session, flash, url_for
from routes.api import api_blueprint, check_auth, is_admin
from db import create_db
import sqlite3

# ----------------- CONFIG ----------------- #

app = Flask(__name__)
create_db()
app.secret_key = "f71c316a6156ffe04b6a3e4d7729af2d"

app.register_blueprint(api_blueprint) # Register the api


# ----------------- ROUTES ----------------- #

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/marker/<int:marker_id>")
def marker(marker_id):
    return "<p>Marker: {}</p>".format(marker_id)

@app.route("/marker")
def markerList():
    return "<p>Marker List</p>"


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        auth = check_auth(username, password)

        if not auth:
            flash('Nom d\'utilisateur ou mot de passe incorrect.')
            return redirect(url_for('login'))

        # Si les informations de connexion sont correctes, on connecte l'utilisateur
        session['user'] = username
        if is_admin(username):
            session['admin'] = True
        else:
            session['admin'] = False
        return redirect(url_for('index'))

    if 'user' in session:
        return redirect(url_for('index'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('admin', None)
    return redirect(url_for('index'))
    


