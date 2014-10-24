import SimpleCV
 
display = SimpleCV.Display()
cam = SimpleCV.Camera(prop_set={"width":320,"height":240})
normaldisplay = True
 
while display.isNotDone():
 
  if display.mouseRight:
    normaldisplay = not(normaldisplay)
    print("Display Mode:", "Normal" if normaldisplay else "Segmented")
  
  img = cam.getImage().flipHorizontal()
  dist = img.colorDistance(SimpleCV.Color.ROYALBLUE).dilate(3)
  flippedDist = dist.invert()
  segmented = dist.stretch(200,255)
  blobs = flippedDist.findBlobs(threshval=180, minsize=8, maxsize=80)
  if blobs:
    for blob in blobs:
      img.drawCircle((blob.x, blob.y), 10, SimpleCV.Color.RED, 3)
      dist.drawCircle((blob.x, blob.y), 10, SimpleCV.Color.RED, 3)
    # circles = blobs.filter([b.isCircle(0.2) for b in blobs])
    # if circles:
      # img.drawCircle((circles[-1].x, circles[-1].y), circles[-1].radius(),SimpleCV.Color.RED,3)
 
  if normaldisplay:
    img.show()
  else:
    # segmented.show()
    flippedDist.show()