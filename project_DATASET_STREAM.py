#!/usr/bin/env python
import os
import sys
import numpy as np
import h5py as h5
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

#print working directory
wd = os.getcwd()
print('\nWorking directory: ', wd)
    
def load_file_h5():
    global filename         #scope outside of this method. 
    #filename = input("Please enter a filename to load: ")
    #FOR NOW
    filename = "DATASET1_8_16_23-1.h5"
    #filename =  "test_manipulate2HDF5.h5"
    #if filename is not within working directory
    if not os.path.exists(filename):
        print("File not found within working directory.")
        return
    
    #loading filename as h5 image
    try:
        with h5.File(filename, "r") as f: 
            print("\nLoaded file successfully.", filename)
    except Exception as e:
        print("\nAn error has occurred:", str(e))
        
        
        
class PeakThresholdProcessor: 
    #self method
    def __init__(self, image_array, threshold_value=0):
        self.image_array = image_array
        self.threshold_value = threshold_value
    #setter for threshold value
    def set_threshold_value(self, new_threshold_value):
        self.threshold_value = new_threshold_value
    #getter for for above threshold
    def get_coordinates_above_threshold(self):  
        coordinates = np.argwhere(self.image_array > self.threshold_value)
        return coordinates
    
class ArrayRegion:
    def __init__(self, array):
        self.array = array
        self.x_center = 0
        self.y_center = 0
        self.region_size = 0
    def set_peak_coordinate(self, x, y):
        self.x_center = x
        self.y_center = y
    def set_region_size(self, size):
        #limit that is printable in terminal
        self.region_size = size
        max_printable_region = min(self.array.shape[0], self.array.shape[1]) //2
        self.region_size = min(size, max_printable_region)
    def get_region(self):
        x_range = slice(self.x_center - self.region_size, self.x_center + self.region_size+1)
        y_range = slice(self.y_center - self.region_size, self.y_center + self.region_size+1)
        region = self.array[x_range, y_range]
        return region
    
 
        
def extract_region(image_array, region_size, x_center, y_center):
    extract = ArrayRegion(image_array)
    extract.set_peak_coordinate(x_center,y_center)
    extract.set_region_size(region_size)
    np.set_printoptions(floatmode='fixed', precision=10)
    np.set_printoptions(edgeitems=3, suppress=True, linewidth=200)
    region = extract.get_region()
    return region        
    
def coordinate_menu(image_array, threshold_value, coordinates, radius): 
    print("\nCoordinates above given threshold:", threshold_value, 'with radius: ', radius)
    for i, (x, y) in enumerate(coordinates):
        print(f"{i + 1}. ({x}, {y})")
        
    while True:
        choice = input("\nWhich coordinate do you want to process? (or 'q' to quit)\n")
        if choice == "q":
            print("Exiting")
            break
        
        try: 
            count = int(choice)-1
            if 0 <= count < len(coordinates):
                x,y = coordinates[count]
                print(f"\nProcessing - ({x}, {y})")
                print('Printing 9x9 two-dimensional array\n')
                
                #creates visualization if the array, of chosen peak
                display_region = extract_region(image_array, region_size=4, x_center=x, y_center=y)
                print('DISPLAY REGION \n', display_region, '\n')
                
                #segment is the area with the given radius that's passed through the function.
                segment = extract_region(image_array, region_size=radius, x_center=x, y_center=y)
                print ('SEGMENT \n', segment, '\n')
                
                # #creating boolean array of segment within the defined circle, so see which index is in the circle (to then be summed)
                # bool_array = in_circle(segment, radius,x_center=x, y_center=y)
                
                #returns boolean array of traversed values.
                # bool_square = in_square(segment)
                # print('BOOLEAN', '\n', bool_square, '\n') 
                square = np.zeros_like(segment, dtype=bool)
                
                ######start 3 ring integration
                values_array = extract_region(image_array, region_size=radius, x_center=x, y_center=y)
                
                total_sum = 0; skipped_point = None; count = 0
                #traverses through all row coordinates for every column
                for col_index in range(values_array.shape[0]):
                    for row_index in range(values_array.shape[1]):
                        if values_array[row_index, col_index]:
                            if col_index == radius and row_index == radius:
                                skipped_point = (col_index, row_index)  
                                print(f'Peak point to be skipped: ({row_index}, {col_index}) ', values_array[radius,radius])
                            else:
                                print(f'(row,col) ({row_index}, {col_index}) with a value of ', values_array[row_index, col_index])
                                square[count] = True
                                total_sum += values_array[row_index, col_index]
                                count += 1
                print('\n######################')
                print(square)
                
                print('Number of traversed cells', count)
                print('Peak point to be skipped:', skipped_point)
                print('Total sum:',total_sum)
                avg_values = total_sum / count
                print('Average surrounding peak:',avg_values)
                break
            else: 
                print("Invalid coordinate idex.")
        except ValueError:
            print("Invalid input. Enter a number of 'q' to quit.")


# traverses the array called segment (already with radius defined)
# creates array of false values, makes them true in traversing to ensure we are accumulating values properly.
def in_square(array):
    square = np.zeros_like(array, dtype=bool)
    print("Before inserting: \n", array)
    count = 0
    for i in square: #iterates rows
        for j in i: 
            j = True
            square[j] = True
    return square
    
   
   
   
if __name__ == "__main__":
    # testing on DATASET1_8_16_23-1.h5
    # load_file_h5()
    #filename = "test_manipulate2.stream-HDF5.h5"
    #filename =  "test_manipulate2HDF5.h5"
    filename = "DATASET1_8_16_23-1.h5"
    image_array = None
    
    # testing on DATASET1_8_16_23-1.h5
    
    #reading input h5 file for dataset1
    image = h5.File(filename, "r") 
    #image_array = None
    with h5.File(filename, "r") as f:
        #prints <HDF5 dataset "data": shape (4371, 4150), type "<f4">
        #dset = image["/data/data/"][()]
        dset = image["/entry/data/data"][()]
        #dset = image["entry/data/data"][()]     #returns np array of (4371,4150) of 0's
        image_array = np.array(dset)
        image_array_size = dset.shape
        print(image_array)
        image.close
        
        
       
       
    
####

threshold = PeakThresholdProcessor(image_array, threshold_value=7000)
print ("Original threshold value: ", threshold.threshold_value, "\n")
global coordinates
coordinates = threshold.get_coordinates_above_threshold()

# ######start 3 ring integration
radius1=2
radius2=3
radius3=4
coordinate_menu(image_array, 1000, coordinates, radius1)
coordinate_menu(image_array, 1000, coordinates, radius2)
coordinate_menu(image_array, 1000, coordinates, radius3)
