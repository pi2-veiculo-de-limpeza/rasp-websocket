from websocket import create_connection

websocket_uri="ws://rasp-server:8000"

ws = create_connection( websocket_uri )

print "Sending 'Mario'..."
ws.send("Mario")
print "Sent"

print "Reeiving..."
result =  ws.recv()
print "Received '%s'" % result

ws.close()