import sqlite3, random

# Ouverture/initialisation de la base de données
conn = sqlite3.connect('logement.db')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# Fonction pour insérer une mesure dans Mesure
def insert_mesure(id_capteur_actionneur, valeur):
    # Pas besoin de date pour utiliser CURRENT_TIMESTAMP par défaut
    c.execute("""
        INSERT INTO Mesure (id_capteur_actionneur, valeur)
        VALUES (?, ?)
    """, (id_capteur_actionneur, valeur))
    print(f"Mesure insérée : Capteur {id_capteur_actionneur}, Valeur {valeur}")

# Fonction pour insérer une facture dans Facture
def insert_facture(id_logement, type_facture, montant, valeur_consomme):
    # Pas besoin de date pour utiliser CURRENT_TIMESTAMP par défaut
    c.execute("""
        INSERT INTO Facture (id_logement, type_facture, montant, valeur_consomme)
        VALUES (?, ?, ?, ?)
    """, (id_logement, type_facture, montant, valeur_consomme))
    print(f"Facture insérée : Logement {id_logement}, Type {type_facture}, Montant {montant}, Consommé {valeur_consomme}")

# Génération de mesures pour les capteurs existants
def generate_mesures():
    capteurs = {
        1: (0, 30),  # Capteur 1 : Température
        2: (100, 1000),  # Capteur 2 : Luminosité
        3: (0, 100),  # Capteur 3 : Humidité
        4: (100, 1000)  # Capteur 4 : Électricité
    }

    for id_capteur, (min_val, max_val) in capteurs.items():
        valeur = round(random.uniform(min_val, max_val), 2)
        insert_mesure(id_capteur, valeur)

# Génération de factures pour un logement avec des types aléatoires
def generate_factures(id_logement):
    types_factures = ['Électricité', 'Eau', 'Assurance', 'Gaz', 'Internet']
    type_facture = random.choice(types_factures)
    montant = round(random.uniform(20, 100), 2)
    valeur_consomme = round(random.uniform(10, 50), 2)
    insert_facture(id_logement, type_facture, montant, valeur_consomme)

# Exécution des fonctions pour remplir la base
generate_mesures()
generate_factures(1)

# Validation et fermeture de la connexion
conn.commit()
conn.close()
