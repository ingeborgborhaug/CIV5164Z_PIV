import io
from scipy.io import loadmat,savemat
import cv2
import generic_box_pb2
import time
import os
from pathlib import Path
import io

#TODO: Can change the Directories to save the data
_SUBMIT_PATH = '/dev/shm/submit.mat'
_DISPLAYIMG_PATH = '/dev/shm/display.png'
_DISPLAYDATA_PATH = '/dev/shm/display.mat'


def submit():
    #TODO:Here is where you can add your code to combine Gradio's inputs to send the GRPC message
    #Wait untill the _SUBMIT_PATH has a file to load
    while not FileIsReady(_SUBMIT_PATH):
        time.sleep(0.01)

    with open(_SUBMIT_PATH, 'rb') as fp:
        image_bytes = fp.read()

    return generic_box_pb2.Data(file=image_bytes)


def display(imgfile):
    #TODO:Here is where you can add your code to save the GRPC's message for Gradio to read
    dados = loadmat(io.BytesIO(imgfile)) 

    img = dados['im0']

    disp_file = Path(_DISPLAYIMG_PATH)
    while disp_file.is_file():
        time.sleep(0.01)
    cv2.imwrite(_DISPLAYIMG_PATH, img) 

    return


'''------------------------------------------Auxiliary Functions--------------------------------------------------------'''

#Function to Clean up files
def cleanup(DispOrSub,wait):
    #Check if cleanup if for the display directory or the submit directory
    if DispOrSub == 'DispImg':
        dir = _DISPLAYIMG_PATH
    elif DispOrSub == 'Sub':
        dir = _SUBMIT_PATH
    elif DispOrSub == 'DispMat':
        dir = _DISPLAYDATA_PATH
    else:
        return
    
    # Delay the cleanup to ensure the files have been sent
    time.sleep(wait)

    if os.path.isfile(dir):
        # Delete the temporary directory
        os.remove(dir)


'''Helper function to make sure a file is ready to read
        Due to the asyncronous behaviour between the gradio and GRPC servers,
        It's useful to have a function that makes sure a file is fully written.
'''
def FileIsReady(path):
    my_file = Path(path)

    #Make sure the file is in directory
    if not my_file.is_file():
        return False

    #Check if the file size changes
    #if it does we assume its still being written
    file_size = my_file.stat().st_size
    time.sleep(0.1)
    new_size = my_file.stat().st_size

    #if file size hasn't changed we return True
    if new_size == file_size:
        return True
    
    return False