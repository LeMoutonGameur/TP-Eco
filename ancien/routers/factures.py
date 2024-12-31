from fastapi import APIRouter, HTTPException
from database import get_db_connection

router = APIRouter()

@router.get("/factures/{id_logement}")
async def get_factures(id_logement: int):
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM Facture WHERE id_logement = ?", (id_logement,))
        factures = [dict(row) for row in cursor.fetchall()]
    if not factures:
        raise HTTPException(status_code=404, detail="Aucune facture trouvée")
    return factures

@router.post("/factures")
async def add_facture(id_logement: int, type_facture: str, montant: float, valeur_consomme: float, date: str):
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO Facture (id_logement, type_facture, montant, valeur_consomme, date) VALUES (?, ?, ?, ?, ?)",
            (id_logement, type_facture, montant, valeur_consomme, date)
        )
        conn.commit()
    return {"message": "Facture ajoutée avec succès"}
