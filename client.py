import threading
import socket
import json
import matplotlib.pyplot as plt
import improvedCamera
import math
import time

"""
This is a client TCP socket that receives gyroscope data from my phone.
The server socket is run on an android phone using this app https://github.com/yaqwsx/SensorStreamer.
"""
HOST = "192.168.1.67"  # The server's hostname or IP address
PORT = 65002  # The port used by the server


totGyroX = 0
totGyroY = 0
totGyroZ = 0


def saveJson(jsonCharArr, jsonArray, rotationArray):
    try:
        jsonString = "".join(jsonCharArr)

        jsonObject = json.loads(jsonString)

        gyroData = jsonObject["gyroscope"]["value"]
        accelData = jsonObject["accelerometer"]["value"]

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

        if jsonArray and all(jsonArray):
            # sets weights for complementary filter
            gyroWeight = 1
            accelWeight = 1 - gyroWeight
    
            maxCol = len(jsonArray[0]) - 1
            
            # gets the time taken for the measurement to occur
            timeDiff = timestamp_s - jsonArray[6][maxCol - 1]
            
            # calculates the gyroscope rotation angles over that time step
            gyroRotX = timeDiff * (jsonArray[0][maxCol] + jsonArray[0][maxCol - 1]) / 2
            gyroRotY = timeDiff * (jsonArray[1][maxCol] + jsonArray[1][maxCol - 1]) / 2
            gyroRotZ = timeDiff * (jsonArray[2][maxCol] + jsonArray[2][maxCol - 1]) / 2
            
            global totGyroX
            global totGyroY
            global totGyroZ
            
            totGyroX += gyroRotX
            totGyroY += gyroRotY
            totGyroZ += gyroRotZ
            
            # adds past rotation data onto the new step to get the total rotation over time
            gyroRotX += improvedCamera.getXRot()
            gyroRotY += improvedCamera.getYRot()
            
            # calculates the acceleration rotation angles from the accelerometer data
            accelRotX = math.atan(
                accelData[1] / (accelData[0] ** 2 + accelData[2] ** 2)
            )
            
            accelRotY = math.atan(
                accelData[0] / (math.sqrt(accelData[1] ** 2 + accelData[2] ** 2))
            )
            
            # gets the weighted value of the gyro data
            weightedGyroRotX = gyroRotX * gyroWeight
            weightedGyroRotY = gyroRotY * gyroWeight
            
            # gets the weighted value of the accelerometer rotation
            weightedAccelRotX = accelRotX * accelWeight
            weightedAccelRotY = accelRotY * accelWeight
            
            # gets the total rotation by summing both values
            totRotX = weightedAccelRotX + weightedGyroRotX
            totRotY = weightedAccelRotY + weightedGyroRotY
            
            # rotationArray[0].append(totGyroX)
            # rotationArray[1].append(totGyroY)
            # rotationArray[2].append(accelRotX)
            # rotationArray[3].append(accelRotY)
            # rotationArray[4].append(totRotX)
            # rotationArray[5].append(totRotY)
            # rotationArray[6].append(timestamp_ns)
            
            # sets the total rotation up to this step to the calculated values for it to be then used later
            improvedCamera.rotateX(totRotX)
            improvedCamera.rotateY(totRotY)
            improvedCamera.rotateZ(totGyroZ)

    except json.JSONDecodeError:
        print("fail")
        pass


thread = threading.Thread(target=improvedCamera.run_camera)

thread.start()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # connects to the phone's server socket
    s.connect((HOST, PORT))

    # initialises the array that will hold the gyroscope data. First element is an array holding x rotational data. Second is y rotational data
    # Third is z rotational data. Fourth holds the time stamps
    dataArray = [[], [], [], [], [], [], []]
    rotationArray = [[], [], [], [], [], [], []]

    # plt.ion()  # Turn on interactive mode
    # fig, ax = plt.subplots()

    # (line1,) = ax.plot([], [], color="red", label="gyro rotation about x")  # First line
    # (line2,) = ax.plot([], [], color="blue", label="gyro rotation about y")  # Second line
    # (line3,) = ax.plot([], [], color="green", label="accel rotation about x")  # Third line
    # (line4,) = ax.plot([], [], color="grey", label="accel rotation about y")  # Third line

    # ax.set_xlabel("Time")
    # ax.set_ylabel("accel-data")
    # ax.set_title("real time accel data")
    # ax.legend()
    
    # fig1, ax1 = plt.subplots()

    # (line11,) = ax1.plot([], [], color="red", label="rotation about x")  # First line
    # (line21,) = ax1.plot([], [], color="blue", label="rotation about y")  # Second line

    # ax1.set_xlabel("Time")
    # ax1.set_ylabel("gyro-data")
    # ax1.set_title("real time gyro data")
    # ax1.legend()
    
    previous_time = time.time()  # Record the initial time
    total_time = 0  # Accumulate time differences
    iteration_count = 0  # Count iterations

    while True:
        data = s.recv(1024).decode("utf-8")
        
        # current_time = time.time()  # Get the current time
    
        # # Calculate the time difference
        # time_diff = current_time - previous_time
        # total_time += time_diff  # Update total time
        # iteration_count += 1  # Increment iteration count
        
        # # Calculate and print the average time difference
        # average_time = total_time / iteration_count
        # print(f"Iteration {iteration_count}: Time diff = {time_diff:.6f} s, Average = {average_time:.6f} s")
        
        # # Update the previous_time for the next iteration
        # previous_time = current_time
        
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
                saveJson(jsonCharArr, dataArray, rotationArray)
                jsonCharArr = ["{"]
                counter = 1
            else:
                jsonCharArr.append(char)

        saveJson(jsonCharArr, dataArray, rotationArray)

        # line1.set_xdata(rotationArray[6])
        # line2.set_xdata(rotationArray[6])
        # line3.set_xdata(rotationArray[6])
        # line4.set_xdata(rotationArray[6])

        # line1.set_ydata(rotationArray[0])
        # line2.set_ydata(rotationArray[1])
        # line3.set_ydata(rotationArray[2])
        # line4.set_ydata(rotationArray[3])

        # ax.relim()  # Recalculate limits
        # ax.autoscale_view()  # Autoscale the view
        
        
        # line11.set_xdata(rotationArray[6])
        # line21.set_xdata(rotationArray[6])

        # line11.set_ydata(rotationArray[4])
        # line21.set_ydata(rotationArray[5])

        # ax1.relim()  # Recalculate limits
        # ax1.autoscale_view()  # Autoscale the view

        # plt.draw()
        # plt.pause(0.01)
