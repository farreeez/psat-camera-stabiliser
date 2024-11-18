import cv2
import numpy as np
import keyboard
import threading
import socket
import json
import matplotlib.pyplot as plt
import improvedCamera
from datetime import datetime, timedelta
from matplotlib.animation import FuncAnimation

rotationAngle = 0
# xMovement = 0
# yMovement = 0


# def rotateY(rotationValue):
#     global xMovement
    
#     xMovement += rotationValue
    
# def rotateX(rotationValue):
#     global yMovement
    
#     yMovement += rotationValue
    
# def rotateZ(rotationValue):
#     global rotationAngle
    
#     rotationAngle += rotationValue

def rotate_frame(frame, angle, origin):
    (h, w) = frame.shape[:2]

    rotMat = cv2.getRotationMatrix2D(origin, angle, 1.0)

    return cv2.warpAffine(frame, rotMat, (w, h))


def translate_frame(frame, tx, ty):
    tMatrix = np.float32([[1, 0, tx], [0, 1, ty]])
    
    (h, w) = frame.shape[:2]

    return cv2.warpAffine(frame, tMatrix, (w, h))


def run_camera():
    cap = cv2.VideoCapture(0)

    # Check if the webcam is opened correctly
    if not cap.isOpened():
        print("Error: Could not access the camera.")
        exit()
        
    x, y, width, height = 100, 100, 200, 200


    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        
        height = min(height, frame.shape[0] - y)
        width = min(width, frame.shape[1] - x)
        
        global rotationAngle
        
        # tFrame = translate_frame(frame, xMovement, yMovement)
        
        rtFrame = rotate_frame(frame, rotationAngle, (x + width/2, y + height/2))
        
        cropped_frame = rtFrame[y:y + height, x:x + width]
        
        # this is for testing
        if keyboard.is_pressed("right arrow"):
            x += 10

        if keyboard.is_pressed("left arrow"):
            x -= 10

        if keyboard.is_pressed("up arrow"):
            y -= 10

        if keyboard.is_pressed("down arrow"):
            y += 10
            
        if keyboard.is_pressed("a"):
            rotationAngle -= 10

        if cv2.waitKey(1) & 0xFF == ord("d"):
            rotationAngle += 10    
        
        if not ret:
            print("Error: Failed to capture frame.")
            break
        
        cv2.imshow('Cropped Camera Feed', cropped_frame)
        
        # Display the resulting frame
        cv2.imshow('Camera Feed', frame)
        
        # Exit when the user presses the 'ESC' key
        if cv2.waitKey(1) & 0xFF == 27:  # 27 is the ASCII value for the 'ESC' key
            break

    # Release the webcam and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()