from websocket_server import WebsocketServer as WSServer

class WebsocketServer():

	def __init__(self, host='0.0.0.0', PORT=8000):

		self.websocket = WSServer(PORT, host=host)

		self.websocket.set_fn_new_client(self.new_client)
		self.websocket.set_fn_client_left(self.client_left)
		self.websocket.set_fn_message_received(self.message_received)
		
	def start(self):
		try:
			self.websocket.run_forever()
		except KeyboardInterrupt:
			pass
		

	# Called for every client connecting (after handshake)
	def new_client(self, client, server):
		print("New client connected and was given id %d" % client['id'])
		self.websocket.send_message_to_all("Hey all, a new client has joined us")

	# Called for every client disconnecting
	def client_left(self, client, server):
		print("Client(%d) disconnected" % client['id'])

	# Called when a client sends a message
	def message_received(self, client, server, message):
		array_message = message.split(',')
		command = array_message[0]

		if command == 'calibrate':
			if self.calibrate:
				self.calibrate(array_message[1])
		elif command == 'right':
			if self.rightMotor:
				self.rightMotor(array_message[1], array_message[2])
		elif command == 'left':
			if self.leftMotor:
				self.leftMotor(array_message[1], array_message[2])
		elif command == 'stand-by':
			if self.turnOffVehicle:
				self.turnOffVehicle()
			else:
				print('error: callback not setted for ' + command)
		elif command == 'turn-on':
			if self.turnOn:
				self.turnOn()
			else:
				print('error: callback not setted for ' + command)
		elif command == 'turn-off-mat':
			if self.turnOffMat:
				self.turnOffMat()
			else:
				print('error: callback not setted for ' + command)
		elif command == 'turn-on-mat':
			if self.turnOnMat:
				self.turnOnMat()
			else:
				print('error: callback not setted for ' + command)

	def rightMotorCallback(self, callback):
		self.rightMotor = callback
	
	def leftMotorCallback(self, callback):
		self.leftMotor = callback

	def turnOffVehicleCallback(self, callback):
		self.turnOffVehicle = callback

	def turnOnMatCallback(self, callback):
		self.turnOnMat = callback

	def turnOffMatCallback(self, callback):
		self.turnOffMat = callback

	def turnOnCallback(self, callback):
		self.turnOn = callback

	def calibrateCallback(self, callback):
		self.calibrate = callback