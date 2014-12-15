import SimpleCV
import math
import serial
import time

ser = serial.Serial('/dev/tty.usbmodem1411', 9600)
ser.flushInput()
ser.flushOutput()
time.sleep(2)
ser.write(chr(32)); #send reset to arduino

#Constants
WIDTH = 320
HEIGHT = 240

#Listen for initialization information from Arduino
frameWidthSteps = 100 #default values
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
frameHeightSteps = ord(ser.read(1))
print("Height steps: ", frameHeightSteps)

# Initialize webcam connection
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
  """
  A utility function to draw a crosshair on the laptop's webcam display
  """
  width = 3;
  img.drawLine((pos[0]-size, pos[1]+size), (pos[0]+size, pos[1]-size), color, width)
  img.drawLine((pos[0]+size, pos[1]+size), (pos[0]-size, pos[1]-size), color, width) 


# Tracking Loop
while display.isNotDone():
 
  # Switch display type on click
  if display.mouseRight:
    normaldisplay = not(normaldisplay)
    print("Display Mode:", "Normal" if normaldisplay else "Segmented")
  
  img = cam.getImage()#.flipHorizontal()
  #Get binary image with magnitude related to color distance from red
  dist = img.colorDistance(SimpleCV.Color.RED)*1.5  
  flippedDist = dist.invert()
  # blur the image a bit to aid edge finding
  flippedDist = flippedDist.blur(window=(6,6))
  # Find blobs of bright color based on edges and size
  blobs = flippedDist.findBlobs(threshval=-1, threshconstant=15, minsize=50)
  track = False
  distance = 100
  if blobs:
    for blob in blobs:
      # Find all blobs that are close to circular
      if blob.isCircle(tolerance=.20):
        track = True
        # Draw circular labels on targets
        img.drawCircle((blob.x, blob.y), 10, SimpleCV.Color.BLUE, 3)
        dist.drawCircle((blob.x, blob.y), 10, SimpleCV.Color.BLUE, 3)
        # Set new goal and find distance from current position
        goal = blob.x, blob.y
        distance = math.sqrt((goal[0]-pos[0])**2+(goal[1]-pos[1])**2)

  # If within 7 pixels, begin shooting
  shooting = distance < 7

  # If a target is being tracked, send commands
  if track:
    # Encode command as 5 bits: X enable, X direction, Y enable, Y direction, trigger enable
    xEn = int(goal[0] != pos[0]) << 4
    xSign = int(goal[0] > pos[0]) << 3
    yEn = int(goal[1] != pos[1]) << 2
    ySign = int(goal[1] > pos[1]) << 1
    t = int(shooting)
    command = xEn | xSign | yEn | ySign | t
    ser.write(chr(command)) #send hex equivalent of 5 bit command
    print "Command: ", bin(command)
    # map from [0,1] to [-1,1] and change stored position
    pos[0] += xSpeed*(2*int(goal[0] > pos[0])-1)
    pos[1] += ySpeed*(2*int(goal[1] > pos[1])-1)
    # Wait for confirmation message before continuing
    conf = ser.read(1)
    time.sleep(0.5)
    
  # Draw cross hair at current position with color changing for trigger status
  if shooting: drawCrossHair(img, pos, size=12, color=SimpleCV.Color.GREEN)
  else: drawCrossHair(img, pos, size=8, color=SimpleCV.Color.BLACK) 

  # Show annotated webcam display
  if normaldisplay:
    img.show()
  else:
    flippedDist.show()

ser.close();