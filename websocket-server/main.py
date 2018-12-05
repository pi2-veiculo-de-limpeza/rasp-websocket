from server import WebsocketServer
import sys
from multiprocessing import Process
import Queue
import time
import random




class Fake():

    def __init__(self):
        self.pwm_left=50
        self.dir_left=False
        self.pwm_right=50
        self.dir_right=False
        self.pwm_est=30

        self.gps_lon=20
        self.gps_lat=30

        self.acc_x=1.241
        self.acc_y=2.653
        self.acc_temp=26.4

        self.vol=20
        self.wei=3

        self.i_acc = 10
        self.i_motor = 3

    def updateAcc(self):
        self.i_acc -= 1
        if self.i_acc < 0:
            self.i_acc = 10
            self.acc_x=round(random.random()*3, 3)
            self.acc_y=round(random.random()*3, 3)
            self.acc_temp= 25 + round(random.random()*3, 2)
        if self.i_acc == 3:
            self.gps_lon=20 + round(random.random()*2, 2)
            self.gps_lat=30 + round(random.random()*2, 2)

        if self.i_acc == 7:
            self.vol= random.randint(0, 10)*10
            self.wei= random.randint(0, 500)*3

    def updateMotor(self):
        self.i_motor -= 1
        if self.i_motor < 0:
            self.i_motor = 3
            self.pwm_left= random.randint(0, 10)*10
            self.pwm_right= random.randint(0, 10)*10
            self.pwm_est= random.randint(0, 10)*10

    def updateAll(self):
        self.updateAcc()
        self.updateMotor()

        r_message = '{},{},{}'.format('right', self.pwm_right, self.dir_right)
        l_message = '{},{},{}'.format('left', self.pwm_left, self.dir_left)
        e_message = '{},{},{}'.format('esteira', self.pwm_est, True)
        sendMessage(r_message)
        sendMessage(l_message)
        sendMessage(e_message)

        sendMessage('weight,{}'.format(self.wei))
        sendMessage( 'volume,{}'.format(self.vol) )
        sendMessage( 'acc,{},{},{}'.format(self.acc_x, self.acc_y, self.acc_temp) )

        sendMessage( 'gps,{},{}'.format(self.gps_lat, self.gps_lon) )

def sendMessage(message):
	print(message)
	ws.websocket.send_message_to_all(message)


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

def turnOffVehicle():
	print("Standby vehicle")
	sendMessage('stand-by')

def turnOnVehicle():
	print('Turn on vehicle')
	sendMessage('turn-on')

def calibrateScale():
    print('calibrate')

 
if __name__ == '__main__':
    ws = WebsocketServer()

    ws.rightMotorCallback(      rigthMotor  )
    ws.leftMotorCallback(       leftMotor   )
    ws.turnOffVehicleCallback(  turnOffVehicle )
    ws.turnOnMatCallback(       turnOnMat   )
    ws.turnOffMatCallback(      turnOffMat  )
    ws.turnOnCallback(          turnOnVehicle )
    ws.calibrateCallback(       calibrateScale )

    # handling new process
    p = Process(target=WebsocketServer.start, args = (ws,))
    p.start()

    print("\nThread is running async")

    fake = Fake()

    try:
        while True:
            fake.updateAll()
            time.sleep(0.2)
    except KeyboardInterrupt:
        print('Keyboard interrupt')
        p.terminate()
        sys.exit(0)