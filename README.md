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
 

 

# SOURCES 

La source principale des codes est ChatGPT qui a généré tout le frontend et a permis de réctifié toute mes endpoints (et a ajouté les commentaires)
N'etant pas grand connaisseur de developpement d'HTML CSS et javascript j'ai laissé ChatGPT s'occupé de cette partie en lui demandant d'abord une esthetique de page puis je lui redonner la première esthétique qu'il m'a donné pour chaque page en ajoutant tout ce qui serait dedans et en lui donnant les endpoints qu'il devait relié. Grâce a cette technique les pages ont casiment toutes été générées rapidement et sans besoin d'interventionde ma part.
Pour les endpoint j'ecrivait une première version du endpoint a chatGPT et je lui disait ce que je voulais qu'il fasse, il modifiait ensuite mon code pour l'adapté au critère.
J'ai du pour l'icone Home présent dans tout les header des pages demandé de l'aide à l'IA présent sur le F12 de google chrome sur les page web qui est bien plus précis que GPT sur le developpement web.

Pour les endpoints j'ai demandé d'abord à ChatGPT de me faire une cours explicatif rapide dessus ce qui m'a permis avec les codes basique qu'il m'a donné de faire des bonnes structure d'endpoint à lui donner par la suite.

# Réponses aux questions 

### 1.1 

Toute la partie 1.1 est présente dans le fichier logement.sql

### 1.2

J'ai fait un fichier remplissage.py pour cette partie mais je n'utilise pas ce fichier dans mon code finale

## 2

### Metéo 

sur le site si on séléctionne un logement ou l'on a rentré un nom correct de ville j'ai fait en sorte de faire une demande à l'API météo qui affichera le temps en Haut à droite de la page du logement (selection des pièces)

### ESP

La partie ESP fonctionne comme expliqué plus tôt grâce à des requètes MQTT. Lors de la rentré d'un capteur sur le site il est demandé le topic sur lequel le capteur communique ses données pour que le serveur s'abonne à celui-ci lors de l'ajout du capteur.

Connection au broker ligne 44 du main.py
logique de reception et ajout à la base de donnée ligne 77 main.py
ligne 303 main.y logique d'abonnement au nouveau capteur


 







