# DANS UN TERMIANL CLASSIQUE 

## Start Mosquitto
cd "repertoire ou mosquitto est installé"   
sc start mosquitto
mosquitto -v

## Pour espionner un topic
```
mosquitto_sub -h localhost -t "nom_topic" 
```

# DANS UN TERMINAL ANACONDA

## Ouvrir l'environnement Fast API et taper dans le terminal pour lancer le serveur :

toute les librairies ont été instalée sur l'environnement
liste librairies utilisées qui ne sont pas de base dans python : fastapi, paho.mqtt, uvicorn, jinja2, httpx
```
conda create --name fastapi-env
conda activate fastapi-env
```

```
conda install fastapi uvicorn jinja2 sqlite
pip install paho-mqtt httpx
```

## Aller dans le repertoire du projet
```
cd Repertoire_du_projet
```
## lancement application
```
fastapi dev main.py                                         
```

## relancer la base de donnée après modification
```
sqlite3 logement.db < logement.sql
```

# CONNECTION POSSIBLE AVEC CAPTEUR

Pour verifier l'ip de l'ordi 
```
ipconfig
```

NE FONCTIONNE QUE SUR UN RESEAU LOCAL
Si un capteur est relié à une interface MQTT il est possible de le faire communiquer avec la base de donnée.
Pour ça il faut envoyé ses messages sous forme json "value : valeur_mesuré"
Pour le Topic MQTT faire attention de bien ecrire le même topic à l'ajout du capteur. 
Il est préférable pour une meilleure lecture graphique d'envoyé les données à intervale réguliée
La logique pour les actionneur voudrait que la valeur envoyé soit 0 ou 1 
 


