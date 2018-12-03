import requests
import json
import datetime



def integrate_peso_lixo(value_measured, time, token):

	data = {"peso": value_measured, "mission_id": "5c0083143545620001c9dfdf", "time_measuring": time}
	url = "http://18.216.157.143/peso"
	headers = {'Content-type': 'application/json', 'Authorization': token}
	result = requests.post(url, data=json.dumps(data), headers=headers)

	if result.status_code != 201:
		result = requests.post(url, data=json.dumps(data), headers=headers)
		print(result.status_code)
	else:
		print(result.status_code)
		

def integrate_monitory_volume_sensor_dump(value_measured, time,token):

	data = {"volume": value_measured, "mission_id": "5c0083143545620001c9dfdf", "time_measuring": time}
	url = "http://18.216.157.143/volume"
	headers = {'Content-type': 'application/json', 'Authorization': token}
	result = requests.post(url, data=json.dumps(data), headers=headers)

	if result.status_code != 201:
		result = requests.post(url, data=json.dumps(data), headers=headers)
		print(result.status_code)
	else:
		print(result.status_code)
		