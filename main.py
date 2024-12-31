from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import sqlite3
import httpx
from fastapi.staticfiles import StaticFiles
from collections import defaultdict
import paho.mqtt.client as mqtt
from contextlib import asynccontextmanager
import json

app = FastAPI()

# MQTT Client
mqtt_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global mqtt_client
    mqtt_client = setup_mqtt_client()
    mqtt_client.loop_start()
    yield
    if mqtt_client:
        mqtt_client.loop_stop()
        mqtt_client.disconnect()

app = FastAPI(lifespan=lifespan)

# API Key and URL for OpenWeatherMap
API_KEY = "cbcf8b3abdce98aa70cd768ef0dcd357"
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

# Configure templates
templates = Jinja2Templates(directory="templates")

# Static files (e.g., CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")



# ------------------------------
# Functions
# ------------------------------

# Setup MQTT Client
def setup_mqtt_client():
    client = mqtt.Client()
    client.on_message = on_message

    MQTT_BROKER = "localhost"  # Replace with actual broker hostname or IP
    MQTT_PORT = 1883

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")

        # Subscribe to topics
        with get_db_connection() as conn:
            topics = conn.execute("SELECT topic FROM CapteurActionneur WHERE topic IS NOT NULL").fetchall()
            for topic_row in topics:
                client.subscribe(topic_row["topic"])
                print(f"Subscribed to topic: {topic_row['topic']}")
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")

    return client


# Database connection
def get_db_connection():
    conn = sqlite3.connect("logement.db")
    conn.row_factory = sqlite3.Row  # Access rows as dictionaries
    return conn

# Callback for when a message is received
def on_message(client, userdata, msg):
    topic = msg.topic
    try:
        # Charger le payload JSON
        payload = json.loads(msg.payload.decode("utf-8"))

        # Extraire la première clé et sa valeur
        if len(payload) != 1:
            print(f"Erreur : Payload inattendu pour le topic {topic} - {payload}")
            return

        key, valeur = list(payload.items())[0]

        # Vérifier si la valeur est valide
        if not isinstance(valeur, (int, float)):
            print(f"Erreur : La valeur extraite pour {key} n'est pas numérique : {valeur}")
            return

        # Trouver l'ID du capteur associé au topic
        with get_db_connection() as conn:
            capteur = conn.execute(
                "SELECT id_capteur_actionneur FROM CapteurActionneur WHERE topic = ?", (topic,)
            ).fetchone()

            if not capteur:
                print(f"Erreur : Aucun capteur trouvé pour le topic {topic}")
                return

            id_capteur = capteur["id_capteur_actionneur"]

            # Insérer la mesure dans la base de données
            conn.execute(
                "INSERT INTO Mesure (id_capteur_actionneur, valeur) VALUES (?, ?)",
                (id_capteur, valeur)
            )
            conn.commit()

        print(f"Mesure insérée : Topic={topic}, Clé={key}, Valeur={valeur}")
    except json.JSONDecodeError:
        print(f"Erreur : Impossible de décoder le payload JSON pour le topic {topic}")
    except Exception as e:
        print(f"Erreur lors du traitement du message MQTT : {e}")

# ------------------------------
# Home Page
# ------------------------------

# Endpoint pour afficher la page principale
@app.get("/", response_class=HTMLResponse)
async def show_index(request: Request):
    try:
        with get_db_connection() as conn:
            logements = conn.execute(
                "SELECT id_logement, adresse, ville, numero_telephone, adresse_ip, date_insertion FROM Logement"
            ).fetchall()
            logements = [dict(row) for row in logements]

        return templates.TemplateResponse(
            "index.html",
            {"request": request, "logements": logements}
        )
    except Exception as e:
        print(f"Erreur lors de la récupération des logements : {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des logements.")
    
# Endpoint pour ajouter un logement via un formulaire POST
@app.post("/add-logement")
async def add_logement(
    adresse: str = Form(...),
    ville: str = Form(...),
    numero_telephone: str = Form(...),
    adresse_ip: str = Form(...)
):
    try:
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO logement (adresse, ville, numero_telephone, adresse_ip, date_insertion)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                (adresse, ville, numero_telephone, adresse_ip)
            )
            conn.commit()
        return RedirectResponse(url="/", status_code=303)  # Redirection vers la page principale
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'ajout du logement : {str(e)}")


# ------------------------------
# Logement Details
# ------------------------------

