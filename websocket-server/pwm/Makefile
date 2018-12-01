default:
	make build
	make run

run:
	docker run --rm -v `pwd`:/code -it rasp-pwm bash

build:
	docker build -t rasp-pwm .
