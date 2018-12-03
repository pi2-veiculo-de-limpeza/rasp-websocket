import RPi.GPIO as GPIO
import time
import sys
import threading
import math
from server import WebsocketServer

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

MIN_DC = 100

esteira_pode_ser_iniciada = True

class Motor():
	
	def __init__(self, pin_out, direction_port=37, frequency=1000):
		self.pin_out = pin_out
		self.direction_port = direction_port
		self.frequency = frequency
		self.direction = True
		self.duty_cycle = MIN_DC
		self.setup()
		self.name = 'Motor'
		self.changingDirection = False

	def setup(self):
		# Configurando GPIO
		GPIO.setup(self.pin_out, GPIO.OUT)
		GPIO.setup(self.direction_port, GPIO.OUT)

		GPIO.output(self.direction_port, True)
		# Configurando o PWM
		self.pwm = GPIO.PWM(self.pin_out, self.frequency)
		
		self.pwm.start(MIN_DC)

	def set_duty_cycle(self, new_dc, direction=None):
		if direction != None:
			direction = float(direction)
			new_dir = direction == -1 # -1 equals True
			if self.direction != new_dir:
				self.handleDirectionChange()
			self.direction = new_dir
		
		self.duty_cycle = math.fabs(float(new_dc) - MIN_DC)
		print(self.name, self.duty_cycle, self.direction)
	
	def update(self):
		
		if self.changingDirection == False:
			GPIO.output(self.direction_port, self.direction)
			self.pwm.ChangeDutyCycle(self.duty_cycle)
		else:
			self.pwm.ChangeDutyCycle(MIN_DC)

	def handleDirectionChange(self):
		p = threading.Thread(target=Motor.finishDirectionChange, args = (self,))
		p.daemon = True
		p.start()

	def finishDirectionChange(self):
		if self.changingDirection == False:
			self.changingDirection = True
			time.sleep(1)
			self.changingDirection = False
		
	def stop(self):
		self.pwm.stop()
		
class Esteira(Motor):
	def __init__(self, pin_out, direction_port=33, frequency=1000):
		self.pin_out = pin_out
		self.direction_port = direction_port
		self.frequency = frequency
		self.direction = True
		self.duty_cycle = MIN_DC
		self.setup()
		self.name = 'Esteira'
		self.shouldStop = False
		self.initialVel = False
		self.shouldStart = True
		self.changingDirection = False
		
	def update(self):
		if not self.shouldStop:
			GPIO.output(self.direction_port, self.direction)
			self.pwm.ChangeDutyCycle(self.duty_cycle)
		else:
			if self.duty_cycle != MIN_DC:
				self.set_duty_cycle(0) # set_dc -> transforms 100 in max
				self.shouldStop = False
		
		
		
def start_inicial_esteira(esteira, vel_inicial, vel_final, delay):
	# if esteira.shouldStart:
	esteira.shouldStop = False
	
	if esteira.shouldStart and esteira.initialVel == False:
		esteira.shouldStart = False
		esteira.initialVel = True
		esteira.set_duty_cycle(vel_inicial)
		
		time.sleep(delay)
		if esteira.duty_cycle != MIN_DC:
			esteira.set_duty_cycle(vel_final)
		
		esteira.initialVel = False
	else:
		print('Esteira nao deve ser iniciada')

def rigthMotor(value, direction):
	# print('receive',right_motor.name, value, direction)
	right_motor.set_duty_cycle(value, direction)

def leftMotor(value, direction):
	# print('receive',left_motor.name, value, direction)
	left_motor.set_duty_cycle(value, direction)

def turnOffVehicle():
	print("Turn off vehicle")

def turnOnMat():
	print("Turn on mat")
	p = threading.Thread(target=start_inicial_esteira, args = (esteira, 100, 50, 1))
	p.daemon = True
	p.start()

def turnOffMat():
	esteira.shouldStop = True
	esteira.shouldStart = True
	print("Turn off mat")

def sendUpdate():
	while True:
		if right_motor.changingDirection == False:
			r_message = '{},{},{}'.format(right_motor.name, right_motor.duty_cycle, right_motor.direction)
		else:
			r_message = '{},{},{}'.format(right_motor.name, 100, right_motor.direction)
		
		if left_motor.changingDirection == False:
			l_message = '{},{},{}'.format(left_motor.name, left_motor.duty_cycle, left_motor.direction)
		else:
			l_message = '{},{},{}'.format(left_motor.name, 100, left_motor.direction)
		
		e_message = '{},{},{}'.format(esteira.name, esteira.duty_cycle, esteira.direction)

		sendMessage(r_message)
		sendMessage(l_message)
		sendMessage(e_message)

		time.sleep(1)
	
def sendMessage(message):
	ws.websocket.send_message_to_all(message)
	
left_motor = Motor(36,35)
left_motor.name = 'left'

right_motor = Motor(38,37)
right_motor.name = 'right'

esteira = Esteira(32, 33)
esteira.name = 'esteira'


ws = WebsocketServer()

ws.rightMotorCallback(      rigthMotor  )
ws.leftMotorCallback(       leftMotor   )
ws.turnOffVehicleCallback(  turnOffVehicle )
ws.turnOnMatCallback(       turnOnMat   )
ws.turnOffMatCallback(      turnOffMat  )

# handling ws threading
p = threading.Thread(target=WebsocketServer.start, args = (ws,))
p.daemon = True
p.start()

# handling threading that sends update to receiver
updt_receiver = threading.Thread(target=sendUpdate) 
updt_receiver.daemon = True
updt_receiver.start()

print("\nWebsocket is running in a separate Thread")

try:
	while True:
		left_motor.update()
		right_motor.update()
		esteira.update()
		time.sleep(0.01)
except KeyboardInterrupt:
	left_motor.stop()
	right_motor.stop()
	esteira.stop()
	print('Stoping motors')
	sys.exit(0)
