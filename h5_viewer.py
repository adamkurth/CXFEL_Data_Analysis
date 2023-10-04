import os
import zmq
import numpy as np
from PIL import Image
from streamz import Stream
import h5pyd

def process_hdf5_file(file_path):
    #Use the endpoint URL of hte hsds server
    #CHANGE if running different port
    endpoint = "http://127.0.0.1:5101"

    # Open the HDF5 file using h5pyd
    f = h5pyd.File(file_path, 'r', endpoint=endpoint)

    # List all datasets in the HDF5 file
    datasets = list(f.keys())

    # Access and process the first dataset here as needed
    if datasets:
        dataset_name = datasets[0]
        data = f[dataset_name][:]
        return data

def main():
    # Create a ZeroMQ publisher
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:5555")

    # Create a Stream for data processing
    s = Stream()

    # Define a function to process the data and publish it via ZeroMQ
    def publish_data(data):
        socket.send_pyobj(data)

    # Subscribe to the Stream and call the processing function
    s.map(publish_data)

    # Load all HDF5 files and process them
    hdf5_directory = "/home/labuser/Projects/Dectris/test/temp_data"
    for hdf5_file in os.listdir(hdf5_directory):
        hdf5_path = os.path.join(hdf5_directory, hdf5_file)
        if os.path.isfile(hdf5_path) and hdf5_file.endswith('.h5'):
            processed_data = process_hdf5_file(hdf5_path)
            if processed_data is not None:
                # Publish the data via the Stream
                s.emit(processed_data)

                # Display the image using PIL (assuming the data is an image)
                img = Image.fromarray(np.array(processed_data, dtype=np.uint16))
                img.show()

if __name__ == "__main__":
    main()
