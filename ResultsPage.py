#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 17:42:49 2022

@author: mariamjabara
"""

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