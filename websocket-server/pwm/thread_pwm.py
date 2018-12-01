# import RPi.GPIO as GPIO
import time
import sys
import Queue
import threading

class GeneratePWM(threading.Thread):
	def __init__(self, pwm_pin, dir_pin, duty_cycle=50, direction=0, freq=1000):
		super(GeneratePWM, self).__init__()
		self._stop_event = threading.Event()

		self.pin_out = pwm_pin
		self.frequency = freq
		self.duty_cycle = duty_cycle
		self.slepping = 2
		self.direction_port = dir_pin
		self.direction = direction
		self.exit = False

	def stop(self):
		self.exit = True
		self._stop_event.set()

    def stopped(self):
		self.exit = True
		return self._stop_event.is_set()

	def run(self, queue):
		GPIO.setwarnings(False)
		self.q = queue

		# Configurando GPIO
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.pin_out,GPIO.OUT)
		GPIO.setup(self.direction_port,GPIO.OUT)

		if self.direction:
			GPIO.output(self.direction_port, True)
		else:
			GPIO.output(self.direction_port, False)
		# Configurando o PWM
		self.PWM = GPIO.PWM(self.pin_out, self.frequency)
		self.PWM.start(self.duty_cycle)

		# Hold thread
		self.updatePWM()

		# cleanup
		self.close()

	def close(self):
		GPIO.cleanup()

	def updatePWM(self):
		limit = 100

		while not self.exit:
			duty_cycle = self.q.get()
			if duty_cycle > 0 and duty_cycle < 100:
				self.PWM.ChangeDutyCycle(duty_cycle)
			else:
				print('duty_cycle different from 0 and 100...')

			# Leave PWM
			limit -= 1
			if limit < 0:
				self.exit = True


class GeneratePWM(threading.Thread):
	def __init__(self, pwm_pin, dir_pin, duty_cycle=50, direction=0, freq=1000):
		super(GeneratePWM, self).__init__()
		self._stop_event = threading.Event()

		self.pin_out = pwm_pin
		self.frequency = freq
		self.duty_cycle = duty_cycle
		self.slepping = 2
		self.direction_port = dir_pin
		self.direction = direction
		self.exit = False

	def stop(self):
		self.exit = True
		self._stop_event.set()

    def stopped(self):
		self.exit = True
		return self._stop_event.is_set()

	def run(self, queue):
		GPIO.setwarnings(False)
		self.q = queue

		# Configurando GPIO
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(self.pin_out,GPIO.OUT)
		GPIO.setup(self.direction_port,GPIO.OUT)

		if self.direction:
			GPIO.output(self.direction_port, True)
		else:
			GPIO.output(self.direction_port, False)
		# Configurando o PWM
		self.PWM = GPIO.PWM(self.pin_out, self.frequency)
		self.PWM.start(self.duty_cycle)

		time.sleep(5)

		# cleanup
		self.close()

	def close(self):
		GPIO.cleanup()

