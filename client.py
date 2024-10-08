import socket
import json
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.animation import FuncAnimation

HOST = "192.168.1.67"  # The server's hostname or IP address
PORT = 65002  # The port used by the server


def saveJson(jsonCharArr, jsonArray):
    try:
        jsonString = "".join(jsonCharArr)
        
        jsonObject = json.loads(jsonString)
        
        gyroData = jsonObject["gyroscope"]["value"]
        
        jsonArray[0].append(gyroData[0])
        jsonArray[1].append(gyroData[1])
        jsonArray[2].append(gyroData[2])
        
        timestamp_ns = jsonObject["gyroscope"]["timestamp"]
        
        # Convert to seconds
        timestamp_s = timestamp_ns / 1_000_000_000

        # Convert to datetime object
        dt = datetime.fromtimestamp(timestamp_s)
        
        dt = dt + timedelta(hours=5)
        dt = dt + timedelta(minutes=37)
        # dt = dt.time()
        # dt = dt.strftime("%H:%M:%S")
        
        jsonArray[3].append(dt)
    except json.JSONDecodeError:
        print("fail")
        pass


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    dataArray = [[], [], [], []]
    
    plt.ion()  # Turn on interactive mode
    fig, ax = plt.subplots()
    
    line1, = ax.plot([], [], color='red', label='rotation about x')  # First line
    line2, = ax.plot([], [], color='blue', label='rotation about y')  # Second line
    line3, = ax.plot([], [], color='green', label='rotation about z')  # Third line
    
    ax.set_xlabel('Time')
    ax.set_ylabel('gyro-data')
    ax.set_title('real time gyro data')
    ax.legend()
    
    while True:
        data = s.recv(1024).decode("utf-8")
        # parsed_data = json.loads(data)
        count = 0
        jsonCharArr = []
        for char in data:
            if char == "\n":
                continue
            if char == "{" and jsonCharArr:
                if count == 1:
                    count = 0
                    saveJson(jsonCharArr, dataArray)
                    jsonCharArr = ["{"]
                else:
                    count = 1
                    jsonCharArr.append(char)
            else:
                jsonCharArr.append(char)

        saveJson(jsonCharArr, dataArray)
        
        
        line1.set_xdata(dataArray[3])
        line2.set_xdata(dataArray[3])
        line3.set_xdata(dataArray[3])
        
        line1.set_ydata(dataArray[0])
        line2.set_ydata(dataArray[1])
        line3.set_ydata(dataArray[2])
        
        ax.relim()  # Recalculate limits
        ax.autoscale_view()  # Autoscale the view 
        
        plt.draw()
        plt.pause(0.01)
        
        
    plt.ioff()
    plt.show()
