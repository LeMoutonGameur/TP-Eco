from fastapi import APIRouter, HTTPException
from database import get_db_connection

# Création d'une instance APIRouter
router = APIRouter()

# Endpoint pour récupérer tous les logements
@router.get("/api/logements")
async def get_logements():
    with get_db_connection() as conn:
        logements = conn.execute("SELECT id_logement AS id, adresse FROM logement").fetchall()
        return [{"id": row["id"], "adresse": row["adresse"]} for row in logements]

# Endpoint pour ajouter un logement
@router.post("/api/logements")
async def add_logement(nom: str, adresse: str):
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO logement (nom, adresse, date_insertion) VALUES (?, ?, CURRENT_TIMESTAMP)",
            (nom, adresse)
        )
        conn.commit()
    return {"message": "Logement ajouté avec succès"}
