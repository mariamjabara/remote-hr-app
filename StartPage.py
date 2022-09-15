#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 17:41:49 2022

@author: mariamjabara
"""

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