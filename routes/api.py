# ----------------- IMPORTS ----------------- #

from flask import Blueprint, redirect, url_for, request, Flask, make_response
import sqlite3
import json
from flask_bcrypt import Bcrypt
import string
import random
import datetime, time
from functools import wraps
from datetime import datetime, timedelta

api_blueprint = Blueprint('api', __name__)
api = Flask(__name__)
bcrypt = Bcrypt(api)

# ----------------- DECORATEUR ----------------- #

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.form.get('token')
        if not token:
            return make_response("token is missing", 401)

        if not check_token(token):
            return make_response("invalid token", 401)

        return f(*args, **kwargs)

    return decorated

# ----------------- FUNCTIONS ----------------- #

def check_token(token):
    conn = sqlite3.connect('markers.db')
    c = conn.cursor()
    
    # Récupère l'entrée correspondant au token
    c.execute("SELECT * FROM tokens WHERE token=?", (token,))
    entry = c.fetchone()
    
    if entry is None:
        # Le token n'est pas dans la base de données
        return False
    
    # Vérifie si le token est expiré
    expiration_date = entry[3]
    if int(time.time()) > expiration_date:
        # Le token est expiré
        return False
    
    # Le token est valide
    return True


def generate_token(user_id):
    # Génère un token aléatoire de 32 caractères
    letters_and_digits = string.ascii_letters + string.digits
    token = ''.join(random.choice(letters_and_digits) for i in range(32))

    conn = sqlite3.connect('markers.db')
    c = conn.cursor()
    c.execute("SELECT * FROM tokens WHERE token = ?", (token,))
    result = c.fetchone()
    while result is not None:
        token = ''.join(random.choice(letters_and_digits) for i in range(32))
        c.execute("SELECT * FROM tokens WHERE token = ?", (token,))
        result = c.fetchone()

    # Calcul de la date d'expiration
    expiration_date = int(time.time()) + 14400

    # Suppression des tokens precedents de l'utilisateur
    c.execute("DELETE FROM tokens WHERE user_id = ?", (user_id,))

    # Insertion du token dans la table tokens
    c.execute("INSERT INTO tokens (token, user_id, expiration_date) VALUES (?, ?, ?)", (token, user_id, expiration_date))
    conn.commit()

    return token

def check_auth(username, password):
    conn = sqlite3.connect('markers.db')
    cursor = conn.cursor()

    cursor.execute("SELECT password FROM users WHERE username=?", (username,))
    result = cursor.fetchone()
    conn.close()

    if result is not None:
        hashed_password = result[0]
        return bcrypt.check_password_hash(hashed_password, password)
    return False


def add_admin(username, password):
    conn = sqlite3.connect('markers.db')
    c = conn.cursor()
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    c.execute("SELECT username FROM users WHERE username=?", (username,))
    result = c.fetchone()
    if result is None:
        c.execute("INSERT INTO users (username, password, admin) VALUES (?, ?, ?)", (username, hashed_password, 1))
        conn.commit()
        return True
    return False

def add_user(username, password, email):
    conn = sqlite3.connect('markers.db')
    c = conn.cursor()
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    c.execute("SELECT username FROM users WHERE username=?", (username,))
    result = c.fetchone()
    if result is None:
        c.execute("INSERT INTO users (username, password, email, admin) VALUES (?, ?, ?, ?)", (username, hashed_password, email, 0))
        conn.commit()
        return True
    return False

def is_admin(username):
    conn = sqlite3.connect('markers.db')
    c = conn.cursor()
    c.execute("SELECT admin FROM users WHERE username=?", (username,))
    result = c.fetchone()
    if result is not None:
        return result[0] == 1
    return False


def get_ip_request_count(ip_address):
    conn = sqlite3.connect('markers.db')
    c = conn.cursor()
    hier = datetime.now() - timedelta(days=1)
    c.execute("SELECT COUNT(*) FROM ip_requests WHERE ip=? AND date>=?", (ip_address, hier))
    count = c.fetchone()[0]
    conn.close()
    return count


def add_ip_request(ip_address):
    conn = sqlite3.connect('markers.db')
    c = conn.cursor()
    now = datetime.now()
    c.execute("INSERT INTO ip_requests (ip, date) VALUES (?, ?)", (ip_address, now))
    conn.commit()
    conn.close()


