from server import WebsocketServer

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
    
    ws.start()