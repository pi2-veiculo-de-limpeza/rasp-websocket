from gps3 import gps3

class SensorGPS(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.daemon = True
		self.gps_socket = gps3.GPSDSocket()
		self.data_stream = gps3.DataStream()

	def run(self):
		self.gps_socket.connect()
		self.gps_socket.watch()

		for new_data in self.gps_socket:
			if new_data:
				self.data_stream.unpack(new_data)
				print('Longitude = {lon} °'.format(lon=self.data_stream.TPV['lon']))
				print('Latitude = {lat} °'.format(lat=self.data_stream.TPV['lat']))
			time.sleep(0.1)
