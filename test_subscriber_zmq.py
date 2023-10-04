import zmq
import requests

context = zmq.Context()
subscriber = context.socket(zmq.SUB)
subscriber.connect("tcp://127.0.0.1:5000")  # Connect to the loopback address
subscriber.setsockopt_string(zmq.SUBSCRIBE, "")  # Subscribe to all messages

while True:
    message = subscriber.recv()
    image_url = message.decode('utf-8')
    
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            with open("received_image.h5", "wb") as f:
                f.write(response.content)
            print("Received image:", image_url)
        else:
            print("Failed to fetch image:", image_url)
    except Exception as e:
        print("Error:", str(e))
