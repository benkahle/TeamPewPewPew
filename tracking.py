import SimpleCV
import math
import serial
import time

ser = serial.Serial('/dev/tty.usbmodem1411', 9600)
ser.flushInput()
ser.flushOutput()
time.sleep(2)
ser.write(chr(32)); #send reset to arduino

WIDTH = 320
HEIGHT = 240
frameWidthSteps = 100
frameHeightSteps = 100
waiting = True
ms = []
startingMs = [0,255,0,255]
while waiting:
  m = ser.read(1)
  print(ord(m))
  ms.append(ord(m))
  if len(ms) == 4:
    if ms == startingMs:
      waiting = False
    else:
      ms.pop(0)

frameWidthSteps = ord(ser.read(1))
print("Width steps: ", frameWidthSteps)
# frameHeightSteps = int(ser.read(1))

display = SimpleCV.Display()
cam = SimpleCV.Camera(0, prop_set={"width":WIDTH,"height":HEIGHT})
normaldisplay = True

xSpeed = WIDTH/frameWidthSteps
ySpeed = HEIGHT/frameHeightSteps

pos = [0,HEIGHT] #Initlization ends bottom-left (?)
# pos = [WIDTH/2, HEIGHT/2]
goal = (0,0)
shooting = 0
initialized = False

def drawCrossHair(img, pos, size=8, color=SimpleCV.Color.BLUE):
  width = 3;
  img.drawLine((pos[0]-size, pos[1]+size), (pos[0]+size, pos[1]-size), color, width)
  img.drawLine((pos[0]+size, pos[1]+size), (pos[0]-size, pos[1]-size), color, width) 

while display.isNotDone():
 
  if display.mouseRight:
    normaldisplay = not(normaldisplay)
    print("Display Mode:", "Normal" if normaldisplay else "Segmented")
  
  img = cam.getImage().flipHorizontal()
  dist = img.colorDistance(SimpleCV.Color.RED)*1.5
  flippedDist = dist.invert()
  flippedDist = flippedDist.blur(window=(6,6))
  blobs = flippedDist.findBlobs(threshval=-1, threshconstant=15, minsize=50)
  track = False
  distance = 100
  if blobs:
    for blob in blobs:
      if blob.isCircle(tolerance=.20):
        track = True
        img.drawCircle((blob.x, blob.y), 10, SimpleCV.Color.BLUE, 3)
        dist.drawCircle((blob.x, blob.y), 10, SimpleCV.Color.BLUE, 3)
        goal = blob.x, blob.y
        distance = math.sqrt((goal[0]-pos[0])**2+(goal[1]-pos[1])**2)
 
  shooting = distance < 7

  if track:
    xEn = int(goal[0] != pos[0]) << 4
    xSign = int(goal[0] > pos[0]) << 3
    yEn = int(goal[1] != pos[1]) << 2
    ySign = int(goal[1] > pos[1]) << 1
    t = int(shooting)
    command = xEn | xSign | yEn | ySign | t
    ser.write(chr(command)) #send command
    print "Command: ", bin(command)
    #map from [0,1] to [-1,1]
    pos[0] += xSpeed*(2*int(goal[0] > pos[0])-1)
    pos[1] += ySpeed*(2*int(goal[1] > pos[1])-1)
    conf = ser.read(1)
    # print "response: ", ord(conf)
    
  if shooting: drawCrossHair(img, pos, size=12, color=SimpleCV.Color.GREEN)
  else: drawCrossHair(img, pos, size=8, color=SimpleCV.Color.BLACK) 

  if normaldisplay:
    img.show()
  else:
    # segmented.show()
    flippedDist.show()

ser.close();
