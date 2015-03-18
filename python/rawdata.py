# Larlite 
from larlite import larlite as fmwk
from ROOT import example
from ROOT import *

# numpy
import numpy as np

import sys

class RawData():
  """docstring for RawData"""
  def __init__(self):
    gSystem.Load("libLArLite_LArUtil")
    gSystem.Load("libargoneut_electrons_EventViewer.so")
    gSystem.Load("libExample_PyPackage.so")   
    self.init_geom()
    self.init_converter()
    self.init_proc()
    self.event=1
    self.nplanes=2
    self.filename = []

  def init_geom(self):
    larutil.LArUtilManager.Reconfigure(fmwk.geo.kArgoNeuT)
    self.aspectRatio = larutil.GeometryUtilities.GetME().TimeToCm() / larutil.GeometryUtilities.GetME().WireToCm()
    # self.aspectRatio = 0
  
  def init_converter(self):
    self.c2p = example.PyExample()   

  def init_proc(self):
    self.my_proc = fmwk.ana_processor()
    # Specify IO mode
    self.my_proc.set_io_mode(fmwk.storage_manager.kREAD)
    self.my_proc.add_process(fmwk.DrawRaw())

  def add_input_file(self, proc):
    self.filename.append(proc)
    self.my_proc.add_input_file(proc)  

  def proc_event(self, axes):
    if len(self.filename) == 0:
      print("ERROR, must include a file on command line or with button.")
      return False
    self.my_proc.process_event(self.event)
    # for p in xrange(0,self.nplanes):
    d0 = np.array(self.c2p.Convert(self.my_proc.get_process(0).getDataByPlane(0)))
    d1 = np.array(self.c2p.Convert(self.my_proc.get_process(0).getDataByPlane(1)))
    axes[0].imshow(d0.T,aspect=self.aspectRatio,cmap="jet")
    axes[1].imshow(d1.T,aspect=self.aspectRatio,cmap="jet")
    return True

  def get_img(self):
    if len(self.filename) == 0:
      print("ERROR, must include a file on command line or with button.")
      return False
    self.my_proc.process_event(self.event)
    # for p in xrange(0,self.nplanes):
    # d0 = np.array(self.c2p.Convert(self.my_proc.get_process(0).getDataByPlane(0)))
    # d1 = np.array(self.c2p.Convert(self.my_proc.get_process(0).getDataByPlane(1)))
    d = np.array(self.c2p.Convert(self.my_proc.get_process(0).getDataByPlane(0))),np.array(self.c2p.Convert(self.my_proc.get_process(0).getDataByPlane(1)))
    return d