# Endpoint pour afficher les pièces d'un logement
@app.get("/logement/{id_logement}", response_class=HTMLResponse)
async def show_pieces(request: Request, id_logement: int):
    try:
        with get_db_connection() as conn:
            # Récupérer les pièces associées au logement
            pieces = conn.execute("SELECT * FROM piece WHERE id_logement = ?", (id_logement,)).fetchall()
            pieces = [dict(row) for row in pieces]

            # Récupérer les informations du logement
            logement = conn.execute(
                "SELECT * FROM logement WHERE id_logement = ?", (id_logement,)
            ).fetchone()

        if not logement:
            raise HTTPException(status_code=404, detail="Logement non trouvé")

        # Appeler l'API météo pour récupérer la météo
        city = logement["ville"]  # Utiliser la ville directement
        weather_data = {}
        if city:  # Si la ville est disponible
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        WEATHER_API_URL,
                        params={"q": city, "appid": API_KEY, "units": "metric", "lang": "fr"}
                    )
                    response.raise_for_status()
                    weather_data = response.json()
            except Exception as e:
                print(f"Erreur lors de la récupération de la météo : {e}")

        # Extraire les informations de la météo
        weather_info = {
            "temperature": weather_data.get("main", {}).get("temp", "N/A"),
            "description": weather_data.get("weather", [{}])[0].get("description", "N/A").capitalize()
        }

        return templates.TemplateResponse(
            "pieces.html",
            {"request": request, "pieces": pieces, "id_logement": id_logement, "logement": logement, "weather": weather_info}
        )
    except Exception as e:
        print(f"Erreur : {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

# Endpoint pour ajouter une pièce à un logement via un formulaire POST
@app.post("/logement/{id_logement}/add-piece")
async def add_piece(id_logement: int, nom: str = Form(...), coordonnees: str = Form(...)):
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO piece (nom, coordonnees, id_logement) VALUES (?, ?, ?)",
            (nom, coordonnees, id_logement)
        )
        conn.commit()
    return RedirectResponse(url=f"/logement/{id_logement}", status_code=303)

# ------------------------------
# Capteurs/Actionneurs
# ------------------------------

# Endpoint pour afficher les capteurs/actionneurs d'une pièce
@app.get("/piece/{id_piece}", response_class=HTMLResponse)
async def show_capteurs(request: Request, id_piece: int):
    try:
        with get_db_connection() as conn:
            # Récupérer les capteurs/actionneurs associés à la pièce
            capteurs = conn.execute("""
                SELECT c.id_capteur_actionneur, c.ref_commerciale, c.port_communication, c.date_insertion,
                       t.nom_type, t.unite_mesure, c.topic
                FROM CapteurActionneur c
                LEFT JOIN TypeCapteurActionneur t ON c.id_type = t.id_type
                WHERE c.id_piece = ?
            """, (id_piece,)).fetchall()
            capteurs = [dict(row) for row in capteurs]

            # Récupérer les informations de la pièce
            piece = conn.execute(
                "SELECT * FROM Piece WHERE id_piece = ?", (id_piece,)
            ).fetchone()

            # Récupérer les types de capteurs/actionneurs
            types = conn.execute("SELECT * FROM TypeCapteurActionneur").fetchall()
            types = [dict(row) for row in types]

        if not piece:
            raise HTTPException(status_code=404, detail="Pièce non trouvée")

        # Ensure id_piece is passed explicitly to the template
        return templates.TemplateResponse(
            "capteurs.html",
            {
                "request": request,
                "capteurs": capteurs,
                "piece": dict(piece),  # Convert to dict for easier template handling
                "types": types,
                "id_piece": id_piece  # Pass id_piece explicitly
            }
        )
    except Exception as e:
        print(f"Erreur lors de la récupération des capteurs/actionneurs : {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des capteurs/actionneurs.")

