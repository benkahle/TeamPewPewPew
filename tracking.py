import SimpleCV
import math
import serial
import time

ser = serial.Serial('COM3', 9600, timeout=0)
time.sleep(2)
display = SimpleCV.Display()
cam = SimpleCV.Camera(0, prop_set={"width":320,"height":240})
normaldisplay = True

pos = (0,0)
speed = 1

goal = (0,0)
shooting = 0

def drawCrossHair(img, pos, size=8, color=SimpleCV.Color.BLUE):
  width = 3;
  img.drawLine((pos[0]-size, pos[1]+size), (pos[0]+size, pos[1]-size), color, width)
  img.drawLine((pos[0]+size, pos[1]+size), (pos[0]-size, pos[1]-size), color, width) 

def goalVector(pos, goal):
  x = goal[0]-pos[0]
  y = goal[1]-pos[1]
  return x,y

def normalizeVector(vec):
  if abs(vec[0]) > abs(vec[1]):
    div = abs(vec[0])
  else:
    div = abs(vec[1])
  if div == 0:
    return vec
  x = float(vec[0])/div
  y = float(vec[1])/div
  return x,y

def magnitude(vec):
  return math.sqrt(vec[0]**2+vec[1]**2)

def scaleVector(vec, scale):
  return vec[0]*scale, vec[1]*scale

def addVectors(a, b):
  return a[0]+b[0],a[1]+b[1]

def sendCommand(step, distance):
  global shooting
  command = [step[0], step[1], 0]
  if distance < 5: shooting = 1
  else: shooting = 0
  command[2] = shooting
  print command

def moveToGoal(pos, goal):
  vector = goalVector(pos, goal)
  norm = normalizeVector(vector)
  step = scaleVector(norm, speed)
  newPos = addVectors(pos, step)
  distance = magnitude(vector)
  sendCommand(step, distance)
  return newPos

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
      goal = blob.x, blob.y
  else:
    track = False
      # flippedDist.drawCircle((blob.x, blob.y), 10, SimpleCV.Color.BLUE, 3)
    # circles = blobs.filter([b.isCircle(0.2) for b in blobs])
    # if circles:x
      # img.drawCircle((circles[-1].x, circles[-1].y), circles[-1].radius(),SimpleCV.Color.RED,3)
  if track:
    pos = moveToGoal(pos, goal)
    xEn = int(goal[0] != pos[0]) << 4
    xSign = int(goal[0] > pos[0]) << 3 #1 when positive, 0 negative
    yEn = int(goal[1] > pos[1]) << 2
    ySign = int(goal[1] > pos[1]) << 1
    t = int(shooting)
    command = xEn | xSign | yEn | ySign | t
    ser.write(command); #send command

  if shooting: drawCrossHair(img, pos, size=12, color=SimpleCV.Color.GREEN)
  else: drawCrossHair(img, pos, size=8, color=SimpleCV.Color.BLACK) 

  if normaldisplay:
    img.show()
  else:
    # segmented.show()
    flippedDist.show()

ser.close();