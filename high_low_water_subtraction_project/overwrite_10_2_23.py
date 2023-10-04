import os
import random
import string
import shutil
import numpy as np

print(os.getcwd())
# os.chdir('/Users/adamkurth/Documents/vscode/CXFEL Image Analysis')
############################################ 

def generate_text():
    column1 = ''.join(random.choice(string.ascii_letters) for _ in range(10))
    column2 = ''.join(random.choice(string.digits) for _ in range(3))
    column3 = ''.join(random.choice(string.punctuation) for _ in range(5))
    return f"{column1}\t{column2}\t{column3}"

def write_to(filename):
    with(filename, "w") as w:
        for _ in range(len(nrow)):
            w.write(generate_text())
    return None

#############################################

def load_stream(stream_name):
    global data_columns
    
    data_columns = {
    'h':[], 'k':[], 'l':[],
    'I':[], 'sigmaI':[], 'peak':[], 'background':[],
    'fs':[],'ss':[], 'panel':[]}      
    
    reading_peaks = False
    reading_geometry = False
    reading_chunks = True 
    
    try:
        stream = open(stream_name, 'r') 
        print("\nLoaded file successfully.", stream_name, '\n')
    except Exception as e: 
        print("\nAn error has occurred in load method:", str(e),'\n')
   
   
    for line in stream:
        if reading_chunks:
           if line.startswith('End of peak list'):
               reading_peaks = False
           elif line.startswith("   h    k    l          I   sigma(I)       peak background  fs/px  ss/px panel"):
               reading_peaks = True
           elif reading_peaks:
                try:
                    elements = line.split()
                    data_columns['h'].append(int(elements[0]))
                    data_columns['k'].append(int(elements[1]))
                    data_columns['l'].append(int(elements[2]))
                    data_columns['I'].append(float(elements[3]))
                    data_columns['sigmaI'].append(float(elements[4]))
                    data_columns['peak'].append(float(elements[5]))
                    data_columns['background'].append(float(elements[6]))
                    data_columns['fs'].append(float(elements[7]))
                    data_columns['ss'].append(float(elements[8]))
                    data_columns['panel'].append(str(elements[9]))
                except:
                    pass
        elif line.startswith('----- End geometry file -----'):
            reading_geometry = False
        elif reading_geometry:   
            try:
                par, val = line.split('=')
                if par.split('/')[-1].strip() == 'max_fs' and int(val) > max_fs:
                    max_fs = int(val)
                elif par.split('/')[-1].strip() == 'max_ss' and int(val) > max_ss:
                    max_ss = int(val)
            except ValueError:
                pass
        elif line.startswith('----- Begin geometry file -----'):
            reading_geometry = True
        elif line.startswith('----- Begin chunk -----'):
            reading_chunks = True   
    return data_columns


def retrieve(data_columns, *args):
    return [data_columns[col] for col in args if col in data_columns]


def duplicate_before_overwrite(filename):
    # taking filename and adding copy extension to it.
    base_file, extension = filename.rsplit('.',1)
    new_base_file = f'{base_file}_copy'
    new_filename = f'{new_base_file}.{extension}'
    duplicate = shutil.copyfile(filename, new_filename)
    return duplicate



# will eventually pass the data of another stream file through this method.
def over_write(stream_name, new_stream, *cols_to_overwrite):
    # duplicate_before_overwrite(stream_name) 
    # MAKE SURE YOUR RUNNING THIS SCRIPT IN THE DIRECTORY OF THE STREAM FILE. 
    
    high_stream_data = load_stream(stream_name)
    if not high_stream_data:
        return "Error has occured when reading low data stream"
    low_stream_data = load_stream(new_stream)
    
    if not low_stream_data:
        return "Error has occured when reading low data stream"
    
    for col in cols_to_overwrite: 
        if col in high_stream_data and col in low_stream_data:
            print('Wanting to read high input intensity, and overwrite to low intensity')
            print('BEFORE \n', high_stream_data[col], low_stream_data[col])
            high_stream_data[col] = low_stream_data[col]
            print('AFTER \n', high_stream_data[col], low_stream_data[col])
            
    return high_stream_data, low_stream_data


if __name__ == "__main__":    
    # dummy test will be the file above, but stream file is what is desired.
    
    filename1 = 'test_high_copy.stream'
    # data = load_stream(filename1)
    # if data: 
    #     h_high = data['h']
    #     k_high = data['k']
    #     l_high = data['l']
    #     I_high = data['I']
    #     sigmaI_high = data['sigmaI']
    #     peak_high = data['peak']
    #     background_high = data['background']
    #     fs_high = data['fs']
    #     ss_high = data['ss']    
    #     panel__high = data['panel']
        
    # select_col = retrieve(data_columns,'h','k', 'l')
    
    ############################
    filename2 = 'test_low_copy.stream'
    # select_col = retrieve(data_columns,'h','k', 'l')
    
    # file1 = load_stream(filename1)
    # file2 = load_stream(filename2)
  
    over_write(filename1, filename2,'I')
    # over_write(filename1,filename2,'I')


    
    
    # # duplicate_before_overwrite(filename)
    # grab_col = []
    
    # #find length of file
    # line_count = 0
    # with open(filename, 'r') as f: 
    #     for line in filename: 
    #         line_count += 1 
    
    # # # now retreiving the columns of random text generation
    # for line in range(line_count):
    #     random_text = generate_text()
    #     cols = random_text.split('\t')
    #     col3 = cols[2]
    #     grab_col.append(col3)
    # for entry in grab_col: 
    #     print(entry)
        
        
        
        
    # write_to = 'overwritten_test.txt'
    # with open(write_to, 'w') as w:
    #     w.write("h  k  l  I  sigma(I)  peak  background  fs/px  ss/px  panel\n")
    #     for i in range(len(h)):
    #         w.write(
    #             f"{h[i]} {k[i]} {l[i]} {I[i]} {sigmaI[i]} {peak[i]} {background[i]} {fs[i]} {ss[i]} {panel[i]} \n" 
    #             )
