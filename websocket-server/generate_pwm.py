import RPi.GPIO as GPIO
import time
import sys
import threading
import math
from server import WebsocketServer

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

esteira_pode_ser_iniciada = True

class Motor():
	
	def __init__(self, pin_out, direction_port=37, frequency=1000):
		self.pin_out = pin_out
		self.direction_port = direction_port
		self.frequency = frequency
		self.direction = True
		self.duty_cycle = 0
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
		
		self.pwm.start(0)

	def set_duty_cycle(self, new_dc, direction):
		direction = float(direction)
		new_dir = direction == -1

		if self.direction != new_dir:
			self.handleDirectionChange()
		
		self.direction = new_dir
		self.duty_cycle = math.fabs(float(new_dc) - 100)
		print(self.name, self.duty_cycle, self.direction)
	
	def update(self):
		
		if self.changingDirection == False:
			GPIO.output(self.direction_port, self.direction)
			self.pwm.ChangeDutyCycle(self.duty_cycle)
			message = '{},{},{}'.format(self.name, self.duty_cycle, self.direction)
			ws.websocket.send_message_to_all(message)
			print('message sent: {}'.format(message) )
		else:
			message = '{},{},{}'.format(self.name, 100, self.direction)
			ws.websocket.send_send_message_to_all(message)
			print('message sent: {}'.format(message) )
			self.pwm.ChangeDutyCycle(100)

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
	def __init__(self, pin_out, direction_port=32, frequency=1000):
		self.pin_out = pin_out
		self.direction_port = direction_port
		self.frequency = frequency
		self.direction = False
		self.duty_cycle = 0
		self.setup()
		self.name = 'Esteira'
		self.shouldStop = False
		self.initialVel = False
		self.shouldStart = True
		
	def update(self):
		if not self.shouldStop:
			GPIO.output(self.direction_port, self.direction)
			self.pwm.ChangeDutyCycle(self.duty_cycle)
		else:
			if self.duty_cycle != 0:
				self.set_duty_cycle(0, -1)
				self.shouldStop = False
		
		
		
def start_inicial_esteira(esteira, vel_inicial, vel_final, delay):
	esteira.shouldStop = False
	
	if esteira.shouldStart and esteira.initialVel == False:
		esteira.shouldStart = False
		esteira.initialVel = True
		esteira.set_duty_cycle(vel_inicial ,-1)
		
		time.sleep(delay)
		if esteira.duty_cycle != 0:
			esteira.set_duty_cycle(vel_final,-1)
		
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
	p = threading.Thread(target=start_inicial_esteira, args = (esteira, 25, 50, 2))
	p.daemon = True
	p.start()

def turnOffMat():
	esteira.shouldStop = True
	esteira.shouldStart = True
	print("Turn off mat")


left_motor = Motor(36,35)
left_motor.name = 'left'

right_motor = Motor(38,37)
right_motor.name = 'right'

esteira = Esteira(32)
esteira.name = 'esteira'


ws = WebsocketServer()

ws.rightMotorCallback(      rigthMotor  )
ws.leftMotorCallback(       leftMotor   )
ws.turnOffVehicleCallback(  turnOffVehicle )
ws.turnOnMatCallback(       turnOnMat   )
ws.turnOffMatCallback(      turnOffMat  )

# handling new process
p = threading.Thread(target=WebsocketServer.start, args = (ws,))
p.daemon = True
p.start()

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
	print('Stoping motors')
	sys.exit(0)

