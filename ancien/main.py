from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
import sqlite3
import httpx
from fastapi.staticfiles import StaticFiles
from collections import defaultdict

app = FastAPI()
IP_esp = "192.168.94.163"

API_KEY = "cbcf8b3abdce98aa70cd768ef0dcd357"
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

# Configuration du dossier des modèles HTML
templates = Jinja2Templates(directory="templates")

# Servir les fichiers statiques
app.mount("/static", StaticFiles(directory="static"), name="static")

# Fonction pour se connecter à la base de données SQLite
def get_db_connection():
    conn = sqlite3.connect("logement.db")
    conn.row_factory = sqlite3.Row  # Permet l'accès aux colonnes par leur nom
    return conn

# Fonction pour envoyer une commande à l'ESP
def send_led_signal_to_esp8266(state: str):
    """
    Envoie un signal à l'ESP8266 pour contrôler la LED.
    """
    esp8266_ip = "192.168.1.100"  # Adresse IP de l'ESP8266
    try:
        with httpx.Client() as client:
            response = client.get(f"http://{esp8266_ip}/led?state={state}")
            response.raise_for_status()
            print(f"Signal LED envoyé : {state}")
    except httpx.RequestError as e:
        print(f"Erreur lors de l'envoi du signal LED : {e}")

# Endpoint pour récupérer toutes les mesures d'un capteur
@app.get("/mesures/{id_capteur_actionneur}")
def get_mesures(id_capteur_actionneur: int):
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM Mesure WHERE id_capteur_actionneur = ?", (id_capteur_actionneur,))
        mesures = [dict(row) for row in cursor.fetchall()]
    if not mesures:
        raise HTTPException(status_code=404, detail="Aucune mesure trouvée")
    return mesures

# Endpoint pour ajouter une mesure
@app.post("/mesures")
def add_mesure(id_capteur_actionneur: int, valeur: float):
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO Mesure (id_capteur_actionneur, valeur, date_insertion) VALUES (?, ?, CURRENT_TIMESTAMP)",
            (id_capteur_actionneur, valeur),
        )
    return {"message": "Mesure ajoutée avec succès"}

# Endpoint pour récupérer toutes les factures d'un logement
@app.get("/factures/{id_logement}")
def get_factures(id_logement: int):
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM Facture WHERE id_logement = ?", (id_logement,))
        factures = [dict(row) for row in cursor.fetchall()]
    if not factures:
        raise HTTPException(status_code=404, detail="Aucune facture trouvée")
    return factures

# Endpoint pour ajouter une facture
@app.post("/factures")
def add_facture(id_logement: int, type_facture: str, montant: float, valeur_consomme: float, date: str):
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO Facture (id_logement, type_facture, montant, valeur_consomme, date) VALUES (?, ?, ?, ?, ?)",
            (id_logement, type_facture, montant, valeur_consomme, date),
        )
    return {"message": "Facture ajoutée avec succès"}

# Endpoint pour afficher les données dans un graphique
@app.get("/chart", response_class=HTMLResponse)
async def render_chart(request: Request):
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT type_facture, SUM(montant) as total FROM Facture GROUP BY type_facture")
        chart_data = [{"type": row["type_facture"], "total": row["total"]} for row in cursor.fetchall()]

    # Rendre le modèle HTML avec les données
    return templates.TemplateResponse("chart.html", {"request": request, "chart_data": chart_data})

