import sqlite3

def create_db():
    # Créer une base de données SQLite
    conn = sqlite3.connect('markers.db')
    cursor = conn.cursor()

    # Créer une table "markers" pour stocker les informations des markers
    cursor.execute('CREATE TABLE IF NOT EXISTS markers (id INTEGER PRIMARY KEY, createur TEXT, type_id INTEGER, lat REAL, long REAL, lien TEXT, titre TEXT, description TEXT)')
    conn.commit()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    admin INTEGER,
    email TEXT,
    biographie TEXT,
    pdp_lien TEXT
    );
    ''')
    conn.commit()

    cursor.execute('''DROP TABLE IF EXISTS ip_requests;''')
    conn.commit()

    # Création de la table ip_requests
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ip_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')

    # Enregistrement des changements
    conn.commit()


    cursor.execute(''' CREATE TABLE IF NOT EXISTS tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    expiration_date INTEGER NOT NULL
    );
    ''')

    conn.commit()
    conn.close()

