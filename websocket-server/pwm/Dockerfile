FROM resin/rpi-raspbian:stretch-20181024
# FROM python:3-alpine3.8

ADD . /code
WORKDIR /code

RUN ln -s /usr/local/bin/pip2.7 /usr/local/bin/pip2

RUN apt-get update && apt-get install python-pip build-essential python-dev python-setuptools raspi-gpio python-rpi.gpio wiringpi -y 


RUN pip2 install -r requirements.txt