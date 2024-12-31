#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

#define DHTPIN1 0  // GPIO0 D3 - Capteur 1
#define DHTTYPE DHT22

const char* ssid = "Instant Tethering c2950";  // Nom  Wi-Fi
const char* password = "230401Ar";   // mdp Wi-Fi

const char* mqtt_server = "10.61.84.37"; // Adresse du broker MQTT
const int mqtt_port = 1883;

DHT dht(DHTPIN1, DHTTYPE);

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connexion au réseau Wi-Fi ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("Wi-Fi connecté");
  Serial.println("Adresse IP : ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Connexion au serveur MQTT...");
    if (client.connect("ESP8266Client")) {
      Serial.println("connecté");
    } else {
      Serial.print("Échec de connexion, code d’erreur = ");
      Serial.print(client.state());
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);

  setup_wifi();

  client.setServer(mqtt_server, mqtt_port);

  dht.begin();
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  float temp = dht.readTemperature();
  float hum = dht.readHumidity();

  // Créer le message JSON
  String payload1 = "{ \"temperature\": ";
  payload1 += String(temp);
  payload1 += " }";

  // Publier les données sur le topic "temp"
  client.publish("1_1", (char*) payload1.c_str());


  // Créer le message JSON
  String payload2 = "{ \"humidite\": ";
  payload2 += String(hum);
  payload2 += " }";

  // Publier les données sur le topic "temp"
  client.publish("2_2", (char*) payload2.c_str());


  delay(10000);  // Intervalle entre deux lectures 10sec
}
