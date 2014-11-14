// Include necessary modules for Adafruit motor shield
#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include "utility/Adafruit_PWMServoDriver.h"

// Create the motor shield object with the default I2C address
Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 
Adafruit_StepperMotor *stepperY = AFMS.getStepper(48, 1); // Motor 1 L/R BYGR
Adafruit_StepperMotor *stepperX = AFMS.getStepper(48, 2); // Motor 2 L/R BYGR

const int safePin = 4;
const int stepsPerCommand = 10;

int safe = 0;
int xEnIndex = 4;
int xSignIndex = 3;
int yEnIndex = 2;
int ySignIndex = 1;
int trigEnIndex = 0;

void setup() {
  Serial.begin(9600);
  AFMS.begin();
  stepperX->setSpeed(120);
  stepperY->setSpeed(120);
  pinMode(safePin, INPUT);
  pinMode(0, OUTPUT);
  pinMode(1, OUTPUT);
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(13, OUTPUT);
}

void stepMotor(int stepSign, Adafruit_StepperMotor* stepper) {
  stepper->step(stepsPerCommand, stepSign, SINGLE);
}

void shoot() {

}

void loop() {
  // safe = digitalRead(safePin);
  // stepMotor(50, stepperY); 
  // delay(50);
  safe = 1;
  if (safe) {
    if (Serial.available() > 0) {
      byte command = Serial.read();
      int xEn = (command & (1 << xEnIndex)) >> xEnIndex;
      int xSign = (command & (1 << xSignIndex)) >> xSignIndex;
      int yEn = (command & (1 << yEnIndex)) >> yEnIndex;
      int ySign = (command & (1 << ySignIndex)) >> ySignIndex;
      int trigEn = (command & (1 << trigEnIndex)) >> trigEnIndex;
      // Serial.write(xEn);
      if (xEn) {
        stepMotor(xSign, stepperX);
      }
      if (yEn) {
        stepMotor(ySign, stepperY); //This is blocking currently
      }
      if (trigEn) {
        shoot();
      }
      if (!xEn || !yEn) { // For debugging only
        stepperY->release();
      }
      Serial.write(ySign); //send confirmation.
    }
  }
}