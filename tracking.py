import SimpleCV
import math
import serial
import time

ser = serial.Serial('/dev/tty.usbmodem1411', 9600)
time.sleep(2)
display = SimpleCV.Display()
cam = SimpleCV.Camera(0, prop_set={"width":320,"height":240})
normaldisplay = True

pos = [0,0]
speed = 10

goal = (0,0)
shooting = 0
readwait = False
ser.flushInput()
ser.flushOutput()

def drawCrossHair(img, pos, size=8, color=SimpleCV.Color.BLUE):
  width = 3;
  img.drawLine((pos[0]-size, pos[1]+size), (pos[0]+size, pos[1]-size), color, width)
  img.drawLine((pos[0]+size, pos[1]+size), (pos[0]-size, pos[1]-size), color, width) 

while display.isNotDone():
 
  if display.mouseRight:
    normaldisplay = not(normaldisplay)
    print("Display Mode:", "Normal" if normaldisplay else "Segmented")
  
  img = cam.getImage().flipHorizontal()
  dist = img.colorDistance(SimpleCV.Color.RED)
  flippedDist = dist.invert()
  segmented = dist.stretch(200,255)
  blobs = flippedDist.findBlobs(threshval=180, minsize=50)
  if blobs:
    for blob in blobs:
      track = True
      img.drawCircle((blob.x, blob.y), 10, SimpleCV.Color.BLUE, 3)
      dist.drawCircle((blob.x, blob.y), 10, SimpleCV.Color.BLUE, 3)
      goal = blob.x, blob.y
      distance = math.sqrt((goal[0]-pos[0])**2+(goal[1]-pos[1])**2)
  else:
    track = False
    distance = 100
  shooting = distance < 7

  if track:
    # if not readwait:
    xEn = int(goal[0] != pos[0]) << 4
    xSign = int(goal[0] > pos[0]) << 3 #1 when positive, 0 negative
    yEn = int(goal[1] != pos[1]) << 2
    ySign = int(goal[1] > pos[1]) << 1
    t = int(shooting)
    command = xEn | xSign | yEn | ySign | t
    ser.write(chr(command)) #send command
    print "Command: ", bin(command)
    #map from [0,1] to [-1,1]
    pos[0] += speed*(2*int(goal[0] > pos[0])-1)
    pos[1] += speed*(2*int(goal[1] > pos[1])-1)
    conf = ser.read(1)
    print "response: ", ord(conf)
    
  if shooting: drawCrossHair(img, pos, size=12, color=SimpleCV.Color.GREEN)
  else: drawCrossHair(img, pos, size=8, color=SimpleCV.Color.BLACK) 

  if normaldisplay:
    img.show()
  else:
    # segmented.show()
    flippedDist.show()

ser.close();
