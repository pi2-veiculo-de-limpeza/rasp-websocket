# -*- coding: utf-8 -*-

import threading
import datetime
import time
import math
import sys
import os

import RPi.GPIO as GPIO
import integrate_api

from mpu6050 import mpu6050
from gps3 import gps3
from hx711 import HX711

from server import WebsocketServer

MIN_DC = 100

TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJuYW1lIjoiQWxmcmVkbyAiLCJjb2RlIjoiSmZqZmpmamYifQ.DU5HNhy3hidFNqMwoDBPvFINPSbXyAqb_GARfLdpjxM"

gps_sensor = None
running = True
standby = False

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

START = 1
STAND_BY = 2
RUNNING = 3
STATUS = START

class bcolors:
	HEADER		= '\033[95m'
	OKBLUE		= '\033[94m'
	OKGREEN		= '\033[92m'
	WARNING		= '\033[93m'
	FAIL		= '\033[91m'
	ENDC		= '\033[0m'
	BOLD		= '\033[1m'
	UNDERLINE	= '\033[4m'


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
		# print(self.name, self.duty_cycle, self.direction)
	
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
	print("Standby vehicle")
	sendMessage('stand-by')

def turnOnVehicle():
	print('Turn on vehicle')
	sendMessage('turn-on')

def turnOnMat():
	print("Turn on mat")
	p = threading.Thread(target=start_inicial_esteira, args = (esteira, 100, 50, 0.65))
	p.daemon = True
	p.start()

def turnOffMat():
	esteira.shouldStop = True
	esteira.shouldStart = True
	print("Turn off mat")

def calibrateScale(weight):
	peso.set()

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
	print(message)
	ws.websocket.send_message_to_all(message)

class SensorPeso(threading.Thread):
	def __init__(self, PIN_OUT=29, PIN_SCK=31):
		threading.Thread.__init__(self)
		self.daemon = True
		self.HX711_SENSOR = HX711(PIN_OUT, PIN_SCK)
		data = self.HX711_SENSOR.get_raw_data_mean(times=1)
		result = self.HX711_SENSOR.zero(times=10)
		data = self.HX711_SENSOR.get_data_mean(times=10)
		self.done_setting = False
	
	def finish_setting(self):
		return self.done_setting
	
	def set(self, peso=None):

		data = self.HX711_SENSOR.get_data_mean(times=10)

		if(peso != None):
			raw_input('Coloque um peso conhecido e pressione ENTER')

		if data != False:
			if(peso != None):
				tara = float(raw_input('Escreva a quantidade de gramas e pressione ENTER: '))
			else:
				tara = peso
			ratio = data / tara
			self.HX711_SENSOR.set_scale_ratio(scale_ratio=ratio)
		else:
			raise ValueError('Não foi possível calcular a tara da balanca')
		self.done_setting = True
		
		
	def run(self):
		try:
			peso_pen = int(self.HX711_SENSOR.get_weight_mean(6))
			
			if peso_pen < 0:
				peso_pen = 0

			peso_ult = int(self.HX711_SENSOR.get_weight_mean(6))
			if peso_ult < 0:
				peso_ult = 0

			while running:
				peso_atual = int(self.HX711_SENSOR.get_weight_mean(6))
				
				if peso_atual < 0:
					peso_atual = 0

				if peso_ult > 0:
					prop1 = abs(peso_pen / peso_ult)
				else:
					prop1 = 0

				if peso_atual > 0:
					prop2 = abs(peso_ult / peso_atual)
				else:
					prop2 = 0

				if 0.80 < max(prop1, prop2) < 1.20:
					print('Peso: {peso}g'.format(peso=peso_atual))
					status = integrate_api.integrate_peso_lixo(peso_atual, str(datetime.datetime.now()), TOKEN)
					sendMessage('weight,{}'.format(peso_atual))
					print('weight,{}'.format(peso_atual))
					mensagem(status, 'Peso')

				peso_pen = peso_ult
				peso_ult = peso_atual

				time.sleep(2)
		except (KeyboardInterrupt, SystemExit):
			pass

