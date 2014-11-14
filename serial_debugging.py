import serial
ser = serial.Serial('/dev/tty.usbmodem1411', 9600)
com = ''
while com != "done":
  ser.flushInput()
  com = raw_input(">>")
  ser.write(chr(int(com)))
  conf = ser.read(1)
  print ord(conf)
