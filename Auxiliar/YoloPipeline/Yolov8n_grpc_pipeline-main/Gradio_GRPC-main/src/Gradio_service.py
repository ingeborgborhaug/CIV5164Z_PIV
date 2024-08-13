import gradio as gr
from scipy.io import savemat,loadmat
import time
import numpy as np
import cv2
from pathlib import Path

from external import cleanup,FileIsReady,_DISPLAYIMG_PATH,_DISPLAYDATA_PATH,_SUBMIT_PATH

#Define the Gradio Interface
def gradio_function():

    #TODO: Here is where you can add your code to change the Gradio Interface
    with gr.Blocks() as demo:

        streamFrame = gr.Number(value=0,visible=False,interactive=False)

        with gr.Row():
            with gr.Column():
                input_type = gr.Dropdown(choices=["Image", "Stream", "Video"], label="Select Input Type")

                with gr.Column(visible=False) as Image_input:
                    img = gr.Image(sources="upload")
                with gr.Column(visible=False) as Stream_input:
                    stream = gr.Image(sources="webcam",streaming=True)
                    resetFrameCount = gr.Button(value='Reset frame Count')
                with gr.Column(visible=False) as Video_input:
                    vid = gr.Video()

            
            with gr.Column():
                display = gr.Image(label="YoloV8n Output")
                fileOutput = gr.File(label='Output .mat file')

        input_type.change(update_visibility,inputs=input_type,outputs=[Image_input,Stream_input,Video_input])
        
        img.change(gradio_GRPC_submit,inputs=[img,input_type],outputs=[])     
        stream.stream(gradio_GRPC_Streamsubmit,inputs=[stream,input_type,streamFrame],outputs=[streamFrame])
        vid.change(gradio_GRPC_Vidsubmit,inputs=[vid,input_type],outputs=[])

        resetFrameCount.click(ResetStreamFrameCount,inputs=[],outputs=[streamFrame])

        demo.load(gradio_GRPC_display,inputs=[], outputs=[display,fileOutput],show_progress='hidden')
        
    demo.launch()


def update_visibility(input_type):
    return gr.update(visible=input_type == "Image"), gr.update(visible=input_type == "Stream"), gr.update(visible=input_type == "Video")

#-----Image---------------------------------

#Function used to process the users data and outputs the desired data for the user
def gradio_GRPC_submit(inputImg,input_type):
    #TODO: Here is where you can add your code to change how you process Gradios inputs and how to read GRPC's saved data
    if (inputImg is None) or (input_type != "Image"):
        return
    
    sub_file = Path(_SUBMIT_PATH)
    while sub_file.is_file():
            time.sleep(0.01)

    # JPC - If image is bigger than 4Mb , resize it because of GRPC -Annotate image
    if np.ndarray.size(inputImg)>3900000:
        logging.info("Image too big")
        cv2.resize(inputImg,(1280,960))
        cv2.putText(inputImg, "Image > 4M, resized to 1080p", (50,50), fontFace = cv2.FONT_HERSHEY_COMPLEX, fontScale = 1.5, color = (250,225,100))
    #Save file in memory so GRPC can access it
    data_dict = {'im': inputImg,'frame': 0}
    savemat(_SUBMIT_PATH, data_dict)

    return

#-----Stream---------------------------------

#Function used to process the users data and outputs the desired data for the user
def gradio_GRPC_Streamsubmit(inputImg,input_type,frame):
    #TODO: Here is where you can add your code to change how you process Gradios inputs and how to read GRPC's saved data
    if (inputImg is None) or (input_type != "Stream"):
        return

    sub_file = Path(_SUBMIT_PATH)
    while sub_file.is_file():
            time.sleep(0.01)

    #Save file in memory so GRPC can access it
    data_dict = {'im': inputImg,'frame': frame}
    savemat(_SUBMIT_PATH, data_dict)

    return frame +1

def ResetStreamFrameCount():
    return 0

#-----Video---------------------------------

#Function used to process the users data and outputs the desired data for the user
def gradio_GRPC_Vidsubmit(inputVid,input_type):  
    if (inputVid is None) or (input_type != "Video"):
        return
    
    sub_file = Path(_SUBMIT_PATH)
    cap = cv2.VideoCapture(inputVid)
    amount_of_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    for i in range(amount_of_frames):

        #Make sure last frame has been sent to yolo
        while sub_file.is_file():
            time.sleep(0.01)
        
        #read frame
        _, frame = cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        #Save file in memory so GRPC can access it
        data_dict = {'im': frame,'frame': i}
        savemat(_SUBMIT_PATH, data_dict)

        yield

#-----Display---------------------------------

#Function used to process the users data and outputs the desired data for the user
def gradio_GRPC_display():
    while True:
        #Wait untill the display images is saved
        while not FileIsReady(_DISPLAYIMG_PATH):
            time.sleep(0.01)

        yield _DISPLAYIMG_PATH,_DISPLAYDATA_PATH
        
        #Make sure the Display directory is cleared
        cleanup("DispImg",0)