class SensorVolume(threading.Thread):
	def __init__(self,  TRIGGER = 16, ECHO = 18):
		threading.Thread.__init__(self)
		self.daemon = True
		self.TRIGGER = TRIGGER
		self.ECHO = ECHO
		GPIO.setup(self.TRIGGER, GPIO.OUT)
		GPIO.setup(self.ECHO, GPIO.IN)
	
	def distance(self):
		GPIO.output(self.TRIGGER, True)
	 
		time.sleep(0.1)
		GPIO.output(self.TRIGGER, False)
	 
		StartTime = time.time()
		StopTime = StartTime
	 
		while GPIO.input(self.ECHO) == 0:
			StartTime = time.time()
			time.sleep(0.5)
	 
		while GPIO.input(self.ECHO) == 1:
			StopTime = time.time()
			time.sleep(0.5)
	 
		TimeElapsed = StopTime - StartTime
		distance = (TimeElapsed * 34300) / 2
	 
		return round(distance, 1)

	def run(self):
		try:
			dist_pen = self.distance()
			dist_ult = self.distance()

			while running:
				dist_atual = self.distance()
				if dist_atual < 40:
					prop1 = abs(dist_pen / dist_ult)
					prop2 = abs(dist_ult / dist_atual)

					if 0.95 < max(prop1, prop2) < 1.05: # Lixeira profundidade 40cm
						volume_percent = (dist_atual * 100) / 40
						print ("Volume livre: {vol}% | Distancia: {dist} cm".format(vol=round(volume_percent,1),dist=dist_atual))
						sendMessage( 'volume,{}'.format(volume_percent) )
						if volume_percent < 40:
							print bcolors.BOLD + bcolors.WARNING + "LIXO CHEIO!\n" + bcolors.ENDC
							status = integrate_api.integrate_monitory_volume_sensor_dump(True, str(datetime.datetime.now()), TOKEN)
				time.sleep(2)

				dist_pen = dist_ult
				dist_ult = dist_atual

		except (KeyboardInterrupt, SystemExit):
			pass

class SensorGPS(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = True
		self.gps_socket = gps3.GPSDSocket()
		self.data_stream = gps3.DataStream()

	def run(self):
		self.gps_socket.connect()
		self.gps_socket.watch()

		for new_data in self.gps_socket:
			if new_data:
				self.data_stream.unpack(new_data)
				print('Longitude = {lon} °'.format(lon=self.data_stream.TPV['lon']))
				print('Latitude = {lat} °'.format(lat=self.data_stream.TPV['lat']))
			time.sleep(0.2)


class SensorMPU6050(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = True
		self.sensor = mpu6050(0x68)

	def run(self):
		while running:
			temp = round(self.sensor.get_temp(),1)
			# print("Temperatura: {temp} °C".format(temp=temp) )
			accel = self.sensor.get_accel_data()
			x = round(accel['x'],2)
			y = round(accel['y'],2)
			# print("Ax: {valor} m/s²".format(valor=x) )
			# print("Ay: {valor} m/s²".format(valor=y) )

			sendMessage( 'acc,{},{},{}'.format(x,y,temp) )
			time.sleep(1)


def mensagem(status, sensor):
	if status == 201:
		print bcolors.BOLD + bcolors.OKGREEN + "[{sens}] Envio com sucesso!".format(sens=sensor) + bcolors.ENDC
	else:
		print bcolors.BOLD + bcolors.FAIL + "[{sens}] Falha no envio...".format(sens=sensor) + bcolors.ENDC


# inicializando Motores
left_motor = Motor(36,35)
left_motor.name = 'left'

right_motor = Motor(38,37)
right_motor.name = 'right'

esteira = Esteira(32, 33)
esteira.name = 'esteira'

# inicializando Sensores
peso = SensorPeso()
volume = SensorVolume()
acegyrotemp = SensorMPU6050()
sensor_gps = SensorGPS()

ws = WebsocketServer()

ws.rightMotorCallback(      rigthMotor  )
ws.leftMotorCallback(       leftMotor   )
ws.turnOffVehicleCallback(  turnOffVehicle )
ws.turnOnMatCallback(       turnOnMat   )
ws.turnOffMatCallback(      turnOffMat  )
ws.turnOnCallback(          turnOnVehicle )
ws.calibrateCallback(       calibrateScale )

# handling ws threading
p = threading.Thread(target=WebsocketServer.start, args = (ws,))
p.daemon = True
p.start()

# handling threading that sends update to receiver
updt_receiver = threading.Thread(target=sendUpdate) 
updt_receiver.daemon = True
updt_receiver.start()

print("\nWebsocket is running in a separate Thread")

# try:
# 	while True:
# 		left_motor.update()
# 		right_motor.update()
# 		esteira.update()
# 		time.sleep(0.01)
# except KeyboardInterrupt:
# 	left_motor.stop()
# 	right_motor.stop()
# 	esteira.stop()
# 	GPIO.cleanup()
# 	print('Stoping motors')
# 	sys.exit(0)


try:
	while True:
		left_motor.update()
		right_motor.update()
		esteira.update()

		# STATUS = web_socket.get_status()
		if STATUS == START:
			running = True
			
			peso.start()
			volume.start()
			acegyrotemp.start()
			sensor_gps.start()
			
			STATUS = RUNNING

		elif STATUS == STAND_BY:
			running = False
		time.sleep(0.1)

except(KeyboardInterrupt, SystemExit):
	running = False
	left_motor.stop()
	right_motor.stop()
	esteira.stop()
	GPIO.cleanup()
	print('Stoping all')
	sys.exit(0)
