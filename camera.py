import cv2
import keyboard
import math
import numpy as np
from math import cos, sin


def getMidPointOfRect(rect):
    x = (rect[0][0] + rect[1][0]) / 2
    y = (rect[0][1] + rect[3][1]) / 2

    return [x, y]


def rotatePoint(pointXY, rotationRad):
    rotatedX = pointXY[0] * cos(rotationRad) - pointXY[1] * sin(rotationRad)
    rotatedY = pointXY[1] * cos(rotationRad) + pointXY[0] * sin(rotationRad)

    return [(rotatedX), (rotatedY)]


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
    for i in range(len(rectCoordsXY)):
        rectCoordsXY[i] = [
            a + b for a, b in zip(rectCoordsXY[i], [xMovement, yMovement])
        ]


def streamCroppedImg(croppedFrame, frame, rectCoordsXY, croppedHeight, croppedWidth):
    xDifference = rectCoordsXY[2][0] - rectCoordsXY[0][0]

    if xDifference == 0:
        xDifference = 0.000001

    heightGrad = (rectCoordsXY[2][1] - rectCoordsXY[0][1]) / (xDifference)

    xSign = (xDifference) / abs(xDifference)

    heightXInterval = math.sqrt(1 / (heightGrad**2 + 1)) * xSign

    heightYInterval = heightXInterval * heightGrad

    xDifference = rectCoordsXY[1][0] - rectCoordsXY[0][0]

    if xDifference == 0:
        xDifference = 0.000001

    widthGrad = (rectCoordsXY[1][1] - rectCoordsXY[0][1]) / (xDifference)

    xSign = (xDifference) / abs(xDifference)

    widthXInterval = math.sqrt(1 / (widthGrad**2 + 1)) * xSign

    widthYInterval = widthXInterval * widthGrad

    rowPoint = [rectCoordsXY[0][0], rectCoordsXY[0][1]]

    for i in range(croppedHeight):
        rowPoint[0] += heightXInterval
        rowPoint[1] += heightYInterval
        
        colPoint = [0,0]

        for j in range(croppedWidth):
            colPoint[0] += widthXInterval
            colPoint[1] += widthYInterval

            roundPoint = [round(rowPoint[0] + colPoint[0]), round(rowPoint[1] + colPoint[1])]

            # # if the pixel is within range then copy the colour else make the pixel black
            if (
                roundPoint[1] < frame.shape[0]
                and roundPoint[0] < frame.shape[1]
                and roundPoint[1] > -1
                and roundPoint[0] > -1
            ):
                croppedFrame[i][j] = frame[roundPoint[1]][roundPoint[0]]
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
    [topLeftCoord[0] + 0.000001, topLeftCoord[1]],
    [croppedWidth - 1 + topLeftCoord[0], topLeftCoord[1]],
    [topLeftCoord[0], croppedHeight - 1 + topLeftCoord[1]],
    [croppedWidth - 1 + topLeftCoord[0], croppedHeight - 1 + topLeftCoord[1]],
]

run = True
croppedFrame = np.zeros((croppedHeight, croppedWidth, 3), dtype=np.uint8)
while run:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    xMovement = 0
    yMovement = 0
    rotation = 0

    # this is for testing
    if keyboard.is_pressed("right arrow"):
        xMovement += 10

    if keyboard.is_pressed("left arrow"):
        xMovement -= 10

    if keyboard.is_pressed("up arrow"):
        yMovement -= 10

    if keyboard.is_pressed("down arrow"):
        yMovement += 10

    if keyboard.is_pressed("a"):
        rotation -= 90

    if cv2.waitKey(1) & 0xFF == ord("d"):
        rotation += 10

    rotateCamera(rectCoordsXY, rotation)

    translateCamera(rectCoordsXY, xMovement, yMovement)

    streamCroppedImg(croppedFrame, frame, rectCoordsXY, croppedHeight, croppedWidth)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
cv2.destroyAllWindows()