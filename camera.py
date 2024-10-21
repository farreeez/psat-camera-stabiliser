import cv2
import keyboard
import math
import numpy as np
from math import cos, sin


def getMidPointOfRect(rect):
    x = round((rect[0][0] + rect[1][0]) / 2)
    y = round((rect[0][1] + rect[3][1]) / 2)

    return [x, y]


def rotatePoint(pointXY, rotationRad):
    rotatedX = pointXY[0] * cos(rotationRad) - pointXY[1] * sin(rotationRad)
    rotatedY = pointXY[1] * cos(rotationRad) + pointXY[0] * sin(rotationRad)

    return [round(rotatedX), round(rotatedY)]


# for the angle counter clock wise is positive
def rotateCamera(rectCoordsXY, rotationDeg):
    rotationRad = math.radians(rotationDeg)
    midPoint = getMidPointOfRect(rectCoordsXY)

    # make the midpoint the origin
    for i in range(len(rectCoordsXY)):
        rectCoordsXY[i] = [a - b for a, b in zip(rectCoordsXY[i], midPoint)]

    # rotate the corners of the rectangle about the origin
    for i in range(len(rectCoordsXY)):
        rectCoordsXY[i] = rotatePoint(rectCoordsXY[i], rotationRad)

    # return to the normal origin
    for i in range(len(rectCoordsXY)):
        rectCoordsXY[i] = [a + b for a, b in zip(rectCoordsXY[i], midPoint)]


def translateCamera(rectCoordsXY, xMovement, yMovement):
    # unsure if this is needed
    # rotatedMovement = rotatePoint([xMovement, yMovement], math.radians(rotationDeg))

    for i in range(len(rectCoordsXY)):
        rectCoordsXY[i] = [
            a + b for a, b in zip(rectCoordsXY[i], [xMovement, yMovement])
        ]


def streamCroppedImg(croppedFrame, frame, rectCoordsXY, croppedHeight, croppedWidth):
    heightInterval = (rectCoordsXY[2][1] - rectCoordsXY[0][1]) / croppedHeight
    widthInterval = (rectCoordsXY[1][0] - rectCoordsXY[0][0]) / croppedWidth

    for i in range(croppedHeight):
        row = round(rectCoordsXY[0][1] + heightInterval * i)
        for j in range(croppedWidth):
            col = round(rectCoordsXY[0][0] + widthInterval * j)

            # if the pixel is within range then copy the colour else make the pixel black
            if row < frame.shape[0] and col < frame.shape[1] and row > -1 and col > -1:
                croppedFrame[i][j] = frame[row][col]
            else:
                croppedFrame[i][j] = 0

    cv2.imshow("Camera", frame)
    cv2.imshow("Camera2", croppedFrame)


# Replace 1 with whatever camera you want
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

croppedHeight = 100
croppedWidth = 100

cap.set(cv2.CAP_PROP_FRAME_WIDTH, croppedWidth)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, croppedHeight)


currentRotation = 0

topLeftCoord = [200, 150]

# order of corner coords: left to right top to bottom (width is the first element and height is the second element opposite the array notation)
rectCoordsXY = [
    [topLeftCoord[0], topLeftCoord[1]],
    [croppedWidth - 1 + topLeftCoord[0], topLeftCoord[1]],
    [topLeftCoord[0], croppedHeight - 1 + topLeftCoord[1]],
    [croppedWidth - 1 + topLeftCoord[0], croppedHeight - 1 + topLeftCoord[1]],
]

test = [[-1,1], [1,1], [-1,-1], [1,-1]]

rotateCamera(rectCoordsXY=test, rotationDeg=40)

# translateCamera(test, 1, 0, 90)

print(test)

run = False
croppedFrame = np.zeros((croppedHeight, croppedWidth, 3), dtype=np.uint8)

while run:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    xMovement = 0
    yMovement = 0
    rotation = 0

    if keyboard.is_pressed("right arrow"):
        xMovement += 10

    if keyboard.is_pressed("left arrow"):
        xMovement -= 10

    if keyboard.is_pressed("up arrow"):
        yMovement -= 10

    if keyboard.is_pressed("down arrow"):
        yMovement += 10
        
    if keyboard.is_pressed("a"):
        rotation -= 10
    
    if keyboard.is_pressed("d"):
        rotation += 10
        
    rotateCamera(rectCoordsXY, rotation)
        
    translateCamera(rectCoordsXY, xMovement, yMovement)

    streamCroppedImg(croppedFrame, frame, rectCoordsXY, croppedHeight, croppedWidth)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
cv2.destroyAllWindows()


# def moveCamera(
#     frame, topLeftCoord, croppedHeight, croppedWidth, xMovement, yMovement, rotation
# ):
#     imgHeight = frame.shape[0]
#     imgWidth = frame.shape[1]

#     if croppedHeight > imgHeight or croppedWidth > imgWidth:
#         raise Exception("Cropped frame cannot be larger than the original frame")

#     topLeftCoord[0] += yMovement
#     topLeftCoord[1] += xMovement

#     croppedY = topLeftCoord[0]
#     croppedX = topLeftCoord[1]

#     if croppedY < 0:
#         croppedY = 0

#     if croppedX < 0:
#         croppedX = 0

#     if croppedY + croppedHeight >= imgHeight:
#         croppedY = imgHeight - croppedHeight

#     if croppedX + croppedWidth >= imgWidth:
#         croppedX = imgWidth - croppedWidth

#     cropped = frame[
# croppedY : (croppedY + croppedHeight), croppedX : (croppedX + croppedWidth), 0:3
#     ]

#     cv2.imshow("Camera", frame)
#     cv2.imshow("Camera2", cropped)
