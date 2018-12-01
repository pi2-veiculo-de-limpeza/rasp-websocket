from server import WebsocketServer
import sys
from multiprocessing import Process
import Queue
import time

# example callbacks
def rigthMotor(value, direction):
	print("right: " + str(value) + " " + str(direction) )

def leftMotor(value, direction):
	print("left: " + str(value) + " " + str(direction) )

def turnOffVehicle():
	print("Turn off vehicle")

def turnOnMat():
	print("Turn on mat")

def turnOffMat():
	print("Turn off mat")
 
if __name__ == '__main__':
    ws = WebsocketServer()

    ws.rightMotorCallback(      rigthMotor  )
    ws.leftMotorCallback(       leftMotor   )
    ws.turnOffVehicleCallback(  turnOffVehicle )
    ws.turnOnMatCallback(       turnOnMat   )
    ws.turnOffMatCallback(      turnOffMat  )

    # handling new process
    p = Process(target=WebsocketServer.start, args = (ws,))
    p.start()

    print("\nThread is running async")

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        print('Keyboard interrupt')
        p.terminate()
        sys.exit(0)