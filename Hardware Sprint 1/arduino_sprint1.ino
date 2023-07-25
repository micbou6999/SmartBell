#include <NewPing.h>

#define TRIGGER_PIN D1  // GPIO pin connected to the trigger pin of SR04
#define ECHO_PIN D2     // GPIO pin connected to the echo pin of SR04
#define MAX_DISTANCE 200 // Maximum distance supported by the sensor in centimeters

NewPing sonar(TRIGGER_PIN, ECHO_PIN, MAX_DISTANCE);

void setup() {
  Serial.begin(115200); // Initialize serial communication
}

void loop() {
  delay(500); // Delay between readings

  unsigned int distance = sonar.ping_cm(); // Send ultrasonic pulse and get the distance in centimeters
  
  if (distance == 0) {
    Serial.println("Out of range");
  } else {
    Serial.print("Distance: ");
    Serial.print(distance);
    Serial.println(" cm");
  }
}