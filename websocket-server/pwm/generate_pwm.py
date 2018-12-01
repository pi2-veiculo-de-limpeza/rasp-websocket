import RPi.GPIO as GPIO
import time
import sys
from controle import Controle

pin_out = 38
direction_port = 26
frequency = 1000
duty_cycle = 50
slepping = 2
direction = 0

# Handling Joystick thread
joystick = Controle()
q = Queue.Queue()
t = threading.Thread(target=Controle.run, args = (joystick, q))
t.daemon = True
# Starting thread
t.start()


GPIO.setwarnings(False)

# Configurando GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(pin_out,GPIO.OUT)
GPIO.setup(direction_port,GPIO.OUT)

if direction:
	GPIO.output(direction_port, True)
else:
	GPIO.output(direction_port, False)
# Configurando o PWM
PWM = GPIO.PWM(pin_out,frequency)
PWM.start(duty_cycle)

should_exit = False

while not should_exit:
	duty_cycle = q.get()
	print(duty_cycle)
	if duty_cycle > 100:
		should_exit = True

	if duty_cycle > 0 and duty_cycle < 100:
		print("Updating duty: " + duty_cycle)
		PWM.ChangeDutyCycle(duty_cycle)
	# else:
	# 	print('duty_cycle different from 0 and 100...')

GPIO.cleanup()