# Endpoint pour interroger l'ESP et effectuer une action
@app.get("/fetch_data_from_esp")
def fetch_data_from_esp():
    """
    Interroge l'ESP8266 pour obtenir les données du capteur,
    les enregistre dans la base de données,
    et décide d'allumer ou d'éteindre la LED en fonction de la température.
    """
    esp8266_ip = IP_esp  # Adresse IP de l'ESP8266
    try:
        # Étape 1 : Interroger l'ESP pour obtenir les données
        with httpx.Client() as client:
            response = client.get(f"http://{esp8266_ip}/read_data")
            response.raise_for_status()
            sensor_data = response.json()

        temperature = sensor_data["temperature"]

        # Étape 2 : Enregistrer les données dans la base de données
        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO Mesure (id_capteur_actionneur, valeur, date_insertion) VALUES (?, ?, CURRENT_TIMESTAMP)",
                (1, temperature),  # Supposons que l'ID du capteur soit 1
            )

        # Étape 3 : Vérifier et allumer la LED si nécessaire
        if temperature > 10:
            send_led_signal_to_esp8266("ON")
            led_state = "ON"
        else:
            send_led_signal_to_esp8266("OFF")
            led_state = "OFF"

        return {
            "message": f"LED {led_state} en fonction de la température",
            "temperature": temperature,
            "led_state": led_state,
        }

    except httpx.RequestError as e:
        raise HTTPException(status_code=500, detail=f"Erreur de connexion à l'ESP8266 : {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=response.status_code, detail=response.text)

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

@app.get("/logement/{id_logement}/factures")
async def get_factures(id_logement: int):
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

        return factures
    except Exception as e:
        print(f"Erreur lors de la récupération des factures : {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur.")

# Endpoint pour afficher les factures d'un logement
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


@app.get("/mesures")
def get_all_mesures():
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM Mesure")
        mesures = [dict(row) for row in cursor.fetchall()]
    return mesures

@app.get("/consumption", response_class=HTMLResponse)
async def show_consumption_chart(request: Request):
    return templates.TemplateResponse("consumption_chart.html", {"request": request})

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

@app.get("/consumption-data/{id_logement}")
def get_consumption_data(id_logement: int):
    with get_db_connection() as conn:
        cursor = conn.execute("""
            SELECT type_facture, date, SUM(valeur_consomme) as total
            FROM Facture
            WHERE id_logement = ?
            GROUP BY type_facture, date
            ORDER BY date
        """, (id_logement,))
        data = [dict(row) for row in cursor.fetchall()]
    return data

@app.get("/chart-data")
def get_chart_data():
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT type_facture as type, SUM(montant) as montant FROM Facture GROUP BY type_facture")
        return [dict(row) for row in cursor.fetchall()]

# Endpoint pour afficher les pièces d'un logement
@app.get("/logement/{id_logement}", response_class=HTMLResponse)
async def show_pieces(request: Request, id_logement: int):
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM piece WHERE id_logement = ?", (id_logement,))
        pieces = [dict(row) for row in cursor.fetchall()]
    return templates.TemplateResponse("pieces.html", {"request": request, "pieces": pieces, "id_logement": id_logement})

# Endpoint pour ajouter une pièce
@app.post("/logement/{id_logement}/add-piece")
async def add_piece(id_logement: int, nom: str = Form(...), coordonnees: str = Form(...)):
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO piece (nom, coordonnees, id_logement) VALUES (?, ?, ?)",
            (nom, coordonnees, id_logement)
        )
        conn.commit()
    return RedirectResponse(url=f"/logement/{id_logement}", status_code=303)

# Endpoint pour afficher les capteurs d'une pièce
@app.get("/piece/{id_piece}", response_class=HTMLResponse)
async def show_capteurs(request: Request, id_piece: int):
    try:
        with get_db_connection() as conn:
            # Récupérer les capteurs/actionneurs associés à la pièce
            capteurs = conn.execute("""
                SELECT c.id_capteur_actionneur, c.ref_commerciale, c.port_communication, c.date_insertion,
                       t.nom_type, t.unite_mesure
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

# Endpoint pour récupérer les types de capteurs/actionneurs
@app.post("/piece/{id_piece}/add-capteur")
async def add_capteur(
    id_piece: int,
    type_capteur: str = Form(...),  # Le type choisi par l'utilisateur
    port_communication: str = Form(...),  # Port de communication fourni
):
    try:
        # Insérer le capteur/actionneur dans la base de données
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO CapteurActionneur (ref_commerciale, id_piece, id_type, port_communication, date_insertion)
                VALUES (
                    ?, ?, 
                    (SELECT id_type FROM TypeCapteurActionneur WHERE nom_type = ?), 
                    ?, CURRENT_TIMESTAMP
                )
                """,
                (
                    f"Ref-{type_capteur[:3]}-{port_communication}",  # Générer une référence commerciale basée sur le type et le port
                    id_piece,
                    type_capteur,
                    port_communication,
                ),
            )
            conn.commit()

        return RedirectResponse(url=f"/piece/{id_piece}", status_code=303)
    except Exception as e:
        print(f"Erreur lors de l'ajout du capteur/actionneur : {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'ajout du capteur/actionneur.")


# Endpoint pour ajouter un capteur/actionneur
@app.post("/piece/{id_piece}/add-capteur")
async def add_capteur(
    id_piece: int,
    ref_commerciale: str = Form(...),
    id_type: int = Form(...),
    port_communication: str = Form(...)
):
    try:
        with get_db_connection() as conn:
            conn.execute(
                """
                INSERT INTO CapteurActionneur (ref_commerciale, id_piece, id_type, port_communication)
                VALUES (?, ?, ?, ?)
                """,
                (ref_commerciale, id_piece, id_type, port_communication)
            )
            conn.commit()
        return RedirectResponse(url=f"/piece/{id_piece}", status_code=303)
    except Exception as e:
        print(f"Erreur lors de l'ajout du capteur/actionneur : {e}")
        raise HTTPException(status_code=500, detail="Erreur lors de l'ajout du capteur/actionneur.")

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

    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
