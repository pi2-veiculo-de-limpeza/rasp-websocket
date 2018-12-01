import RPi.GPIO as GPIO
import time
import sys
import pygame
import Queue
import threading
import os

os.environ['SDL_VIDEODRIVER'] = 'dummy'

esq = 0
dir = 0
done = False

motor_esq = 1
motor_esq_veloc = "Parado"
motor_dir = 4
motor_dir_veloc = "Parado"
BTN_ON = 4
BTN_OFF = 5
esteira_status = "Desligado"

def direction_motor(direction):
	if direction > 0:
		# GPIO.output(direction_port, True)
		return "Back"
	elif direction < 0:
		# GPIO.output(direction_port, False)
		return "Front"
	else:
		return "Parado"

class Controle(threading.Thread):
	def __init__(self):
		super(Controle, self).__init__()
		
		pygame.init()
		pygame.joystick.init()

	def run(self, queue):
		while not done:
			joystick = pygame.joystick.Joystick(0)

			joystick.init()

			os.system('clear')

			for event in pygame.event.get():
				if event.type == pygame.JOYAXISMOTION:
					if event.axis == motor_esq:
						motor_esq_veloc = direction_motor(event.value)
						esq = event.value
					elif event.axis == motor_dir:
						motor_dir_veloc = direction_motor(event.value)
						dir = event.value
				elif event.type == pygame.JOYBUTTONDOWN:
					if event.button == BTN_ON:
						esteira_status = "Ligada"

					elif event.button == BTN_OFF:
						esteira_status = "Desligada"

			queue.put(esq * 100)
			# Leave joystick
			if motor_dir_veloc == "Back":
				print("Exiting joystick  gracefully :D")
				queue.put(200)
				done = True
		#				PWM.start(35)
		#				PWM.ChangeDutyCycle(duty_cycle)
			print("====================================")
			print("Motor Esq Veloc: " + motor_esq_veloc)
			print(esq)
			print("Motor Dir Veloc: " + motor_dir_veloc)
			print(dir)
			print("Esteira: " + esteira_status)
			print("====================================")
			time.sleep(0.5)
		
		# Ending joystick
		pygame.quit ()
