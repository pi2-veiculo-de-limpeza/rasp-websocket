default:
	make build
	make run-server
	make run-client

build:
	make build-client
	make build-server

# Client
build-client:
	docker build -t rasp/pi2 .
client:
	docker network create rasp-ws || true
	docker run --rm -v `pwd`:/code --network="rasp-ws" -it rasp/pi2

# Server
build-server:
	docker build -t websocket-server/pi2 websocket-server
server:
	docker network create rasp-ws || true
	docker run --rm -p 8000:8000 -v `pwd`:/code --network="rasp-ws" --name rasp-server -it websocket-server/pi2
