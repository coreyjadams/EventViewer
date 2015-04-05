
from fileInterface import fileInterface
from larlite import larlite as fmwk
import numpy as np
import sys
from ROOT import *


class rawDataInterface(object):
  """docstring for rawDataInterface"""
  def __init__(self):
    super(rawDataInterface, self).__init__()
    self._process = fmwk.DrawRaw()
    self._producer = ""
    self._nviews=larutil.Geometry.GetME().Nviews()
    self._c2p = fmwk.Converter()

    # self._process.setProducer(self._producer)

  def get_img(self):
    d = []
    for i in range(0,self._nviews):
      d.append(np.array(self._c2p.Convert(self._process.getDataByPlane(i))) )
    return d

  def get_wire(self, plane, wire):
    if plane > self._nviews:
      return
    if wire > 0 and wire < 240:
      return np.array(self._c2p.Convert(self._process.getWireData(plane,wire)))

  def setProducer(self, prod):
    self._producer = prod
    self._process.setProducer(prod)

class hitInterface(object):

  def __init__(self):
    super(hitInterface, self).__init__()
    self._process = fmwk.DrawHit()
    self._producer = ""
    self._nviews=larutil.Geometry.GetME().Nviews()
    self._c2p = fmwk.Converter()

  def get_hits(self):
    h = []
    for i in range(0, self._nviews):
      view = []
      view.append(np.array(self._c2p.Convert(self._process.getWireByPlane())))
      view.append(np.array(self._c2p.Convert(self._process.getWireByPlane())))
      view.append(np.array(self._c2p.Convert(self._process.getWireByPlane())))
      h.append(view)
    return h


class baseDataInterface(object):
  """docstring for baseDataInterface"""
  def __init__(self, argo=True):
    super(baseDataInterface, self).__init__()
    # self.arg = arg
    gSystem.Load("libLArLite_LArUtil")
    # initialize the c to numpy converter
    # initialize the ana processor
    self.init_proc()
    self._fileInterface = fileInterface()
    if argo:
      self.config_argo()
    self.init_geom()
    self._event = 1
    self._lastProcessed = 0
    self._hasFile = False
    
    # Generate blank data for the display if there is no raw:
    self._blankData = np.ones((larutil.Geometry.GetME().Nwires(0),larutil.Geometry.GetME().Nwires(0)/self._aspectRatio))
    self._daughterProcesses = dict()

  def init_geom(self):
    self._aspectRatio = larutil.GeometryUtilities.GetME().TimeToCm() / larutil.GeometryUtilities.GetME().WireToCm()
    self._nviews=larutil.Geometry.GetME().Nviews()
    # self.xmin
  
  def config_argo(self):
    larutil.LArUtilManager.Reconfigure(fmwk.geo.kArgoNeuT)
    self.init_geom()

  def init_proc(self):
    self._my_proc = fmwk.ana_processor()
    self._my_proc.set_io_mode(fmwk.storage_manager.kREAD)

  def set_input_file(self, file):
    self._my_proc.reset()
    self.init_proc()
    if self._fileInterface.fileExists(file):
      self._fileInterface.pingFile(file)
    else:
      print "Requested file does not exist: ", file
      return
    self._my_proc.add_input_file(file) 
    self._hasFile=True

  def add_drawing_process(self, dataProduct, producer):
    if not self._hasFile:
      return
    # First, check that the key/products exists
    if dataProduct in self._fileInterface.getListOfKeys():
      if producer in self._fileInterface.getListOfKeys()[dataProduct]:
        # go through the list and add the interface needed:
        if dataProduct == 'wire':
          self._daughterProcesses.update({dataProduct : rawDataInterface()} )
          self._my_proc.add_process(self._daughterProcesses[dataProduct]._process)
          self._daughterProcesses[dataProduct].setProducer(producer)
        if dataProduct == 'hit':
          self._daughterProcesses.update({dataProduct : HitInterface()} )
          self._daughterProcesses[dataProduct].setProducer(producer)
          self._my_proc.add_process(self._daughterProcesses[dataProduct])
      else:
        print "Failed to find producer ", producer
    else:
      print "Failed to find data product", dataProduct          
    pass
    self._my_proc.process_event()


  def processEvent(self):
    if self._lastProcessed != self._event:
      self._my_proc.process_event(self._event)
      self._lastProcessed = self._event

