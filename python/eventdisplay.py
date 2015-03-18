#!/usr/bin/python

# Window Management
from Tkinter import *
import Tkinter as Tk
from tkFileDialog import askopenfilename
import ttk

# matplotlib stuff
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

from rawdata import *

# This is the main window:
root = Tk.Tk()
root.wm_title("Event Display")

# Set up the main figure
fig, axes = plt.subplots(2,1,figsize=(15,10))
fig.tight_layout()

# Two frames for now.  One for data, one for buttons and info
content = Tk.Frame(root)
display = Tk.Frame(content,width=700,height=1000)
info    = Tk.Frame(content,width=70, height=1000)

display = FigureCanvasTkAgg(fig, master=content)
display.show()


content.grid(column=0,row=0,sticky=(N,S,W,E))
info.grid(column=0,row=0,rowspan=20,sticky=(N,S,W))
display.get_tk_widget().grid(column=2,row=0,rowspan=20,sticky=(N,S,E))

event=IntVar()
run  =IntVar()
event.set(1)
run.set(1)

# Need to initialize the rawData object:
r = RawData()
r.event=event.get()

startingInput=False
# Pass any input files to the drawer:
for x in xrange(len(sys.argv)-1):
  r.add_input_file(sys.argv[x+1])
  startingInput=True

# Prepare the buttons:

def redraw():
  if r.proc_event(axes):
    display.draw()

# Define all of the functions that are mapped to buttons
def _quit():
    root.quit()     # stops mainloop
    root.destroy()  # this is necessary on Windows to prevent
                    # Fatal Python Error: PyEval_RestoreThread: NULL tstate

def _next_event():
  # Iterate the event
  event.set(event.get()+1)
  r.event=event.get()
  # Call the function to redraw
  redraw()
  print("Drew Event: " + str(event.get()))

def _prev_event():
  # Iterate the event
  event.set(event.get()-1)
  r.event=event.get()
  # And, redraw:
  redraw()
  print("Drew Event: " + str(event.get()))



def _goto_event():
  print("Go to (Run, Event) = (" + str(run.get()) +", " + str(event.get()) + ")" )
  r.event=event.get()
  redraw()


def _get_filename():
  filename = askopenfilename()
  r.add_input_file(filename)
  # print("Filename is ", filename)


# Put in labels for run and event number
_run_label = Tk.Label(master=info,text="Run")
_event_label = Tk.Label(master=info,text="Event")
_run_entry = Tk.Entry(master=info, width=7, textvariable=run)
_event_entry = Tk.Entry(master=info, width=7, textvariable=event)

_run_label.grid(column=0,row=0,columnspan=1,stick=(E,W))
_event_label.grid(column=1,row=0,columnspan=1,stick=(E,W))
_run_entry.grid(column=0,row=1,columnspan=1, sticky =(E,W))
_event_entry.grid(column=1,row=1,columnspan=1, sticky =(E,W))



_prev_button = Tk.Button(master=info,text='Prev',command=_prev_event)
_next_button = Tk.Button(master=info,text='Next',command=_next_event)
_filename_button = Tk.Button(master=info,text='Open File',command=_get_filename)
_goto_button = Tk.Button(master=info,text='Go To ...',command=_goto_event)
_quit_button = Tk.Button(master=info, text='Quit', command=_quit,activebackground="red")


_goto_button.grid(column=0,row=2,columnspan=2, sticky =(E,W))
_next_button.grid(column=0,row=3,columnspan=2, sticky =(E,W))
_prev_button.grid(column=0,row=4,columnspan=2, sticky =(E,W))
_filename_button.grid(column=0,row=5,columnspan=2, sticky =(E,W))
_quit_button.grid(column=0,row=6,columnspan=2,sticky =(E,W,S))





root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
content.columnconfigure(0, weight=1)
content.columnconfigure(1, weight=1)
content.columnconfigure(2, weight=1)
# content.rowconfigure(1, weight=1)


# If a file was passed on commandline, open the first event:
if startingInput:
  redraw()


Tk.mainloop()