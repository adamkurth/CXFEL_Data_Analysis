import os
import h5py
import zmq
from PIL import Image
from streamz import Stream

def process_hdf5_file(file_path):
    with h5py.File(file_path, 'r') as hf:
        # List all datasets in the HDF5 file
        datasets = list(hf.keys())

        # Access and process the first dataset here as needed
        if datasets:
            data = hf[datasets[0]][:]
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
                img = Image.fromarray(processed_data)
                img.show()

if __name__ == "__main__":
    main()