def clean_ip_requests():
    conn = sqlite3.connect('markers.db')
    c = conn.cursor()
    now = datetime.now()
    threshold = now - timedelta(days=1)
    c.execute("DELETE FROM ip_requests WHERE date < ?", (threshold,))
    conn.commit()
    conn.close()

# ----------------- ROUTES ----------------- #


@api_blueprint.route("/api/get_all_markers_pos")
def getAllMarkers():
    conn = sqlite3.connect('markers.db')
    c = conn.cursor()
    c.execute("SELECT lat, long, id, type_id FROM markers")
    markers = c.fetchall()
    markers_list = []
    for marker in markers:
        marker_dict = {
            "lat": marker[0],
            "long": marker[1],
            "id": marker[2],
            "type" : marker[3]
        }
        markers_list.append(marker_dict)
    return json.dumps(markers_list)

@api_blueprint.route("/api/get_marker_img/<int:marker_id_type>")
def getMarkerImg(marker_id_type):
    return redirect(url_for('static', filename=f'img/{marker_id_type}.png'))


@api_blueprint.route("/api/get_marker/<int:marker_id>")
def getMarker(marker_id):
    conn = sqlite3.connect('markers.db')
    c = conn.cursor()
    c.execute("SELECT * FROM markers WHERE id=?", (marker_id,))
    marker = c.fetchone()
    if marker is not None:
        marker_dict = {
            "id": marker[0],
            "createur": marker[1],
            "type_id": marker[2],
            "lat": marker[3],
            "lon": marker[4],
            "lien": marker[5],
            "titre": marker[6],
            "description": marker[7]
        }
        return json.dumps(marker_dict)
    else:
        return "Marker non trouvé"


# Route pour ajouter un nouveau marker via l'API
@api_blueprint.route('/api/add_marker', methods=['POST'])
@token_required
def addMarker():
    # Récupérer les données POST de la requête
    createur = request.form['createur']
    type_id = request.form['type_id']
    lat = request.form['lat']
    lon = request.form['lon']
    lien = request.form['lien']
    titre = request.form['titre']
    description = request.form['description']
    # Insérer les données dans la table "markers" de la base de données
    conn = sqlite3.connect('markers.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO markers (createur, type_id, lat, long, lien, titre, description) VALUES (?, ?, ?, ?, ?, ?, ?)', (createur, type_id, lat, lon, lien, titre, description))
    conn.commit()
    conn.close()

    # Retourner une réponse pour indiquer que l'ajout a réussi
    return 'Marker ajouté avec succès'
    

@api_blueprint.route('/api/add_admin', methods=['POST'])
@token_required
def addAdmin_api():
    if add_admin(request.form['new_username'], request.form['new_password']):
        return 'Admin ajouté avec succès'
    else:
        return 'Erreur: admin déjà existant'


@api_blueprint.route('/api/add_user', methods=['POST'])
def addUser_api():
    clean_ip_requests()
    ip_address = request.remote_addr
    request_count = get_ip_request_count(ip_address)
    if 'token' not in request.form or not check_token(request.form.get('token')):
        if request_count >= 3:
            return 'Erreur: limite de création de comptes atteinte pour cette adresse IP'
    if add_user(request.form['new_username'], request.form['new_password'], request.form['email']):
        if 'token' not in request.form or not check_token(request.form.get('token')):
            add_ip_request(ip_address)
        return 'Utilisateur ajouté avec succès'
    else:
        return 'Erreur: utilisateur déjà existant'


@api_blueprint.route('/api/delete_user', methods=['POST'])
@token_required
def delete_user_api():
    username = request.form['username']
    conn = sqlite3.connect('markers.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE username=?", (username,))
    conn.commit()
    return 'Utilisateur supprimé avec succès'


@api_blueprint.route('/api/drop_markers', methods=['POST'])
@token_required
def dropMarkers():
    conn = sqlite3.connect('markers.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM markers;')
    conn.commit()
    conn.close()
    return 'Markers supprimés avec succès'
    

@api_blueprint.route('/api/get_token', methods=['POST'])
def get_token():
    username = request.form['username']
    password = request.form['password']
    
    if check_auth(username, password):
        if is_admin(username):
            token = generate_token(username)

            return make_response(token, 200)
    
    return make_response('Unauthorized', 403)
    