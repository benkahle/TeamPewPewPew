// Include necessary modules for Adafruit motor shield
#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_PWMServoDriver.h"

// Create the motor shield object with the default I2C address
Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 

// Select which 'port' M1, M2, M3 or M4. In this case, M1
Adafruit_DCMotor *myMotor = AFMS.getMotor(1);

int motorspeed = 0;
byte incoming;

void setup() {
  Serial.begin(9600);
  AFMS.begin();
  // briefly power cycle the motor
  myMotor->setSpeed(5);
  myMotor->run(FORWARD);
  myMotor->run(RELEASE);
  //tell PySerial you're ready to go
  Serial.print("Initialized!");
}

void loop() {
  if (Serial.available() > 0) { //check for new data
    //convert new data to an int for motorspeed
    incoming = Serial.read();
    delay(1000);
    Serial.print(incoming);
  }
}

