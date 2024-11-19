import cv2
import keyboard
import math

zRot = 0
xRot = 0
yRot = 0


def rotateY(rotationValue):
    global yRot

    yRot = rotationValue


def rotateX(rotationValue):
    global xRot

    xRot = rotationValue


def rotateZ(rotationValue):
    global zRot

    zRot = rotationValue


def getZRot():
    return zRot


def getXRot():
    return xRot


def getYRot():
    return yRot


def rotate_frame(frame, angle, origin):
    (h, w) = frame.shape[:2]

    rotMat = cv2.getRotationMatrix2D(origin, angle, 1.0)

    return cv2.warpAffine(frame, rotMat, (w, h))


def run_camera():
    cap = cv2.VideoCapture(0)
    
    maxY = 510
    maxX = 1070

    # Check if the webcam is opened correctly
    if not cap.isOpened():
        print("Error: Could not access the camera.")
        exit()

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        x, y, width, height = 500, 100, 200, 200
        
        height = min(height, frame.shape[0] - y)
        width = min(width, frame.shape[1] - x)

        global xRot
        global yRot
        global zRot

        # xRot and yRot are rotations about their respective axis therefore xRot affects the y pixels and vice versa
        
        print(xRot)
        y = round(y + 30 * math.degrees(xRot))
        x = round(x + 25 * math.degrees(yRot))
        
        x = max(0, x)
        x = min(x, maxX)
        y = max(0, y)
        y = min(y, maxY)

        # TODO: fix rotation about z axis and re-enable it
        rtFrame = rotate_frame(
            frame, math.degrees(zRot), (x + width / 2, y + height / 2)
        )
        
        cropped_frame = rtFrame[y : y + height, x : x + width]

        # this is for testing
        if keyboard.is_pressed("right arrow"):
            x += 30

        if keyboard.is_pressed("left arrow"):
            x -= 30

        if keyboard.is_pressed("up arrow"):
            y -= 30

        if keyboard.is_pressed("down arrow"):
            y += 30

        if keyboard.is_pressed("a"):
            zRot -= 10

        if cv2.waitKey(1) & 0xFF == ord("d"):
            zRot += 10

        if not ret:
            print("Error: Failed to capture frame.")
            break

        cv2.imshow("Cropped Camera Feed", cropped_frame)

        # Display the resulting frame
        cv2.imshow("Camera Feed", frame)

        # Exit when the user presses the 'ESC' key
        if cv2.waitKey(1) & 0xFF == 27:  # 27 is the ASCII value for the 'ESC' key
            break

    # Release the webcam and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()
