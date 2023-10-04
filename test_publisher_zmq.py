import zmq
import time
import os

context = zmq.Context()
publisher = context.socket(zmq.PUB)
publisher.bind("tcp://127.0.0.1:5000")  # Bind to the loopback address

image_directory = "/home/labuser/Projects/Dectris/test/temp_data"
last_uploaded = None

while True:
    new_images = [f for f in os.listdir(image_directory) if os.path.isfile(os.path.join(image_directory, f))]
    
    if new_images != last_uploaded:
        for image_file in new_images:
            image_url = f"http://10.139.1.5/data/{image_file}"
            message = image_url.encode("utf-8")
            publisher.send(message)
            print("Sent: ", image_url)
        last_uploaded = new_images 
        
    time.sleep(1)
    
