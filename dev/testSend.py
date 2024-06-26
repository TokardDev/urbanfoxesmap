import requests

def addmarker(createur, type_id, lat, lon, lien, titre, description, token):
    url = 'http://127.0.0.1:5000/api/add_marker'

    # Les données à envoyer en POST
    data = {
        'createur': createur,
        'type_id': type_id,
        'lat': lat, 
        'lon': lon, 
        'lien' : lien, 
        'titre' : titre,
        'description' : description,
        'token' : token
    }

    # Envoyer la requête POST
    response = requests.post(url, data=data)

    # Afficher la réponse du serveur
    print(response.text)

def dropMarkers(token):
    url = 'http://127.0.0.1:5000/api/drop_markers'
    data = {
        'token' : token
    }

    # Envoyer la requête POST
    response = requests.post(url, data=data)

    # Afficher la réponse du serveur
    print(response.text)

def addAdmin(new_username, new_password, token):
    url = 'http://127.0.0.1:5000/api/add_admin'
    data = {
        'new_username' : new_username,
        'new_password' : new_password,
        'token' : token
        
    }
    # Envoyer la requête POST
    response = requests.post(url, data=data)
    # Afficher la réponse du serveur
    print(response.text)


def getMarkers():
    url = 'http://127.0.0.1:5000/api/get_all_markers_pos'
    # Envoyer la requête POST
    response = requests.get(url)
    # Afficher la réponse du serveur
    print(response.text)


def add_user(new_username, new_password, email, token=None):
    url = 'http://127.0.0.1:5000/api/add_user'
    data = {
        'email' : email,
        'new_username' : new_username,
        'new_password' : new_password
    }

    if token != None:
        data['token'] = token

    # Envoyer la requête POST
    response = requests.post(url, data=data)
    print(response.text)


def get_token(username, password):
    url = 'http://127.0.0.1:5000/api/get_token'
    data = {
        'username' : username,
        'password' : password,
    }

    # Envoyer la requête POST
    response = requests.post(url, data=data)
    print(response.text)
    return response.text


def getMarker(id):
    url = 'http://127.0.0.1:5000/api/get_marker/'+str(id)
    # Envoyer la requête POST
    response = requests.get(url)

    # Afficher la réponse du serveur
    print(response.text)

# username : tokageki
# password : tokapass

"""
addmarker('tokageki', 'tokapass', 'Tokageki', 1, 43.607081, 1.455997, 'https://cdn.discordapp.com/attachments/828942054783975454/1095301008701280256/20230304_184253.jpg', 'bear\'s bar 2', 'sticker placé sur le poteau en face du bear\'s')
addmarker('tokageki', 'tokapass', 'Arson', 3, 43.602048, 1.434607, 'https://cdn.discordapp.com/attachments/828942054783975454/1095301041098076190/Screenshot_20230303_135031_Gallery.jpg', 'dessin sur le pont', 'dessin de Arson sur le pont Saint Pierre')
addmarker('tokageki', 'tokapass', 'Tokageki', 0, 43.533992, 1.344303, 'https://cdn.discordapp.com/attachments/828942054783975454/1095301114758443070/20230326_225518.jpg', 'Sticker sur le poteau', 'sticker de arson sur le poteau')
addmarker('tokageki', 'tokapass', 'Arson', 2, 44.664770, -1.163623, 'https://media.discordapp.net/attachments/1046431217295302708/1094967876986863696/IMG_20230410_144940.jpg', 'Sticker sur le panneau', 'Stickers à arcachon')
"""


# getMarker(1)
#dropMarkers('tokageki', 'tokapass')

#add_user('tokageki', 'tokapass', 'klem97', 'klem97', 'klem@gmail.com')
#addAdmin('tokageki', 'tokapass', 'arson', 'arsonpass')

token = get_token('tokageki', 'tokapass')
#addmarker('tokageki', 'tokapass', 'Tokageki', 1, 43.607081, 1.455997, 'https://cdn.discordapp.com/attachments/828942054783975454/1095301008701280256/20230304_184253.jpg', 'bear\'s bar 2', 'sticker placé sur le poteau en face du bear\'s', token)

"""
for i in range(4):
    import random
    import string
    alphabet = string.ascii_letters + string.digits
    random_string = ''.join(random.choices(alphabet, k=10))
    add_user(random_string, 'test', "mail@test.com")
"""

for i in range(10):
    getMarker(i)

