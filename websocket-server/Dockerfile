# FROM python:3.6.7-alpine
FROM resin/rpi-raspbian:stretch-20181024

ADD . /code/websocket-server
WORKDIR /code/websocket-server

RUN ln -s /usr/local/bin/pip2.7 /usr/local/bin/pip2

RUN apt-get update && apt-get install python-pip python-setuptools -y
RUN pip2 install -r requirements.txt

# RUN apt-get update && apt-get install python-pip
# RUN pip install --upgrade pip
# RUN pip install -r requirements.txt

ENTRYPOINT python server.py