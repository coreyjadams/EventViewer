
from fileInterface import fileInterface
from larlite import larlite as fmwk
import numpy as np
import sys
from ROOT import *


class rawDataInterface(object):
  """docstring for rawDataInterface"""
  def __init__(self):
    super(rawDataInterface, self).__init__()
    gSystem.Load("libEventViewer_RawViewer.so")
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
    if wire > 0 and wire < larutil.Geometry.GetME().Nwires(plane):
      return np.array(self._c2p.Convert(self._process.getWireData(plane,wire)))

  def setProducer(self, prod):
    self._producer = prod
    self._process.setProducer(prod)




class hitInterface(object):

  def __init__(self):
    super(hitInterface, self).__init__()
    # print "In the init function for the hit interface"
    gSystem.Load("libLArLite_LArUtil")
    self._process = fmwk.DrawHit()
    self._producer = ""
    self._nviews=larutil.Geometry.GetME().Nviews()
    self._c2p = fmwk.Converter()

  def get_hits(self, view):
    h = []
    # for i in range(0, self._nviews):
    h.append(np.array(self._c2p.Convert(self._process.getWireByPlane(view))))
    h.append(np.array(self._c2p.Convert(self._process.getHitStartByPlane(view))))
    h.append(np.array(self._c2p.Convert(self._process.getHitEndByPlane(view))))
    return h

  def setProducer(self, prod):
    self._producer = str(prod)
    self._process.setProducer(self._producer)

  def initialize(self):
    self._process.initialize()

class clusterInterface(object):

  def __init__(self):
    super(clusterInterface, self).__init__()
    # print "In the init function for the hit interface"
    self._process = fmwk.DrawCluster()
    self._producer = ""
    self._nviews=larutil.Geometry.GetME().Nviews()
    self._c2p = fmwk.Converter()
    self._clusterColors = [ 
                            # (0,255,255),  # teal - too close to wire colors
                            (0,147,147),  # dark teal
                            (0,0,252),   # bright blue
                            # (0,0,100), # navy blue - not great
                            (156,0,156), # purple
                            (255,0,255), # pink
                            (255,0,0),  #red
                            (175,0,0),  #red/brown
                            (252,127,0), # orange
                            (102,51,0), # brown
                            (127,127,127),  # dark gray
                            (210,210,210),  # gray
                            # (0,147,0), # medium green
                            (100,253,0) # bright green
                            ]



  def get_hits(self, view, cluster):
    h = []
    # for i in range(0, self._nviews):
    h.append(np.array(self._c2p.Convert(self._process.getWireByPlaneAndCluster(view,cluster))))
    h.append(np.array(self._c2p.Convert(self._process.getHitStartByPlaneAndCluster(view,cluster))))
    h.append(np.array(self._c2p.Convert(self._process.getHitEndByPlaneAndCluster(view,cluster))))
    return h

  def get_n_clusters(self,view):
    return self._process.getNClustersByPlane(view)

  def setProducer(self, prod):
    self._producer = str(prod)
    self._process.setProducer(self._producer)

  def initialize(self):
    self._process.initialize()


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
    else:
      self.init_geom()
    self._event = 0
    self._lastProcessed = 0
    self._hasFile = False
    
    # Generate blank data for the display if there is no raw:
    self._blankData = np.ones((larutil.Geometry.GetME().Nwires(0),larutil.Geometry.GetME().Nwires(0)/self._aspectRatio))
    self._daughterProcesses = dict()

  def init_geom(self):
    self._nviews=larutil.Geometry.GetME().Nviews()
    # Get the conversions
    self._time2Cm = larutil.GeometryUtilities.GetME().TimeToCm()
    self._wire2Cm = larutil.GeometryUtilities.GetME().WireToCm()
    self._aspectRatio = self._time2Cm / self._wire2Cm
    # Get the ranges:
    self._wRange = larutil.Geometry.GetME().Nwires(0)
    self._tRange = larutil.DetectorProperties.GetME().ReadOutWindowSize()

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

        # If the interface already exists, don't duplicate it
        if dataProduct in self._daughterProcesses:
          self._daughterProcesses.pop(dataProduct)
        # go through the list and add the interface needed:

        if dataProduct == 'wire':
          self._daughterProcesses.update({dataProduct : rawDataInterface()} )
          self._my_proc.add_process(self._daughterProcesses[dataProduct]._process)
          self._daughterProcesses[dataProduct].setProducer(producer)
        if dataProduct == 'hit':
          self._daughterProcesses.update({dataProduct : hitInterface()} )
          self._my_proc.add_process(self._daughterProcesses[dataProduct]._process)
          self._daughterProcesses[dataProduct].setProducer(producer)
          self._daughterProcesses[dataProduct].initialize()
        if dataProduct == 'cluster':
          self._daughterProcesses.update({dataProduct : clusterInterface()} )
          self._my_proc.add_process(self._daughterProcesses[dataProduct]._process)
          self._daughterProcesses[dataProduct].setProducer(producer)
          self._daughterProcesses[dataProduct].initialize()
      else:
        print "Failed to find producer ", producer
    else:
      print "Failed to find data product", dataProduct          
    pass
    self._my_proc.process_event(self._event)

  def remove_drawing_process(self,dataProduct):
    if dataProduct in self._daughterProcesses:
      self._daughterProcesses.pop(dataProduct)

  def processEvent(self):
    if self._lastProcessed != self._event:
      self._my_proc.process_event(self._event)
      self._lastProcessed = self._event

