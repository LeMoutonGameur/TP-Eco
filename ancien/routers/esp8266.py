from fastapi import APIRouter, HTTPException
from database import get_db_connection
import httpx

router = APIRouter()
IP_ESP = "192.168.1.100"

@router.get("/fetch_data_from_esp")
async def fetch_data_from_esp():
    try:
        with httpx.Client() as client:
            response = client.get(f"http://{IP_ESP}/read_data")
            response.raise_for_status()
            sensor_data = response.json()

        temperature = sensor_data["temperature"]

        with get_db_connection() as conn:
            conn.execute(
                "INSERT INTO Mesure (id_capteur_actionneur, valeur, date_insertion) VALUES (?, ?, CURRENT_TIMESTAMP)",
                (1, temperature)
            )

        led_state = "ON" if temperature > 10 else "OFF"
        with httpx.Client() as client:
            client.get(f"http://{IP_ESP}/led?state={led_state}")

        return {"message": f"LED {led_state}", "temperature": temperature}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur ESP8266 : {e}")
