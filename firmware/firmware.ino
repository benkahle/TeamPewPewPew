// Include necessary modules for Adafruit motor shield
#include <Wire.h>
#include <Adafruit_MotorShield.h>
#include <avr/wdt.h>
#include "utility/Adafruit_PWMServoDriver.h"

// Create the motor shield object with the default I2C address
Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 
Adafruit_StepperMotor *stepperY = AFMS.getStepper(48, 1); // Motor 1 L/R BYGR
Adafruit_StepperMotor *stepperX = AFMS.getStepper(48, 2); // Motor 2 L/R BYGR

//Pin numbers
const int safePin = 4;
const int xPosLimitPin = 5;
const int xNegLimitPin = 6;
const int yPosLimitPin = 7;
const int yNegLimitPin = 8; 
const int stepsPerCommand = 10;

const int xEnIndex = 4;
const int xSignIndex = 3;
const int yEnIndex = 2;
const int ySignIndex = 1;
const int trigEnIndex = 0;

int safe = 0;
int resetIndex = 5;
int frameWidth = 0;
int frameHeight = 0;

void setup() {
  MCUSR = 0;  // clear out any flags of prior resets.
  Serial.begin(9600);
  AFMS.begin();
  stepperX->setSpeed(120);
  stepperY->setSpeed(120);
  pinMode(safePin, INPUT);
  pinMode(4, INPUT);
  pinMode(5, INPUT);
  pinMode(6, INPUT);
  pinMode(7, INPUT);
  pinMode(8, INPUT);
  initialize();
}

// Motor command function wrapper
void stepMotor(int stepSign, Adafruit_StepperMotor* stepper) {
  stepper->step(stepsPerCommand, stepSign, SINGLE);
}

void shoot() {

}

// Initialization routine run on startup 
void initialize() {
  int xPosLimit = !digitalRead(xPosLimitPin);
  int xNegLimit = !digitalRead(xNegLimitPin);
  int yPosLimit = !digitalRead(yPosLimitPin);
  int yNegLimit = !digitalRead(yNegLimitPin);
  int xPosHit = 0;
  int xNegHit = 0;
  int yPosHit = 0;
  int yNegHit = 0;

  while (!xPosHit) {
    xPosLimit = !digitalRead(xPosLimitPin);
    if (xPosLimit) xPosHit = 1;
    stepMotor(1, stepperX);
    delay(200);
  }
  while (!yPosHit) {
    yPosLimit = !digitalRead(yPosLimitPin);
    if (yPosLimit) yPosHit = 1;
    stepMotor(1, stepperY);
    delay(50);
  }
  while (!xNegHit) {
    xNegLimit = !digitalRead(xNegLimitPin);
    if (xNegLimit) xNegHit = 1;
    stepMotor(0, stepperX);
    frameWidth++;
    delay(200);
  }
  while (!yNegHit) {
    yNegLimit = !digitalRead(yNegLimitPin);
    if (yNegLimit) yNegHit = 1;
    stepMotor(0, stepperY);
    frameHeight++;
    delay(50);
  }
  Serial.write((byte)0); // Serial Sync message
  Serial.write((byte)255);
  Serial.write((byte)0);
  Serial.write((byte)255);
  byte fw = byte(frameWidth);
  Serial.write(fw);

  stepperX->step(0,0,SINGLE);
  stepperY->step(0,0,SINGLE);

  byte fh = byte(frameHeight);
  Serial.write(fh);

  stepperX->release();
  stepperY->release();
}

void loop() {
  // safe = digitalRead(safePin);
  // stepMotor(50, stepperY); 
  // delay(50);
  safe = 1;
  if (safe) {
    if (Serial.available() > 0) {
      byte command = 0x00;
      command = Serial.read();
      int reset = (command & (1 << resetIndex)) >> resetIndex;
      int xEn = (command & (1 << xEnIndex)) >> xEnIndex;
      int xSign = (command & (1 << xSignIndex)) >> xSignIndex;
      int yEn = (command & (1 << yEnIndex)) >> yEnIndex;
      int ySign = (command & (1 << ySignIndex)) >> ySignIndex;
      int trigEn = (command & (1 << trigEnIndex)) >> trigEnIndex;
      if (reset) {
        wdt_enable(WDTO_15MS); // turn on the WatchDog
        for(;;) { 
          // do nothing and wait for the reset...
        } 
      }
      if (xEn) {
        stepMotor(xSign, stepperX);
      }
      if (yEn) {
        stepMotor(ySign, stepperY);
      }
      if (trigEn) {
        shoot();
      }
      // if (!xEn || !yEn) { // For debugging only
      //   stepperY->release();
      // }
      Serial.write(command); //send confirmation.
    }
  }
}