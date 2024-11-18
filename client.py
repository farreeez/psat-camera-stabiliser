import threading
import socket
import json
import matplotlib.pyplot as plt
import improvedCamera
import math
from datetime import datetime, timedelta

"""
This is a client TCP socket that receives gyroscope data from my phone.
The server socket is run on an android phone using this app https://github.com/yaqwsx/SensorStreamer.
"""
HOST = "192.168.1.67"  # The server's hostname or IP address
PORT = 65002  # The port used by the server


def saveJson(jsonCharArr, jsonArray):
    try:
        jsonString = "".join(jsonCharArr)

        jsonObject = json.loads(jsonString)

        gyroData = jsonObject["gyroscope"]["value"]
        accelData = jsonObject["accelerometer"]["value"]

        oldData = []

        calculateAgnle = False

        if jsonArray and all(jsonArray):
            oldData = [row[-1] for row in jsonArray]
            calculateAgnle = True

        improvedCamera.rotateZ(gyroData[2])

        jsonArray[0].append(gyroData[0])
        jsonArray[1].append(gyroData[1])
        jsonArray[2].append(gyroData[2])
        jsonArray[3].append(accelData[0])
        jsonArray[4].append(accelData[1])
        jsonArray[5].append(accelData[2])

        timestamp_ns = jsonObject["gyroscope"]["timestamp"]

        # Convert to seconds
        timestamp_s = timestamp_ns / 1_000_000_000

        jsonArray[6].append(timestamp_s)

        if calculateAgnle:
            timeDiff = timestamp_s - oldData[6]
            
            gyroRotX = timeDiff * (jsonArray[0][-1] + oldData[0]) / 2
            gyroRotY = timeDiff * (jsonArray[1][-1] + oldData[1]) / 2
            gyroRotZ = timeDiff * (jsonArray[2][-1] + oldData[2]) / 2

            accelRotX = math.atan(
                accelData[1] / (accelData[0] ** 2 + accelData[2] ** 2)
            )
            
            accelRotY = math.atan(
                accelData[0] / (math.sqrt(accelData[1] ** 2 + accelData[2] ** 2))
            )

    except json.JSONDecodeError:
        print("fail")
        pass


thread = threading.Thread(target=improvedCamera.run_camera)

# thread.start()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # connects to the phone's server socket
    s.connect((HOST, PORT))

    # initialises the array that will hold the gyroscope data. First element is an array holding x rotational data. Second is y rotational data
    # Third is z rotational data. Fourth holds the time stamps
    dataArray = [[], [], [], [], [], [], []]

    plt.ion()  # Turn on interactive mode
    fig, ax = plt.subplots()

    (line1,) = ax.plot([], [], color="red", label="rotation about x")  # First line
    (line2,) = ax.plot([], [], color="blue", label="rotation about y")  # Second line
    (line3,) = ax.plot([], [], color="green", label="rotation about z")  # Third line

    ax.set_xlabel("Time")
    ax.set_ylabel("gyro-data")
    ax.set_title("real time gyro data")
    ax.legend()

    while True:
        data = s.recv(1024).decode("utf-8")
        # parsed_data = json.loads(data)
        count = 0
        jsonCharArr = []

        counter = 0

        # The data received consists of a string that contains multiple json objects
        # Therefore this loop is needed to break down that string into singular json strings that get parsed later on
        for char in data:
            if char == "\n":
                continue
            if char == "{":
                counter += 1

            if counter == 4:
                saveJson(jsonCharArr, dataArray)
                jsonCharArr = ["{"]
                counter = 1
            else:
                jsonCharArr.append(char)

        saveJson(jsonCharArr, dataArray)

        line1.set_xdata(dataArray[6])
        line2.set_xdata(dataArray[6])
        line3.set_xdata(dataArray[6])

        line1.set_ydata(dataArray[3])
        line2.set_ydata(dataArray[4])
        line3.set_ydata(dataArray[5])

        ax.relim()  # Recalculate limits
        ax.autoscale_view()  # Autoscale the view

        plt.draw()
        plt.pause(0.01)
