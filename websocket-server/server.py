import asyncio
import websockets
import time

async def hello(websocket, path):
    while True:
        try:
            name = await websocket.recv()
            print("< " + name)

            greeting = "Server: " + name

            await websocket.send(greeting)
            print("> " + greeting)
            
            time.sleep(0.001)
        except websockets.exceptions.ConnectionClosed:
            print("end connection :D")
            break
    

start_server = websockets.serve(hello, '0.0.0.0', 8000)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()