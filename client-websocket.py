import websocket
import random
import threading
import time

try:
    import Queue
except ImportError:
    import queue as Queue

try:
    import thread
except ImportError:
    import _thread as thread

class API_Websocket(threading.Thread):

    def __init__(self, uri, loop_time=1.0/60):

        self.max_retries = 10
        self.retries = self.max_retries
        self.q = Queue.Queue()
        self.timeout = loop_time
        super(API_Websocket, self).__init__()

        self.uri = uri
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(self.uri,
                                on_message = self.on_message,
                                on_error = self.on_error,
                                on_close = self.on_close)
        self.ws.on_open = self.on_open
    
    def onThread(self, function, *args, **kwargs):
        self.q.put((function, args, kwargs))

    def start(self):
        try:
            t = threading.Thread(target=self.ws.run_forever)
            t.start()
        except Exception:
            print(":)")

    def on_message(self, message):
        print("> " + message)

    def on_error(self, error):
        print("ERROR >")
        print(error)

    def on_close(ws):
        print("### closed ###")

    def on_open(self):
        def run(*args):
            while True:
                if Queue is type(None):
                    self.close_connection()
                    break
                
                try:
                    function, args, kwargs = self.q.get(timeout=self.timeout)
                    function(*args, **kwargs)
                    self.retries = self.max_retries
                except Queue.Empty:
                    if self.retries > 0:
                        self.idle()
                    else:
                        self.close_connection()
                        break

        try:
            thread.start_new_thread(run, ())
        except Exception:
            print(":D")

    def idle(self):
        if self.retries > 0:
            self.retries -= 1
        self.ping()
        time.sleep(1)
        pass

    def close_connection(self):
        self.ws.close()
        print("Connection closed...")

    def ping(self):
        message = "."
        print(message)
        # self.sendMessage(message)

    def hello(self):
        message = "Hello!"
        self.sendMessage(message)

    def volume(self, volume):
        message = "volume: %2f" % volume
        self.sendMessage(message)

    def distance(self, distance):
        message = "distance: %2f" % distance
        self.sendMessage(message)

    def battery(self, battery):
        message = "battery: %2f" % battery
        self.sendMessage(message)

    def sendMessage(self, message):
        try:
            print(message)
            self.ws.send(message)
        except sys.excepthook:
            print(":P")


class API():

    def __init__(self, uri="ws://rasp-server:8000"):
        print("Opening socket...")
        self.api = API_Websocket(uri=uri)

    def start(self):
        print("Starting...")
        self.api.start()

    def close(self):
        print("Closing...")
        self.api.onThread(API_Websocket.close_connection, self.api)

    def sendVolume(self, data):
        self.api.onThread(API_Websocket.volume, self.api, data)

    def sendDistance(self, data):
        self.api.onThread(API_Websocket.distance, self.api, data)

    def sendBattery(self, data):
        self.api.onThread(API_Websocket.battery, self.api, data)



api = API()
api.start()

api.sendVolume(30)
api.sendDistance(30)
time.sleep(2)

api.sendVolume(40)
api.sendDistance(500)
time.sleep(2)

api.close()

