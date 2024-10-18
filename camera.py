import cv2
import keyboard


def moveCamera(
    frame, topLeftCoord, croppedHeight, croppedWidth, xMovement, yMovement, rotation
):
    imgHeight = frame.shape[0]
    imgWidth = frame.shape[1]

    if croppedHeight > imgHeight or croppedWidth > imgWidth:
        raise Exception("Cropped frame cannot be larger than the original frame")

    topLeftCoord[0] += yMovement
    topLeftCoord[1] += xMovement

    croppedY = topLeftCoord[0]
    croppedX = topLeftCoord[1]
    
    if croppedY < 0:
        # print("here")
        croppedY = 0
    
    if croppedX < 0:
        # print("here1")
        croppedX = 0

    if croppedY + croppedHeight >= imgHeight:
        # print("here2")
        croppedY = imgHeight - croppedHeight

    if croppedX + croppedWidth >= imgWidth:
        # print("here3")
        croppedX = imgWidth - croppedWidth

    cropped = frame[
        croppedY : (croppedY + croppedHeight), croppedX : (croppedX + croppedWidth), 0:3
    ]

    cv2.imshow("Camera", frame)
    cv2.imshow("Camera2", cropped)


# Replace 1 with whatever camera you want
cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

topLeftCoord = [0, 0]
croppedHeight = 360
croppedWidth = 720

while True:
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

    moveCamera(
        frame, topLeftCoord, croppedHeight, croppedWidth, xMovement, yMovement, rotation
    )

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


cap.release()
cv2.destroyAllWindows()
