from fastapi import APIRouter, HTTPException
from database import get_db_connection

router = APIRouter()

@router.get("/mesures/{id_capteur_actionneur}")
async def get_mesures(id_capteur_actionneur: int):
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM Mesure WHERE id_capteur_actionneur = ?", (id_capteur_actionneur,))
        mesures = [dict(row) for row in cursor.fetchall()]
    if not mesures:
        raise HTTPException(status_code=404, detail="Aucune mesure trouvée")
    return mesures

@router.post("/mesures")
async def add_mesure(id_capteur_actionneur: int, valeur: float):
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO Mesure (id_capteur_actionneur, valeur, date_insertion) VALUES (?, ?, CURRENT_TIMESTAMP)",
            (id_capteur_actionneur, valeur)
        )
        conn.commit()
    return {"message": "Mesure ajoutée avec succès"}
