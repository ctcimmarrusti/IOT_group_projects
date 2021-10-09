import picar_4wd as fc
from enum import Enum
from picar_4wd.filedb import FileDB
from picar_4wd.servo import Servo
from picar_4wd.pwm import PWM
from picar_4wd.pin import Pin
from picar_4wd.ultrasonic import Ultrasonic 
import socket
import threading
import io
import numpy as np
import picamera
from PIL import Image
import base64
import time
from picar_4wd.utils import cpu_temperature, gpu_temperature, power_read

FLIP_IMAGE_VERTIAL = True
HOST = "192.168.2.107" 
COMMANDPORT = 65432
WEBCAMPORT = 65433
STATSPORT = 65434

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
speed = 10

class Direction(Enum):
    FORWARD = 1
    BACKWARD = 2
    LEFT = 3
    RIGHT = 4
    STOPPED = 5
currentDirection = Direction.STOPPED
def driveTowardsDirection(direction):
    global currentDirection
    if direction == Direction.FORWARD and currentDirection != Direction.FORWARD:
        fc.forward(speed)
    elif direction == Direction.BACKWARD and currentDirection != Direction.BACKWARD:
        fc.backward(speed)
    elif direction == Direction.LEFT and currentDirection != Direction.LEFT:
        fc.turn_left(speed)
    elif direction == Direction.RIGHT and currentDirection != Direction.RIGHT:
        fc.turn_right(speed)
    elif direction == Direction.STOPPED and currentDirection != Direction.STOPPED:
        fc.stop()
    currentDirection = direction
def driveViaSocketCommand(command):
    if command == "87":
        driveTowardsDirection(Direction.FORWARD)
    elif command == "83":
        driveTowardsDirection(Direction.BACKWARD)
    elif command == "65":
        driveTowardsDirection(Direction.LEFT)
    elif command == "68":
        driveTowardsDirection(Direction.RIGHT)
    elif command == "STOP":
        driveTowardsDirection(Direction.STOPPED)
def runCameraSocket():
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, WEBCAMPORT))
    s.listen()
    camclient, clientInfo = s.accept()
    while True:
        with picamera.PiCamera(resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=30) as camera:
            camera.start_preview()
            try:
                stream = io.BytesIO()
                camera.capture(stream, format='jpeg')
                stream.seek(0)
                image = Image.open(stream).convert('RGB')   
                if FLIP_IMAGE_VERTIAL:
                    image = image.transpose(Image.FLIP_TOP_BOTTOM)        
                stream.seek(0)
                stream.truncate()
                buffer = io.BytesIO()
                image.save(buffer,format="JPEG")                  
                still_buff = buffer.getvalue()                     
                if not camclient == None:
                    camclient.send(base64.b64encode(still_buff)) # somewhat inefficient, a better approach would be to just send the raw stream data from the picamera and use webRTC on the client
                    camclient.send(bytes("\r\n", "utf-8"))
            except Exception as e: 
                print(e)
                camclient.close()
                s.close()
            finally:
                camera.stop_preview()            
def runCommandSocket():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, COMMANDPORT))
        s.listen()
        client, clientInfo = s.accept() 
        try:
            while True:
                data = client.recv(1024)      
                command = data.decode("utf-8")
                driveViaSocketCommand(command)
        except Exception as e: 
            print(e)
            client.close()
            s.close()
def runStatsSocket():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, STATSPORT))
        s.listen()
        statsclient, clientInfo = s.accept() 
        try:
            while True:
                time.sleep(1)
                cputemp = str(cpu_temperature())
                gputemp = str(gpu_temperature())

                battery = str(power_read())
                statsclient.send(bytes('{"cputemp": "'+ cputemp +'","gputemp": "'+ gputemp +'", "battery":"'+ battery +'"}', "utf-8"))
                statsclient.send(bytes("\r\n", "utf-8"))
        except Exception as e: 
            print(e)
            statsclient.close()
            s.close()

t1 = threading.Thread(target=runCameraSocket, args=())
t2 = threading.Thread(target=runCommandSocket, args=())
t3 = threading.Thread(target=runStatsSocket, args=())


t1.start()
t2.start()
t3.start()
