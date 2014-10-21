import serial
import time
import math

def main():
    """This is a PySerial testing function. In combination with the
    associated Arduino file pyserial_demo.ino, it takes a user-input
    integer speed between -255 and 255, then commands a DC motor to 
    move at that speed."""
    #initialize serial object (i.e. the arduino)
    ser = serial.Serial('COM3',9600,timeout=0)
    time.sleep(2) #you must allow 2s for arduino reset
    print ser.read(64) #should print "Initialized!"

    #user input for the motor speed
    motorspeed = raw_input("I want the motor to move at speed ")
    try:
        checkval = int(motorspeed) #if not int-able, exception
        if checkval > 255:
            motorspeed = "255" #don't exceed max speed
        elif checkval < -255:
            motorspeed = "-255" #don't exceed(?) min speed
        #send the motorspeed to the arduino program via serial port
        ser.write(motorspeed)
    except ValueError:
        print "Quit screwing around and type in an integer."

    ser.close() #do this to be clean, before the program ends

if __name__ == "__main__":
    main()
