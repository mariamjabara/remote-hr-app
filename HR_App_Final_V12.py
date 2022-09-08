#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May  6 15:15:19 2020

@author: mariamjabara
"""

# Install notes:
#
# 1) Download and install Anaconda.
# For Windows, the following link can be used (link found from https://www.anaconda.com/products/individual#windows , bottom of the page):
# https://repo.anaconda.com/archive/Anaconda3-2020.07-Windows-x86_64.exe (Oct. 29, 2020)
#
# 2) On Windows, using the Windows search tool, find "Anaconda Prompt" and select Run as Administrator. 
#    Or open a console on a Mac/Linux OS. 
#
# 3) In the Anaconda prompt, perform the following instructions:
# conda update -n base conda -c defaults     
# conda create -n HeartRateExtractionApp python=3.7 
# conda activate HeartRateExtractionApp
# conda install anaconda
# conda install --channel conda-forge opencv
#
# Note: from the above commands, only the command "conda activate HeartRateExtractionApp"  will be required in later executions.  
#
# 4) Download HandbrakeCLI.exe using one of the multi-platform links available at https://handbrake.fr/downloads2.php .
# For Windows: https://github.com/HandBrake/HandBrake/releases/download/1.3.3/HandBrakeCLI-1.3.3-win-x86_64.zip (Oct. 29, 2020).
# Extract the .exe file and copy it in the same directory as this python script (e.g. "HR_App_Final_V12.py").
 
# To start execution on Windows, :
# - from the Anaconda prompt, navigate (change drive and directory) to the directory where this python script is located.
# - type:  python HR_App_Final_V12.py 
# - At run time, it is a good practice to position the python GUI window on the computer screen so that both the GUI window and the conda console can be displayed. This helps to follow the execution of the program (text displayed on console while processing, etc.)

# Known issue:
# - On Windows, if the code is started from within the Spyder IDE platform (not required), the GUI controls do not execute properly. 
#	But the code runs fine from a Windows Anaconda prompt. On a Mac, the code runs fine from the Spyder IDE. 
# Additional notes:
# - The code currently does not perform face or skin tracking. 
# - To speed up execution, the conversion to constant fps could be computed for only the desired video frames, instead of for the whole video file
#	(ex. using --start-at --stop-at (in sec.) https://handbrake.fr/docs/en/latest/cli/command-line-reference.html).
#   But since we only compute this once and then we save the resulting video with constant fps, this is less critical,
#	especially if the user wants to try different time ranges.


LARGE_FONT=("Verdana",12)
NORMAL_FONT=("Verdana",10)
SMALL_FONT=("Verdana",8)

import tkinter as tk
from tkinter import filedialog 
from tkinter import ttk 
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.widgets import RectangleSelector
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import cv2
import numpy as np
import sys
from sys import platform
import time
import os.path
import subprocess
import os


fps=30.0 # desired frame per second rate after conversion to constant frame rate 
desired_resolution_BPM=0.1 # (was 0.01) (frequency resolution in BPM), maximum allowed frequency distance ("computational resolution") between points in FFT 

# only for debugging with Spyder under Windows  
run_in_spyder_with_hardcoded_param_values_to_overwrite_GUI_values=0  # 0 is normal execution, 1 is for execution in Spyder under Windows, where GUI fields parameters are not correctly received, so overwritten by hardcoded values (for debugging)
start_time_hardcoded=10.0
end_time_hardcoded=50.0  
segment_size_seconds_hardcoded=10.0
segment_update_time_hardcoded=1.0
BPM_range_low_hardcoded=60.0
BPM_range_high_hardcoded=100.0
            
c_x1 = 0.0
c_x2 = 0.0
c_y1 = 0.0
c_y1 = 0.0

getROI_was_called=0 # to detect case where user presses "next" before "load video" in 1st page, and then asks for processing without ROI selection
            

def sprintf(format, *args):  # so that the same s=sprintf("%3.2f",x) as in C can be used, for old programmers
    s = format % args  
    return s
           
def popUpMessage(msg):
    popup = tk.Tk()
    
    def leavemini():
        popup.destroy()
        
    popup.wm_title("!")
    label = ttk.Label(popup, text=msg,font=NORMAL_FONT)
    label.pack(side="top",fill="x", pady=10)
    B1 = ttk.Button(popup,text = "Okay", command = leavemini)
    B1.pack()
    popup.mainloop()
    

class HRDetectorApp(tk.Tk): #in brackets, what the class inherits
    def __init__(self,*args,**kwargs): #this will always load when we run the program. self is implied args = unlimited vars. kwargs are keywords arguments (dictionaries)

        tk.Tk.__init__(self,*args,**kwargs)
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True) #pack into top, fill into entire top space, and expand will expand into the whole window. fill into the area you packed.

        container.grid_rowconfigure(0, weight=1) #min size zero, weight is priority
        container.grid_columnconfigure(0,weight=1)

        self.frames = {}
        self.shared_data = {"filename": tk.StringVar(), "isClicked": tk.StringVar(), "x1": tk.IntVar(), "isConfirmed": tk.StringVar(), "start": tk.DoubleVar(), "end": tk.DoubleVar(), "update": tk.DoubleVar(), "segmentSize": tk.DoubleVar(), "bpm_low": tk.DoubleVar(),"bpm_high": tk.DoubleVar()}
		
        for F in (StartPage, SelectROIPage, ResultsPage):

            frame = F(container,self)

            self.frames[F] = frame

            frame.grid(row=0,column=0, sticky="nsew") #sticky = alignment + stretch, north south east west

        self.show_frame(StartPage)
        self.title("Heart Rate Detection")

    def show_frame(self,cont):
        frame=self.frames[cont]
        frame.tkraise()

    def get_page(self, page_class):
        return self.frames[page_class]


class StartPage(tk.Frame):
    def __init__(self,  parent: tk.Widget, controller: HRDetectorApp):
        tk.Frame.__init__(self,parent)
        self.filename = controller.shared_data['filename'] # use the same object for filename here as in SelectROIPage
        self.isClicked = controller.shared_data['isClicked']
        self.startTime = controller.shared_data['start'] 
        
        tk.Label(self, text = "1. Enter the START time in seconds to specify the video frame to be displayed (next page) and the default start time of the processing. If you would like to see the first video frame and by default analyze the video from the beginning, simply leave the value at 0. \n 2. Click 'Load a Video', select a video and wait until the 'work in progress' icon disappears, then click 'Next'. \n The video will be converted to a constant frame rate. If the constant frame rate converted video file already exists (with suffix '_30_fps.avi'), i.e., if no 'work in progress' icon is showing, you can click 'Next' right after selecting a video.", wraplength = 600, relief="sunken", background = "pale green",fg="black",).pack(side = "top", pady =15)

        
        startLabel = tk.Label(self, text = "START time, frame to display (seconds):").pack(side = "top")
        start = tk.Entry(self,textvariable=self.startTime)
        start.pack(side='top',pady = (0,5))
    
        
        
        
        ttk.Button(self,text="Load a Video", command=self.openFile).pack()
        ttk.Button(self,text ="Next", command = lambda: controller.show_frame(SelectROIPage)).pack()
        
      
    
        self.startTime.set(0.0)

    def openFile(self):
        try:
            name = filedialog.askopenfilename(title="Select an Mp4 Video", filetypes =(("Mp4 Files", "*.mp4"),))
            self.filename.set(name)
            self.isClicked.set("True")
            if len(self.filename.get())!=0:            
                print('filename in StartPage: {}'.format(self.filename.get()))
            
            
        except:
            print("Something went wrong when reading Mp4 file!")
      
                
def line_select_callback(eclick, erelease):
    'eclick and erelease are the press and release events'
    
    global c_x1, c_x2, c_y1, c_y2
        
    
    x1, y1 = eclick.xdata, eclick.ydata
    x2, y2 = erelease.xdata, erelease.ydata
      
    c_x1 = x1
    c_x2 = x2
    c_y1 = y1
    c_y2 = y2
    
    print("(%3.2f, %3.2f) --> (%3.2f, %3.2f)" % (x1, y1, x2, y2))
    
    print(" The button you used were: %s %s" % (eclick.button, erelease.button))
    
    
def toggle_selector(event):
    print(' Key pressed.')
    if event.key in ['Q', 'q'] and toggle_selector.RS.active:
        print(' RectangleSelector deactivated.')
        toggle_selector.RS.set_active(False)
        toggle_selector.RS.set_visible(False)
        toggle_selector.RS.update()
    if event.key in ['A', 'a'] and not toggle_selector.RS.active:
        print(' RectangleSelector activated.')
        toggle_selector.RS.set_active(True)
        toggle_selector.RS.set_visible(True)
        toggle_selector.RS.update()
    
    
def mycallback(event):
    if toggle_selector.RS.active:
        toggle_selector.RS.update()       


class SelectROIPage(tk.Frame):   
    
    def __init__(self,  parent: tk.Widget, controller: HRDetectorApp):
        tk.Frame.__init__(self,parent)
        self.controller = controller 
        self.filename = controller.shared_data['filename']
        self.isConfirmed = controller.shared_data['isConfirmed']
        self.startTime = controller.shared_data['start'] 
        self.endTime = controller.shared_data['end'] 
        self.updateTime = controller.shared_data['update']
        self.segmentSize  = controller.shared_data['segmentSize']
        self.bpmLow = controller.shared_data['bpm_low']
        self.bpmHigh = controller.shared_data['bpm_high']
        self.canvas = None
        self.fig = Figure(figsize=(5,5),dpi=100)


                
        self.x1 = controller.shared_data['x1']
        tk.Label(self, text = "Click & drag on the image to select a Region of Interest (R.O.I.) and enter START and END times for video processing. If no END time is provided, the whole video will be processed from the START time until the end of the video. The displayed frame corresponds to the START time that was specified in the previous page (i.e., when a video was loaded). To change the frame displayed: press 'back', change START time, and re-load video.", wraplength = 600, relief="sunken", background = "pale green",fg="black",).pack(pady= 15) # text assigns a permanent value
        
        returnButton = ttk.Button(self, text="Back", command = lambda: controller.show_frame(StartPage)).pack(side = "top", anchor = 'w')
        tk.Label(self, text = "After entering your parameters and selecting the Region of Interest, click 'Confirm Selection & Process Video'. Then once the 'work in progress' icon has disappeared, you may click the 'View Results' button. You may need to re-size (e.g. maximize) the Results window to view the plots properly.", wraplength = 600, relief="sunken", background = "pale green",fg="black",).pack(side = "bottom", anchor = 's',pady=15)
        processButton = ttk.Button(self, text = "2. View Results", command = lambda: controller.show_frame(ResultsPage)).pack(side = "bottom", anchor = 's')
        confirmROIButton = ttk.Button(self, text="1. Confirm Selection & Process Video", command = self.confirmSelection).pack(side = "bottom", anchor = 's')
                
        self.endTime.set(0.0) 
        self.segmentSize.set(10.0) 
        self.updateTime.set(1.0)
        self.bpmLow.set(60.0)
        self.bpmHigh.set(100.0)
       
        
        segmentLabel = tk.Label(self, text = "Segment size (seconds, normally 6 to 20, default 10):").pack(side = "top")
        segment_size_time = tk.Entry(self, textvariable = self.segmentSize)
        segment_size_time.pack(side = "top")
        
        updateLabel = tk.Label(self, text = "Update time (seconds, default 1.0):").pack(side = "top")
        update_time = tk.Entry(self, textvariable = self.updateTime)
        update_time.pack(side = "top")

        BPM_low_Label = tk.Label(self, text = "BPM Lower Bound (default 60):").pack(side = "top")
        BPM_low = tk.Entry(self, textvariable = self.bpmLow)
        BPM_low.pack(side = "top")

        BPM_high_Label = tk.Label(self, text = "BPM Upper Bound (default 100):").pack(side = "top")
        BPM_high = tk.Entry(self, textvariable = self.bpmHigh)
        BPM_high.pack(side = "top")
        
        end = tk.Entry(self,textvariable=self.endTime)
        end.pack(side='bottom',pady = (0,15))
        endLabel = tk.Label(self, text = "END time of processing (seconds):").pack(side = "bottom")
        
        start = tk.Entry(self,textvariable=self.startTime)
        start.pack(side='bottom',pady = (0,5))
        startLabel = tk.Label(self, text = "START time of processing (seconds):").pack(side = "bottom")
         
        self.filename.trace("w", lambda *args: self.getROI())
              
		
        
    def confirmSelection(self):
        self.isConfirmed.set("True")
      
        
          
    def getROI(self):

        global getROI_was_called
        global fps				  
                
         
        if len(self.filename.get())==0:
            print("\n\nNo video has been selected and loaded! Try again...\n\n") 
            return

        getROI_was_called=1 # to detect case where user presses "next" before "load video" in 1st page, and then asks for processing without ROI selection

        convertedPath = self.filename.get()+'_'+str(int(fps))+'_fps.avi'
        
        # check if constant fps file .avi already exists for selected video
        if os.path.isfile(convertedPath):
            video = cv2.VideoCapture(str(self.filename.get())+'_'+str(int(fps))+'_fps.avi')
            
        else: # convert selected video to constant fps
        
            # Possible values for codec -e: x264, x264_10bit, x265, x265_10bit, x265_12bit, mpeg4, mpeg2, VP8, VP9, theora
            # Possible values for --encoder-preset (listed here for x264): ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow, placebo
            #  (to see list of --encoder-preset possible values: HandBrakeCLI.exe --encoder-preset-list x264 (or other codec))
            # Optional -q: quality setting,  50 (low quality) to 0 (highest quality), default is 20 (ok for DVD copy  https://www.tweaking4all.com/video/handbrake-optimizing-video-encoding-h264/ )

            if platform == "win32": # Windows               
                # HandBrakeCLI.exe if run under Windows, with HandBrakeCLI.exe in same directory as python script
                cmd=sprintf("HandBrakeCLI.exe -i \"%s\" -e x264 --encoder-preset ultrafast -q 20 --cfr -r %d -o \"%s\"", str(self.filename.get()), np.int(fps), str(self.filename.get())+'_'+str(int(fps))+'_fps.avi')                 
            elif platform == "darwin": # OS X               
                # HandBrakeCLI.exe if run under a Mac
                current_dir = os.getcwd()
                cmd=sprintf("/usr/local/bin/HandBrakeCLI -i \"%s\" -e x264 --encoder-preset ultrafast -q 20 --cfr -r %d -o \"%s\"", str(self.filename.get()), np.int(fps), str(self.filename.get())+'_'+str(int(fps))+'_fps.avi') 
            else:  # platform == "linux" or platform == "linux2"
                # HandBrakeCLI.exe if run under Linux (NOT TESTED YET)
                current_dir = os.getcwd()
                cmd=sprintf("/usr/local/bin/HandBrakeCLI -i \"%s\" -e x264 --encoder-preset ultrafast -q 20 --cfr -r %d -o \"%s\"", str(self.filename.get()), np.int(fps), str(self.filename.get())+'_'+str(int(fps))+'_fps.avi') 

            if subprocess.call(cmd, shell=True) != 0:
                print("\n\nError during system execution of HandBrakeCLI.exe, please try again!\n\n")
                #sys.exit() #or not
            video = cv2.VideoCapture(str(self.filename.get())+'_'+str(int(fps))+'_fps.avi')       

          
        # Display a frame so that the user will be able to select a ROI later     
        
        if not video.isOpened():
            print("\n\nCould not open video. Try again...\n\n")
            #sys.exit()
        # Read one frame.
        frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT)) 
        if(self.startTime.get() > (frames-1)/fps):
            print("\nCannot have a start_time greater than the duration of the video. Try again ...\n\n") 
            #sys.exit()
        else: 
            video.set(cv2.CAP_PROP_POS_FRAMES,round(self.startTime.get()*fps)) # jump to start_frame in video             
            ok, im = video.read()
            if not ok:
                print("\n\nCannot read video file. Try again...\n\n")
                #sys.exit()
            
        try: 
            self.canvas.get_tk_widget().pack_forget()
        except AttributeError: 
            pass   
                    
        self.fig.clear()
        self.fig.set_tight_layout(True)
        a = self.fig.add_subplot(111)
        
        a.imshow(cv2.cvtColor(im, cv2.COLOR_BGR2RGB))
                   
        self.canvas = FigureCanvasTkAgg(self.fig,self)

        toggle_selector.RS = RectangleSelector(a, line_select_callback,
                                               drawtype='box', useblit=False,
                                               button=[1, 3],  # don't use middle button
                                               minspanx=5, minspany=5,
                                               spancoords='pixels',
                                               interactive=True)
        self.canvas.mpl_connect('key_press_event', toggle_selector)
        self.canvas.mpl_connect('draw_event', mycallback)

        self.canvas.draw()       

        self.canvas.get_tk_widget().pack(side = tk.TOP, fill = tk.BOTH, expand = True)
        
        self.canvas._tkcanvas.pack(side = tk.TOP, fill = tk.BOTH, expand = True)
               

class ResultsPage(tk.Frame):
    def __init__(self,  parent: tk.Widget, controller: HRDetectorApp):
        tk.Frame.__init__(self,parent)
        self.controller = controller
        self.isConfirmed = controller.shared_data['isConfirmed']
        self.filename = controller.shared_data['filename']
        self.startTime = controller.shared_data['start'] 
        self.endTime = controller.shared_data['end'] 
        self.updateTime = controller.shared_data['update']
        self.segmentSize  = controller.shared_data['segmentSize']
        self.bpmLow = controller.shared_data['bpm_low']
        self.bpmHigh = controller.shared_data['bpm_high']
        self.canvas = None
        self.myFig = Figure(figsize=(5,5),dpi=100)						  
        self.params = tk.StringVar()
        self.avgHR = tk.StringVar()	 
        self.paramLabel = None
        self.avgHRLabel = None		

        returnButton = ttk.Button(self, text="Back", command = lambda: controller.show_frame(SelectROIPage)).pack(side = "top", anchor = 'w')

        self.isConfirmed.trace("w", lambda *args: self.test())
        
         
        
    def test(self):
    
        global c_x1, c_x2, c_y1, c_y2, getROI_was_called
    
         
        if getROI_was_called==0:
            print("\n\nNo video has been selected and loaded! Press 'Back' and 'Load a video' and try again...\n\n") 
            return

        ok = True

        video = cv2.VideoCapture(str(self.filename.get())+'_'+str(int(fps))+'_fps.avi')
        frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        print("Total nb. video frames in video: " + str(frames))	
        print("fps: " + str(fps))	
        
      
        #PARAMS
        if run_in_spyder_with_hardcoded_param_values_to_overwrite_GUI_values ==0:    
            start_time = self.startTime.get()
            end_time  = self.endTime.get()            
            segment_size_seconds = self.segmentSize.get()
            segment_update_time = self.updateTime.get()
            BPM_range_low=self.bpmLow.get() # in beats per minute, determines range of frequencies to look for in the FFT
            BPM_range_high=self.bpmHigh.get() # max value = fps/2*60
        else:
            start_time=start_time_hardcoded
            end_time=end_time_hardcoded              
            segment_size_seconds = segment_size_seconds_hardcoded
            segment_update_time = segment_update_time_hardcoded
            BPM_range_low=BPM_range_low_hardcoded
            BPM_range_high=BPM_range_high_hardcoded          

		
        #TIME RANGE ERROR HANDLING:
        if(start_time < 0.0):
            print("\nCannot have negative start_time. Try again ...\n\n")		
            return

        if(start_time > (frames-1)/fps):
            print("\nCannot have a start_time greater than the duration of the video. Try again ...\n\n") 
            return
            
        if(end_time <= 0.0):
            print("end_time set to end of video") 
            end_time = (frames-1)/fps

        if(end_time > (frames-1)/fps):
            print("\nCannot have an end_time greater than the duration of the video. Try again ...\n\n") 
            return
            
        if(end_time - start_time < segment_size_seconds):
            print("\nend_time - start_time < segment_size_seconds. Try again ...\n\n") 
            return
         
        if(segment_size_seconds < 1.0):
            print("\nsegment_size_seconds < 1.0. Try again ...\n\n") 
            return
            
        if(segment_update_time < 0.1):
            print("\nsegment_update_time < 0.1. Try again ...\n\n") 
            return
            
        if(segment_update_time >  segment_size_seconds):
            print("\nsegment_update_time >  segment_size_seconds. Try again ...\n\n") 
            return

            
        print("Start time : %3.2f" % start_time)
        start_frame = round(start_time*fps)
        video.set(cv2.CAP_PROP_POS_FRAMES, start_frame) # jump to start_frame in video 


        segment_size_frames=  round(segment_size_seconds*fps)
        segment_update_frames=round(segment_update_time*fps)
 
        end_frame = round(end_time*fps) # first estimated value, will be updated later based on segment length and segment_update

        nb_segments = 1+ np.floor(((end_frame-start_frame+1)-segment_size_frames)/segment_update_frames,dtype=float) 
        nb_segments = int(nb_segments) 
    
        end_frame = start_frame + segment_size_frames-1 + (nb_segments-1) * segment_update_frames # update based on segment length and segment_update
        end_time = np.float(end_frame+1)/fps  # one frame added artificially here for rounded end_time display value, matching user's entry, also giving correct t_bpm values later  

        print("End time : %3.2f" % end_time) 
        print("Nb. video frames to process: " + str(end_frame-start_frame+1))           
        print("Segment size: " + str(segment_size_seconds))
        print("Segment update time (shift): " + str(segment_update_time))              
        print("Number of segments: " + str(nb_segments)) 

        
        #BPM RANGE ERROR HANDLING:
        if(BPM_range_low < 30.0):
            print("\nBPM_range_low < 30.0. Try again ...\n\n") 
            return
            
        if(BPM_range_high > 150.0):
            print("\nBPM_range_high > 150.0. Try again ...\n\n") 
            return
            
        if(BPM_range_high < BPM_range_low):
            print("\nBPM_range_high < BPM_range_low. Try again ...\n\n") 
            return


        #  ROI ERROR HANDLING:
        if ((c_x1==0.0) and (c_x2==0.0)):
            print("\nNo ROI selected (with mouse). Try again ...\n\n") 
            return
        
        
        # Extract ROI, compute mean, and save ROI to video
        
        c_x1_int = int(c_x1)
        c_y1_int = int(c_y1)
        w = int(c_x2 - c_x1)
        h = int(c_y2 - c_y1)
        x = []
        	
        start = time.time()
        ROIvideosize = (w,h) 
        ROIfourcc = cv2.VideoWriter_fourcc('M', 'J', 'P','G')                    
        ROIout = cv2.VideoWriter('ROI.avi', ROIfourcc, fps, ROIvideosize)      
        for i in range(end_frame-start_frame+1):

            ok, frame = video.read()  
                
            height, width, layers = frame.shape
 
            (B,G,R) = cv2.split(frame)
                
            # save ROI frames to file                
            roiG = G[c_y1_int:c_y1_int+h, c_x1_int:c_x1_int+w]
            roiB = B[c_y1_int:c_y1_int+h, c_x1_int:c_x1_int+w]
            roiR = R[c_y1_int:c_y1_int+h, c_x1_int:c_x1_int+w]                
            ROIout.write(cv2.merge((roiB,roiG,roiR)))														 
				
            #Calculate Average Pixel Value of the Bounding Box:
			# use green channel 
            meanPixelValue = np.mean(roiG)
            x.append(meanPixelValue)
				
        ROIout.release()
        print("ROI extraction completed, execution time: %3.2f" % (time.time()-start))
              
        
        #WRITING RAW DATA TO TXT FILE:
        outputData = open(str(self.filename.get())+"_RAWDATA_.txt","w+")
        for i in range(end_frame-start_frame+1):
            outputData.write(str(x[i])+"\n")
        outputData.close()

        x = np.asarray(x, dtype = float)        
        x = np.reshape(x,(len(x),1))
        
        
        #PROCESS THE ROI AVERAGES, USING FFT:
        fft_size = 2**(np.ceil((np.log(1/(desired_resolution_BPM/60/fps))/np.log(2))))
        fft_size=int(fft_size)
        start_freq_index=int(np.round(BPM_range_low/60/fps*fft_size))
        end_freq_index=int(np.round(BPM_range_high/60/fps*fft_size))
        BPM_range_low = np.float(start_freq_index)/np.float(fft_size)*fps*60.0 # update, real BPM edge value
        BPM_range_high = np.float(end_freq_index)/np.float(fft_size)*fps*60.0 # update, real BPM edge value 

        print("Lower BPM bound : %3.2f" % BPM_range_low)    
        print("Higher BPM bound : %3.2f" % BPM_range_high)         
        print("Low freq index bound: " + str(start_freq_index))
        print("High freq index bound: " + str(end_freq_index))
        
        ffts = np.zeros((nb_segments,(end_freq_index - start_freq_index + 1)))
        window=np.hamming(np.floor(segment_size_frames))
        window = np.reshape(window, (segment_size_frames,1))
        
        for i in range(nb_segments):
            start_frame_index = i*segment_update_frames
            end_frame_index = start_frame_index + segment_size_frames
            tmp = x[start_frame_index:end_frame_index]
            tmp = tmp - np.mean(tmp) #important because there is a huge DC component which "leaks" with sidelobes over other components (undesirable windowing effect)
            windowed_tmp = tmp*window
            fft_tmp= np.absolute(np.fft.fft(np.transpose(windowed_tmp), fft_size)) # FFT, with zero padding 
            fft_tmp_sliced = fft_tmp[:,start_freq_index:end_freq_index+1]
            ffts[i] = fft_tmp_sliced
            
            
        #Find BPM from max peaks in frequency:
            
        measured_BPMs=np.zeros((nb_segments,1))

        for i in range(nb_segments):
            max_index = np.argmax(ffts[i,:])
            measured_BPMs[i]= (start_freq_index+max_index)/fft_size*fps*60
        
       
        #plotting BPM over TIME:
        
        try: 
            self.canvas.get_tk_widget().pack_forget()
        except AttributeError: 
            pass   			 
        
        self.myFig.clear()
        self.myFig.set_tight_layout(True)
        a1 = self.myFig.add_subplot(221)
        a2 = self.myFig.add_subplot(222)
        a3 = self.myFig.add_subplot(223)
        a4 = self.myFig.add_subplot(224)
        
        t_meanROI = np.linspace(start_time,end_time,end_frame-start_frame+1,True)

        a1.plot(t_meanROI,x)
        a1.set_ylabel("Amplitude")
        a1.set_xlabel("Time (seconds)")
        a1.title.set_text("Mean pixel value in Region of Interest (green channel)")
        a1.grid()
        
        
        t_bpm = np.linspace(((segment_size_seconds/2)+start_time),((end_time - segment_size_seconds/2)),len(measured_BPMs),True) #timescale from first to last segment center time
        
        a2.plot(t_bpm,measured_BPMs)
        a2.set_ylabel("BPM")
        a2.set_xlabel("Time (seconds)")
        a2.title.set_text("Extracted Heart Rate")
        a2.grid()

        a2.set_ylim([(BPM_range_low),(BPM_range_high)])
        
        print("Time Stamps (s):")
        for i in t_bpm:
            print("%3.1f " % i, end='')			
        print("", end='\n')
        
        print("Measured BPMs:")
        for i in measured_BPMs:
            print("%3.1f " % i[0], end='')				
        print("", end='\n')
        
        maxValfft = np.amax(ffts)
		#timescale from first to last segment center, with offsets so that center of each "band" displayed is at segment center
        a3.imshow(np.transpose(ffts),extent =[start_time+segment_size_seconds/2-segment_update_time/2, end_time - segment_size_seconds/2+segment_update_time/2,BPM_range_low, BPM_range_high] ,cmap='YlGnBu', vmin=0.0, vmax=(np.ceil(maxValfft)), origin='lower', aspect='auto', alpha=1.0) 
        a3.set_xlabel("Time (seconds)")
        a3.set_ylabel("BPM")
        a3.title.set_text("Spectrogram from all processed segments")
        a3.grid()

        bpm_ffts = np.linspace(BPM_range_low,BPM_range_high,len(ffts[0]),True)
        for i in range(nb_segments):
            a4.plot(bpm_ffts,ffts[i],linewidth=0.5)
        a4.set_xlabel("BPM")
        a4.set_ylabel("Magnitude")
        a4.title.set_text("FFTs from all processed segments")
        a4.grid()

        
 #      GETTING AVG BPM: 
        
        tmp = 0
        for i in range(nb_segments):
            tmp += measured_BPMs[i]
        avgHRtxt = sprintf("Average heart rate: \n%3.1f\n\n",np.float(tmp/len(measured_BPMs)))  
        
        self.avgHR.set(avgHRtxt)
        print(self.avgHR.get())
        
        segmentSizeLabel = "Segment Size (seconds): "+ str(segment_size_seconds)
        segmentUpdateLabel = "Segment Update Time (seconds): " + str(segment_update_time)
            
        self.canvas = FigureCanvasTkAgg(self.myFig,self)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side = tk.TOP, fill = tk.BOTH, expand = True)
        try: 
            self.toolbar.destroy()

        except AttributeError: 
            pass 
        self.toolbar=NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        self.canvas._tkcanvas.pack(side = tk.TOP, fill = tk.BOTH, expand = True)
   
        try: 
            
            self.avgHRLabel.destroy()
            self.paramLabel.destroy()

        except AttributeError: 
            pass			 
    

        paramsTxt = "Parameters: \n" + segmentSizeLabel + "\n" + segmentUpdateLabel + "\n"
        self.params.set(paramsTxt)
        self.avgHRLabel = tk.Label(self, textvariable = self.avgHR, relief="sunken", background = "steel blue",fg="white",)
        self.avgHRLabel.pack(side = "bottom") 
        self.paramLabel = tk.Label(self, textvariable = self.params, relief="sunken", background = "SpringGreen4",fg="white",)
        self.paramLabel.pack(side = "bottom", anchor="w",pady=5,padx=5) 
         
        
        
app = HRDetectorApp()
app.geometry("800x750")
app.mainloop()
