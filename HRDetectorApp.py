#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 17:40:33 2022

@author: mariamjabara
"""

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