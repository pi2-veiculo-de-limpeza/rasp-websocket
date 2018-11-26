# FROM python:2.7.15-alpine
FROM resin/rpi-raspbian:stretch-20181024

ADD . /code
WORKDIR /code

RUN ln -s /usr/local/bin/pip2.7 /usr/local/bin/pip2

RUN apt-get update && apt-get install python-pip
RUN pip2 install -r requirements.txt

ENTRYPOINT python client-websocket.py