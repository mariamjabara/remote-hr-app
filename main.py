#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 17:46:24 2022

@author: mariamjabara
"""

LARGE_FONT=("Verdana",12)
NORMAL_FONT=("Verdana",10)
SMALL_FONT=("Verdana",8)

import HRDetectorApp, Params, ResultsPage, SelectROIPage, StartPage, Utilities
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

app = HRDetectorApp()
app.geometry("800x750")
app.mainloop()