import RPi.GPIO as GPIO
import time
import sys

pin_out = int(sys.argv[1]) # 38
frequency = float(sys.argv[2])
duty_cycle = float(sys.argv[3])
sleep_time = float(sys.argv[4])
direction_port = int(sys.argv[5]) # 36
direction = float(sys.argv[6]) # 1 ou 0

# Configuração para não mostrar warnings na hora de rodar programa
GPIO.setwarnings(False)
 
# Configurando GPIO
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin_out,GPIO.OUT)
GPIO.setup(direction_port,GPIO.OUT)

if direction:
    GPIO.output(direction_port, True)
else:
    GPIO.output(direction_port, False)
# Configurando o PWM
PWM = GPIO.PWM(pin_out,frequency)
PWM.start(duty_cycle)
PWM.ChangeDutyCycle(duty_cycle)
time.sleep(sleep_time)

GPIO.cleanup()