# Endpoint pour ajouter un capteur/actionneur à une pièce via un formulaire POST
@app.post("/piece/{id_piece}/add-capteur")
async def add_capteur(
    id_piece: int,
    type_capteur: str = Form(...),  # Le type choisi par l'utilisateur
    port_communication: str = Form(...),  # Port de communication fourni
    topic: str = Form(...)  # Topic MQTT fourni
):
    global mqtt_client  # Accéder au client MQTT global
    try:
        # Insérer le capteur/actionneur dans la base de données
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO CapteurActionneur (ref_commerciale, id_piece, id_type, port_communication, topic)
                VALUES (
                    ?, ?, 
                    (SELECT id_type FROM TypeCapteurActionneur WHERE nom_type = ?), 
                    ?, ?
                )
                """,
                (
                    f"Ref-{type_capteur[:3]}-{port_communication}",  # Générer une référence commerciale basée sur le type et le port
                    id_piece,
                    type_capteur,
                    port_communication,
                    topic,
                ),
            )
            conn.commit()

        # S'abonner dynamiquement au nouveau topic MQTT
        if mqtt_client and topic:
            mqtt_client.subscribe(topic)
            print(f"Abonné au nouveau topic MQTT : {topic}")

        return RedirectResponse(url=f"/piece/{id_piece}", status_code=303)
    except Exception as e:
        print(f"Erreur lors de l'ajout du capteur/actionneur : {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'ajout du capteur/actionneur.")

# ------------------------------
# Mesures d'un Capteur
# ------------------------------

# Endpoint pour afficher les mesures d'un capteur
@app.get("/piece/{id_piece}/capteur/{id_capteur}/mesures", response_class=HTMLResponse)
async def show_mesures(request: Request, id_piece: int, id_capteur: int):
    try:
        with get_db_connection() as conn:
            # Get sensor details
            capteur = conn.execute("""
                SELECT c.id_capteur_actionneur, c.ref_commerciale, t.nom_type, t.unite_mesure
                FROM CapteurActionneur c
                LEFT JOIN TypeCapteurActionneur t ON c.id_type = t.id_type
                WHERE c.id_capteur_actionneur = ?
            """, (id_capteur,)).fetchone()

            if not capteur:
                raise HTTPException(status_code=404, detail="Capteur non trouvé")

            # Get measurements
            mesures = conn.execute("""
                SELECT valeur, date_insertion as date
                FROM Mesure
                WHERE id_capteur_actionneur = ?
                ORDER BY date_insertion ASC
            """, (id_capteur,)).fetchall()

            mesures = [dict(row) for row in mesures]

        return templates.TemplateResponse(
            "mesures_capteur.html",
            {
                "request": request,
                "id_piece": id_piece,
                "capteur": dict(capteur),
                "mesures": mesures
            }
        )
    except Exception as e:
        print(f"Erreur lors de la récupération des mesures : {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des mesures.")

# ------------------------------
# Consommation
# ------------------------------

# Endpoint pour afficher la consommation d'un logement
@app.get("/logement/{id_logement}/consumption", response_class=HTMLResponse)
async def show_consumption(request: Request, id_logement: int):
    try:
        with get_db_connection() as conn:
            # Récupérer les factures du logement
            cursor = conn.execute("""
                SELECT type_facture, date, SUM(valeur_consomme) as total
                FROM Facture
                WHERE id_logement = ?
                GROUP BY type_facture, date
                ORDER BY date
            """, (id_logement,))
            consumption_data = [dict(row) for row in cursor.fetchall()]

        # Traiter les données pour combler les lacunes
        filled_data = []
        last_values = defaultdict(lambda: 0)  # Dernière valeur mesurée par type de facture
        all_dates = sorted(set(row['date'] for row in consumption_data))  # Liste de toutes les dates

        # Grouper les données par type de facture
        grouped_data = defaultdict(list)
        for row in consumption_data:
            grouped_data[row['type_facture']].append(row)

        # Remplir les données manquantes avec la dernière valeur mesurée
        for facture_type, rows in grouped_data.items():
            rows_by_date = {row['date']: row['total'] for row in rows}
            for date in all_dates:
                if date in rows_by_date:
                    last_values[facture_type] = rows_by_date[date]
                filled_data.append({
                    "type_facture": facture_type,
                    "date": date,
                    "total": last_values[facture_type]
                })

        # Passer les données complétées au template
        return templates.TemplateResponse(
            "consumption.html",
            {"request": request, "id_logement": id_logement, "consumption_data": filled_data}
        )
    except Exception as e:
        print(f"Erreur lors de la récupération des consommations : {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des consommations.")

# ------------------------------
# Graphique des Factures
# ------------------------------

# Endpoint pour afficher un graphique des factures
@app.get("/logement/{id_logement}/factures/graphique", response_class=HTMLResponse)
async def show_factures_graph(request: Request, id_logement: int):
    try:
        with get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT type_facture, date, montant
                FROM Facture
                WHERE id_logement = ?
                ORDER BY date
            """, (id_logement,))
            factures = [dict(row) for row in cursor.fetchall()]

        if not factures:
            raise HTTPException(status_code=404, detail="Aucune facture trouvée pour ce logement.")

        return templates.TemplateResponse(
            "factures_graph_temps.html",
            {"request": request, "id_logement": id_logement, "factures": factures}
        )
    except Exception as e:
        print(f"Erreur lors de la récupération des factures pour le graphique : {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de la récupération des factures.")
