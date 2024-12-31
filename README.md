## DANS UN TERMIANL CLASSIQUE 

# Start Mosquitto
cd "repertoire ou mosquitto est installé"   
sc start mosquitto
mosquitto -v

# Pour espionner un topic
mosquitto_sub -h localhost -t "nom_topic" 

# Pour verifier l'ip de l'ordi 
ipconfig


## DANS UN TERMINAL ANACONDA
# Ouvrir l'environnement Fast API et taper dans le terminal pour lancer le serveur :


# toute les librairies ont été instalée sur l'environnement
# liste librairies utilisées qui ne sont pas de base dans python : fastapi, paho.mqtt, uvicorn, jinja2, httpx
conda activate Nom_environement                                  

# repertoire du dossier
cd Repertoire_du_projet
# lancement application
fastapi dev main.py                                         

# relancer la base de donnée après modification
sqlite3 logement.db < logement.sql

