FROM resin/raspberrypi3-alpine:latest

ADD . /code
WORKDIR /code

RUN sudo apt-get install python3-pip

RUN pip3 install -r requirements.txt

ENTRYPOINT [ "bash" ]