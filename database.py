import sqlite3

def get_db_connection():
    """
    Fonction pour se connecter à la base de données SQLite.
    """
    conn = sqlite3.connect("logement.db")
    conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par leur nom
    return conn
