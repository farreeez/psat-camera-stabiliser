import cv2
import keyboard
import math
from math import cos, sin


def getMidPointOfRect(rect):
    x = round((rect[0][0] + rect[1][0]) / 2)
    y = round((rect[0][1] + rect[3][1]) / 2)

    return [x, y]


# for the angle counter clock wise is positive
def rotate(rectCoordsXY, rotationDeg):
    rotationDeg = math.radians(rotationDeg)
    midPoint = getMidPointOfRect(rectCoordsXY)

    # make the midpoint the origin
    for i in range(len(rectCoordsXY)):
        rectCoordsXY[i] = [a - b for a, b in zip(rectCoordsXY[i], midPoint)]

    # rotate the corners of the rectangle about the origin
    for i in range(len(rectCoordsXY)):
        rotatedX = rectCoordsXY[i][0] * cos(rotationDeg) - rectCoordsXY[i][1] * sin(
            rotationDeg
        )
        rotatedY = rectCoordsXY[i][1] * cos(rotationDeg) + rectCoordsXY[i][0] * sin(
            rotationDeg
        )

        rectCoordsXY[i][0] = round(rotatedX)
        rectCoordsXY[i][1] = round(rotatedY)

    # return to the normal origin
    for i in range(len(rectCoordsXY)):
        rectCoordsXY[i] = [a + b for a, b in zip(rectCoordsXY[i], midPoint)]


def moveCamera(frame, croppedFrame, xMovement, yMovement, rotation):
    pass


# Replace 1 with whatever camera you want
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

croppedHeight = 360
croppedWidth = 720
currentRotation = 0

# order of corner coords: left to right top to bottom (width is the first element and height is the second element opposite the array notation)
rectCoordsXY = [
    [0, 0],
    [croppedWidth - 1, 0],
    [0, croppedHeight - 1],
    [croppedWidth - 1, croppedHeight - 1],
]

test = [[-1, 1], [1, 1], [-1, -1], [1, -1]]

rotate(rectCoordsXY=test, rotationDeg=90)

print(test)

run = False

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

    croppedFrame = frame[0 : (0 + croppedHeight), 0 : (0 + croppedWidth), 0:3]

    # moveCamera(
    #     frame, topLeftCoord, croppedHeight, croppedWidth, xMovement, yMovement, rotation
    # )

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
