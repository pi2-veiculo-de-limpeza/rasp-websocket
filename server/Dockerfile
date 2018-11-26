FROM python:3.6.7-alpine

ADD . /code/server
WORKDIR /code/server

# RUN apt-get update && apt-get install python-pip
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT python server.py