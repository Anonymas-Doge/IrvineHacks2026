// SPDX-FileCopyrightText: Copyright (C) ARDUINO SRL (http://www.arduino.cc)
//
// SPDX-License-Identifier: MPL-2.0

#include <Arduino_Modulino.h>
#include <Arduino_RouterBridge.h>
#include <Wire.h>
#include <Bonezegei_LCD1602_I2C.h>

Bonezegei_LCD1602_I2C lcd(0x27);
// Create object instance 
ModulinoThermo thermo;

unsigned long previousMillis = 0; 	// Stores last time values were updated
const long interval = 1000; 		//Every second

// Non-blocking eye animation timing
unsigned long lastEyeUpdate = 0;
const long eyeOpenDuration = 3000;    // Eyes open for 800ms
const long eyeClosedDuration = 200;  // Eyes closed for 150ms
boolean eyesOpen = true;  // Track eye state

void setup() {
  Serial.begin(9600);
  delay(1000);  // Wait for Serial to initialize
  
  Serial.println("\n\nStarting Setup...");
  
  Bridge.begin();

  // Initialize Modulino I2C communication
  Modulino.begin(Wire1);
  // Detect and connect to temperature/humidity sensor module
  thermo.begin();
  
  // Initialize LCD
  Serial.println("Initializing LCD...");
  int result = lcd.begin();
  Serial.print("LCD begin result: ");
  Serial.println(result);
  
  lcd.setBacklight(1);
  Serial.println("Backlight ON");
  
  lcd.clear();
  Serial.println("LCD Cleared");
  
  // Display test message
  lcd.setPosition(0, 0);
  lcd.print("Eyes Init");
  Serial.println("Test message sent to LCD");
  
  delay(2000);
  lcd.clear();
  
  Serial.println("LCD Ready - Eyes Active!");
}

void loop() {
  unsigned long currentMillis = millis(); // Get the current time
  
  // Handle Bridge.notify on schedule (non-blocking)
  if (currentMillis - previousMillis >= interval) {
    // Save the last time you updated the values
    previousMillis = currentMillis;

    // Read temperature in Celsius from the sensor
    float celsius = thermo.getTemperature();

    Bridge.notify("record_sensor_samples", celsius);
  }

  // Handle eye blinking animation (non-blocking)
  if (eyesOpen) {
    // Eyes are open - check if it's time to close them
    if (currentMillis - lastEyeUpdate >= eyeOpenDuration) {
      // Time to blink (close eyes)
      eyesOpen = false;
      lastEyeUpdate = currentMillis;
      
      lcd.clear();
      lcd.setPosition(4, 1);
      lcd.print("_");
      lcd.setPosition(11, 1);
      lcd.print("_");
      lcd.setPosition(5, 1);
      lcd.print("_");
      lcd.setPosition(10, 1);
      lcd.print("_");
      lcd.setPosition(18, 1);
    }
  } else {
    // Eyes are closed - check if it's time to open them
    if (currentMillis - lastEyeUpdate >= eyeClosedDuration) {
      // Time to open eyes
      eyesOpen = true;
      lastEyeUpdate = currentMillis;
      
      lcd.clear();
      lcd.setPosition(5, 0);
      lcd.print(char(255));
      lcd.setPosition(10, 0);
      lcd.print(char(255));
      lcd.setPosition(4, 0);
      lcd.print(char(255));
      lcd.setPosition(11, 0);
      lcd.print(char(255));
      lcd.setPosition(5, 1);
      lcd.print(char(255));
      lcd.setPosition(10, 1);
      lcd.print(char(255));
      lcd.setPosition(4, 1);
      lcd.print(char(255));
      lcd.setPosition(11, 1);
      lcd.print(char(255));
      lcd.setPosition(18, 1);
    }
  }
}
