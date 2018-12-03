# -*- coding: utf-8 -*-

from mpu6050 import mpu6050
import RPi.GPIO as GPIO
from hx711 import HX711
import integrate_api
from gps import gps
import threading
import datetime
import time
import math
import sys
import os


TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJuYW1lIjoiQWxmcmVkbyAiLCJjb2RlIjoiSmZqZmpmamYifQ.DU5HNhy3hidFNqMwoDBPvFINPSbXyAqb_GARfLdpjxM"
gps_sensor = None
running = True
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

class SensorPeso(threading.Thread):
	def __init__(self, PIN_OUT=29, PIN_SCK=31):
		threading.Thread.__init__(self)
		self.daemon = True
		self.HX711_SENSOR = HX711(PIN_OUT, PIN_SCK)
		self.done_setting = False
	
	def finish_setting(self):
		return self.done_setting
	
	def set(self):
		raw_input('Coloque um peso conhecido e pressione ENTER')
		data = self.HX711_SENSOR.get_data_mean(times=10)
		time.sleep(1)
		if data != False:
			tara = float(raw_input('Escreva a quantidade de gramas e pressione ENTER: '))
			ratio = data / tara
			self.HX711_SENSOR.set_scale_ratio(scale_ratio=ratio)
		else:
			raise ValueError('Não foi possível calcular a tara da balanca')
		time.sleep(1)
		self.done_setting = True
		print bcolors.BOLD + bcolors.OKGREEN + "COMEÇANDO..." + bcolors.ENDC

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
	 
		time.sleep(0.00001)
		GPIO.output(self.TRIGGER, False)
	 
		StartTime = time.time()
		StopTime = StartTime
	 
		while GPIO.input(self.ECHO) == 0:
			StartTime = time.time()
	 
		while GPIO.input(self.ECHO) == 1:
			StopTime = time.time()
	 
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
		global gps_sensor
		gps_sensor = gps(mode=1)

	def run(self):
		global gps_sensor
		while running:
			gps_sensor.next()

class SensorMPU6050(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = True
		self.sensor = mpu6050(0x68)

	def run(self):
		while running:
			print("Temperatura: {temp} °C".format(temp=round(self.sensor.get_temp(),1)))
			accel = self.sensor.get_accel_data()
			print("Ax: {valor} m/s²".format(valor=round(accel['x'],2)))
			print("Ay: {valor} m/s²".format(valor=round(accel['y'],2)))
			time.sleep(2)


def mensagem(status, sensor):
	if status == 201:
		print bcolors.BOLD + bcolors.OKGREEN + "[{sens}] Envio com sucesso!".format(sens=sensor) + bcolors.ENDC
	else:
		print bcolors.BOLD + bcolors.FAIL + "[{sens}] Falha no envio...".format(sens=sensor) + bcolors.ENDC


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

try:
	while True:
		# STATUS = web_socket.get_status()
		if STATUS == START:
			running = True
			peso = SensorPeso()
			#volume = SensorVolume()
			#acegyrotemp = SensorMPU6050()
			
			peso.set()
			
			done_setting_peso = peso.finish_setting()
			
			while not done_setting_peso:
				done_setting_peso = peso.finish_setting()
			
			peso.start()
			#volume.start()
			#acegyrotemp.start()
			
			STATUS = RUNNING

		elif STATUS == STAND_BY:
			running = False

except(KeyboardInterrupt, SystemExit):
	running = False


