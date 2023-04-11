# ----------------- IMPORTS ----------------- #

from flask import Blueprint, redirect, url_for, request, Flask
import sqlite3
import json
from flask_bcrypt import Bcrypt

api_blueprint = Blueprint('api', __name__)
api = Flask(__name__)
bcrypt = Bcrypt(api)


# ----------------- FUNCTIONS ----------------- #


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
def addMarker():
    # Récupérer les données POST de la requête
    createur = request.form['createur']
    type_id = request.form['type_id']
    lat = request.form['lat']
    lon = request.form['lon']
    lien = request.form['lien']
    titre = request.form['titre']
    description = request.form['description']


    if check_auth(request.form['username'], request.form['password']):
        # Insérer les données dans la table "markers" de la base de données
        conn = sqlite3.connect('markers.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO markers (createur, type_id, lat, long, lien, titre, description) VALUES (?, ?, ?, ?, ?, ?, ?)', (createur, type_id, lat, lon, lien, titre, description))
        conn.commit()
        conn.close()

        # Retourner une réponse pour indiquer que l'ajout a réussi
        return 'Marker ajouté avec succès'
    else:
        return 'Erreur: identifiants incorrects'
    

@api_blueprint.route('/api/add_admin', methods=['POST'])
def addAdmin_api():
    if check_auth(request.form['username'], request.form['password']):
        if is_admin(request.form['username']):
            if add_admin(request.form['new_username'], request.form['new_password']):
                return 'Admin ajouté avec succès'
            else:
                return 'Erreur: admin déjà existant'
        else:
            return 'Erreur: vous n\'êtes pas admin'
    else:
        return 'Erreur: identifiants incorrects'


@api_blueprint.route('/api/add_user', methods=['POST'])
def addUser_api():
    if check_auth(request.form['username'], request.form['password']):
        if is_admin(request.form['username']):
            if add_user(request.form['new_username'], request.form['new_password'], request.form['email']):
                return 'Utilisateur ajouté avec succès'
            else:
                return 'Erreur: utilisateur déjà existant'
        else:
            return 'Erreur: vous n\'êtes pas admin'
    else:
        return 'Erreur: identifiants incorrects'



@api_blueprint.route('/api/drop_markers', methods=['POST'])
def dropMarkers():
    if check_auth(request.form['username'], request.form['password']):
        conn = sqlite3.connect('markers.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM markers;')
        conn.commit()
        conn.close()
        return 'Markers supprimés avec succès'
    else:
        return 'Erreur: identifiants incorrects'
    