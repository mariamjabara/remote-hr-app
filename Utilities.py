#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 11 17:43:59 2022

@author: mariamjabara
"""
            

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