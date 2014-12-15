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
const int triggerFirePin = 9;
const int triggerReleasePin = 10;
const int activatePin = 13;
const int yStepsPerCommand = 6;
const int xStepsPerCommand = 20;

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
  stepperX->setSpeed(80);
  stepperY->setSpeed(50);
  pinMode(safePin, INPUT);
  pinMode(xPosLimitPin, INPUT);
  pinMode(xNegLimitPin, INPUT);
  pinMode(yPosLimitPin, INPUT);
  pinMode(yNegLimitPin, INPUT);
  pinMode(triggerFirePin, OUTPUT);
  pinMode(triggerReleasePin, OUTPUT);
  pinMode(activatePin, INPUT);
  int safeToGo = digitalRead(activatePin);
  if (safeToGo) {
    initialize();
  }
}

// Motor command function wrapper
void stepMotor(int stepSign, Adafruit_StepperMotor* stepper) {
  if (stepper == stepperY) {
    stepper->step(yStepsPerCommand, stepSign, DOUBLE);
  }
  if (stepper == stepperX) {
    stepper->step(xStepsPerCommand, stepSign, DOUBLE);
  }
}

void shoot() {
  digitalWrite(triggerReleasePin, 0);
  digitalWrite(triggerFirePin, 1);
  delay(500);
  digitalWrite(triggerFirePin, 0);
  digitalWrite(triggerReleasePin, 1);
  delay(250);
  digitalWrite(triggerReleasePin, 0);
  delay(100);
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
    delay(50);
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
    delay(50);
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
  byte fh = byte(frameHeight);
  Serial.write(fh);

  // stepperX->step(0,0,SINGLE);
  // stepperY->step(0,0,SINGLE);


  //Center Shot
  // movePercent(50, stepperY);
  // movePercent(50, stepperX);
  // shoot();
  // shoot();

  //Top Left - Center - Bottom Right
  movePercent(35, stepperY);
  movePercent(35, stepperX);
  shoot();
  // delay(5000);
  movePercent(12, stepperY);
  movePercent(15, stepperX);
  shoot();
  // delay(5000);
  movePercent(10, stepperY);
  movePercent(15, stepperX);
  shoot();
  // delay(5000);

  stepperX->release();
  stepperY->release();
}

void movePercent(int percent, Adafruit_StepperMotor* stepper) {
  int dir;
  int steps;
  if (percent > 0) {
    dir = 1;
  } else {
    dir = 0;
  }
  if (stepper == stepperY) {
    steps = (int)frameHeight/(100/(float)abs(percent));
  } else {
    steps = (int)frameWidth/(100/(float)abs(percent));
  }
  for (int k = 0; k < steps; k++) {
    stepMotor(dir, stepper);
  }
}

void loop() {
  safe = digitalRead(safePin);
  // safe = 1;
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