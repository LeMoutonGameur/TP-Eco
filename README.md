// Strat Mosquitto 
// Terminal classique 

cd "C:\Program Files\mosquitto"   //repertoire ou mosquitto est installé
sc start mosquitto
mosquitto -v

// pour espionner un topic : mosquitto_sub -h localhost -t "test/topic"  //mettre le nom du topic entre les guillemets
// pour verifier l'ip de l'ordi : ipconfig

// Ouvrir l'environnement Fast API et taper dans le terminal pour lancer le serveur :

conda activate fastapi-env                                  // toute les librairies ont été instalée sur l'environnement
                                                            // liste librairies utilisées qui ne sont pas de base dans python : fastapi, paho.mqtt, uvicorn, jinja2, httpx

cd C:\Users\arthu\OneDrive\Bureau\Année4\IoT\TP Eco         //repertoire du dossier
fastapi dev main.py                                         //lancement application

// relancer la base de donnée après modification : sqlite3 logement.db < logement.sql

