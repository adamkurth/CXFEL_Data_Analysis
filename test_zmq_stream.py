#tcp://10.139.1.5:9999
#ZMQ STREAM

#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

import zmq, json, time


def ___init___():
    context  = zmq.Context()
    subscriber = context.socket(zmq.SUB)
    subscriber.bind("tcp://10.139.1.5:9999")
    subscriber.setsockopt(zmq.SUBSCRIBE, "")
    while True:
        print(subscriber.recv())
        print('main is working')
    
def send():
    context = zmq.Context()
    publisher = context.socket(zmq.PUB) 
    publisher.connect("tcp://10.139.1.5:9999")
    while True:
        publisher.send("Hello World")
        time.sleep(1)
        print('send is working')
        



# context = zmq.Context()

# #  Socket to talk to server
# print("Connecting to hello world server…")
# socket = context.socket(zmq.REQ)
# socket.connect("tcp://10.139.1.5:9999")

# #  Do 10 requests, waiting each time for a response
# for request in range(10):
#     print("Sending request %s …" % request)
#     socket.send(b"Hello")

#     #  Get the reply.
#     message = socket.recv()
#     print("Received reply %s [ %s ]" % (request, message))

