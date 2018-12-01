import RPi.GPIO as GPIO
import time
import sys
import pygame
import Queue
import threading
import os
from generate_pwm import GeneratePWM

os.environ['SDL_VIDEODRIVER'] = 'dummy'

pygame.init()
pygame.joystick.init()

# Instantiate pwm
pwm_motor = GeneratePWM(38, 26)

# Handling pwm thread
q = Queue.Queue()
t = threading.Thread(target=GeneratePWM.run, args = (pwm_motor, q))
t.daemon = True
# Starting thread
t.start()


motor_esq = 1
motor_esq_veloc = "Parado"
motor_dir = 4
motor_dir_veloc = "Parado"
BTN_ON = 4
BTN_OFF = 5
esteira_status = "Desligado"
#esteira_status = "Desligada"

#MOT_esq = 20 # GPIO20 | Pin 38
#MOT_dir = 16
#MOT_esteira = 12
#DIR_esq = 26
#DIR_dir = 19
#DIR_esteira = 13

#GPIO.setwarnings(False)

# Configurando GPIO
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(MOT_esq,GPIO.OUT)
#GPIO.setup(DIR_esq,GPIO.OUT)
#GPIO.setup(MOT_dir,GPIO.OUT)
#GPIO.setup(DIR_dir,GPIO.OUT)
#GPIO.setup(MOT_esteira,GPIO.OUT)
#GPIO.setup(DIR_esteira,GPIO.OUT)
#PWM_esteira = GPIO.PWM(MOT_esteira,1000)
esq = 0
dir = 0
done = False

def direction_motor(direction):
	if direction > 0:
#		GPIO.output(direction_port, True)
		return "Back"
	elif direction < 0:
#		GPIO.output(direction_port, False)
		return "Front"
	else:
		return "Parado"

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

	q.put(motor_esq_veloc)
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

pygame.quit ()

# Trying to close thread
pwm_motor.stop()
# t.close()
