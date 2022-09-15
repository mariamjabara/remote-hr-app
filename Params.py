#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 17:46:06 2022

@author: mariamjabara
"""

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
            