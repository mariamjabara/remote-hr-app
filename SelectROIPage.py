#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 17:42:22 2022

@author: mariamjabara
"""

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