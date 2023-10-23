#include <WiFiNINA.h>
#include <MQTT.h>

char ssid[] = "Sujal Jain";  
char pass[] = "12345678";
char server[] = "a32d056c843e4e16a70944e5f4eb65a6.s1.eu.hivemq.cloud";  
int port = 8883;                      // MQTT broker's port
char clientName[] = "HeartRateMonitoring";
WiFiClient wifiClient;
MQTTClient mqttClient;

int sensorPin = A3;
float calibrationFactor = 1;

void setup() {
  Serial.begin(9600);
  setupWiFi();    // Function to connect to Wi-Fi
  setupMQTT();    // Function to set up MQTT
}

void loop() {
  int sensorValue = analogRead(sensorPin);
  float correctedPulseRate = map(sensorValue, 0, 1023, 85, 125) * calibrationFactor;

  Serial.print("Heart Rate: ");
  Serial.println(correctedPulseRate);
  Serial.print("Mood Detected: ");
  
  String mood;
  if (correctedPulseRate > 35 && correctedPulseRate <= 55) mood = "SAD";
  else if (correctedPulseRate > 55 && correctedPulseRate <= 85) mood = "NEUTRAL";
  else if (correctedPulseRate > 85 && correctedPulseRate <= 125) mood = "HAPPY";

  Serial.println(mood);

  mqttClient.beginMessage("/heartrate");
  mqttClient.print(mood);
  mqttClient.endMessage();
  
  delay(3000);
}

void setupWiFi() {
  Serial.println("Connecting to Wi-Fi...");
  while (WiFi.begin(ssid, pass) != WL_CONNECTED) {
    delay(250);
    Serial.print(".");
  }
  Serial.println("\nConnected to Wi-Fi");
}

void setupMQTT() {
  Serial.println("Connecting to MQTT broker...");
  while (!mqttClient.connect(clientName, server, port)) {
    Serial.print(".");
    delay(1000);
  }
  Serial.println("\nConnected to MQTT broker");
}