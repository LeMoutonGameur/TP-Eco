#include "DHT.h"
#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>

// Configuration du capteur DHT
#define DHTPIN 0        // GPIO0 (D3)
#define DHTTYPE DHT22   // Type du capteur DHT22
DHT dht(DHTPIN, DHTTYPE);

const char* ssid = "Instant Tethering c2950";  // Nom  Wi-Fi
const char* password = "230401Ar";   // mdp Wi-Fi

// Serveur Web sur l'ESP8266
ESP8266WebServer server(80);

int ledPin = LED_BUILTIN;  // Pin de la LED

void setup() {
  Serial.begin(115200);

  // Initialisation du capteur DHT
  dht.begin();

  // Initialisation du Wi-Fi
  WiFi.begin(ssid, password);
  Serial.print("Connexion à ");
  Serial.println(ssid);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("\nWi-Fi connecté");
  Serial.println("Adresse IP : ");
  Serial.println(WiFi.localIP());

  // Route pour lire les données du capteur
  server.on("/read_data", []() {
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    // Vérifiez si le capteur est opérationnel
    if (isnan(temperature) || isnan(humidity)) {
      server.send(500, "application/json", "{\"error\": \"Erreur de lecture du capteur\"}");
      return;
    }

    // Retourner les données sous forme JSON
    String response = "{\"temperature\": " + String(temperature) + ", \"humidity\": " + String(humidity) + "}";
    server.send(200, "application/json", response);
  });

  // Route pour contrôler la LED
  server.on("/led", []() {
    String state = server.arg("state");
    if (state == "ON") {
      digitalWrite(ledPin, HIGH);
      server.send(200, "text/plain", "LED ON");
    } else if (state == "OFF") {
      digitalWrite(ledPin, LOW);
      server.send(200, "text/plain", "LED OFF");
    } else {
      server.send(400, "text/plain", "Commande inconnue");
    }
  });

  // Configuration de la LED
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);

  // Démarrage du serveur
  server.begin();
  Serial.println("Serveur web démarré");
}

void loop() {
  server.handleClient();  // Gérer les requêtes HTTP
}
