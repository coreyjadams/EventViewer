
from fileInterface import fileInterface
from larlite import larlite as fmwk
import numpy as np
import sys
from ROOT import *



class rawDaqInterface(object):
  """docstring for rawDataInterface"""
  def __init__(self):
    super(rawDaqInterface, self).__init__()
    # gSystem.Load("libEventViewer_RawViewer.so")
    self._process = fmwk.DrawLariatDaq()
    self._producer = ""
    self._nviews=larutil.Geometry.GetME().Nviews()
    self._c2p = fmwk.Converter()
    self._hasFile = False
    self._lastProcessed = -1
    self._event = 0
    # self._process.setProducer(self._producer)

  def get_img(self):
    d = []
    for i in range(0,self._nviews):
      d.append(np.array(self._c2p.Convert(self._process.getDataByPlane(i))) )
      # print "got a plane, here is a sample: ", d[i][0][0]
    return d

  def get_wire(self, plane, wire):
    if plane > self._nviews:
      return
    if wire > 0 and wire < larutil.Geometry.GetME().Nwires(plane):
      return np.array(self._c2p.Convert(self._process.getWireData(plane,wire)))

  def set_input_file(self, file):
    self._file = file
    if file == None:
      return
    else:
      self._process.setInputFile(file)
      self._hasFile = True
      self._maxEvent = self._process.n_events()

  def processEvent(self,force = False):
    if self._lastProcessed != self._event or force:
      self._process.goToEvent(self._event)
      self._lastProcessed = self._event

  def next(self):
    # print "Called next"
    self._process.nextEvent()

  def prev(self):
    # print "Called prev"
    self._process.prevEvent()

  def getRunAndEvent(self):
    return self._process.run(),self._process.event_no()

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

  def get_clusters(self,view):
    # return a packaged up set of all the clusters
    clusters = []
    for clust in range(0, self.get_n_clusters(view)):
      clusters.append(self.get_hits(view,clust))
    return clusters

  def get_hits(self, view, cluster):
    h = []
    # for i in range(0, self._nviews):
    h.append(np.array(self._c2p.Convert(self._process.getWireByPlaneAndCluster(view,cluster))))
    h.append(np.array(self._c2p.Convert(self._process.getHitStartByPlaneAndCluster(view,cluster))))
    h.append(np.array(self._c2p.Convert(self._process.getHitEndByPlaneAndCluster(view,cluster))))
    return h

  def get_n_clusters(self,view):
    return self._process.getNClustersByPlane(view)

  def get_range(self,view):
    return np.array(self._c2p.Convert(self._process.GetWireRange(view))), np.array(self._c2p.Convert(self._process.GetTimeRange(view)))

  def setProducer(self, prod):
    self._producer = str(prod)
    self._process.setProducer(self._producer)

  def initialize(self):
    self._process.initialize()


class baseDataInterface(object):
  """docstring for baseDataInterface"""
  def __init__(self, geometry,mode):
    super(baseDataInterface, self).__init__()
    # self.arg = arg
    gSystem.Load("libLArLite_LArUtil")
    # initialize the c to numpy converter
    # initialize the ana processor
    if geometry == "argoneut":
      self.config_argo()
    elif geometry == "lariat":
      self.config_lariat()
    else:
      self.init_geom()
    self._lastProcessed = -1
    # self._hasFile = False
    
    # Generate blank data for the display if there is no raw:
    self._blankData = []
    for v in range(0, self._nviews):
      self._blankData.append(np.ones((larutil.Geometry.GetME().Nwires(v),larutil.Geometry.GetME().Nwires(v)/self._aspectRatio)))

    if mode == "daq":
      self._dataHandle = rawDaqInterface()
    else:
      self._dataHandle = larliteInterface()

    # hold the drawing levels for each plane:
    self._levels = []
    if geometry == "argoneut": 
      self._levels.append( (-15,15 ) )
      self._levels.append( (-10,30 ) )
    if geometry == "lariat":
      self._levels.append( (-15,15 ) )
      self._levels.append( (-10,30 ) )
      self._tRange = 1536
    else:
      self._levels.append( (-15,15 ) )
      self._levels.append( (-15,15 ) )
      self._levels.append( (-10,30 ) )


  def init_geom(self):
    self._nviews=larutil.Geometry.GetME().Nviews()
    # Get the conversions
    self._time2Cm = larutil.GeometryUtilities.GetME().TimeToCm()
    self._wire2Cm = larutil.GeometryUtilities.GetME().WireToCm()
    self._aspectRatio = self._time2Cm / self._wire2Cm
    # Get the ranges:
    self._wRange = []
    for v in range(0, self._nviews):
      self._wRange.append(larutil.Geometry.GetME().Nwires(0))
    self._tRange = larutil.DetectorProperties.GetME().ReadOutWindowSize()

    # self.xmin
  
  def config_argo(self):
    larutil.LArUtilManager.Reconfigure(fmwk.geo.kArgoNeuT)
    self.init_geom()

  def config_lariat(self):
    larutil.LArUtilManager.Reconfigure(fmwk.geo.kArgoNeuT)
    self.init_geom()


class larliteInterface(object):
  """docstring for larliteInterface"""
  def __init__(self):
    super(larliteInterface, self).__init__()
    self.init_proc()
    self._fileInterface = fileInterface()
    self._daughterProcesses = dict()
    self._hasFile = False
    self._event = 0
    self._lastProcessed = -1
    
  def init_proc(self):
    self._my_proc = fmwk.ana_processor()
    self._my_proc.set_verbosity(larlite.msg.kERROR)
    self._my_proc.set_io_mode(fmwk.storage_manager.kREAD)
    # Set up a storage manager to handle event validation:
    self._mgr = fmwk.storage_manager()

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
        self.processEvent(True)
      else:
        print "Failed to find producer ", producer
    else:
      print "Failed to find data product", dataProduct          

  def set_input_file(self, file):
    self.init_proc()
    if self._fileInterface.fileExists(file):
      self._fileInterface.pingFile(file)
    else:
      print "Requested file does not exist: ", file
      return
    self._my_proc.add_input_file(file) 
    self._mgr.add_in_filename(file)
    self._mgr.set_io_mode(self._mgr.kREAD)
    self._mgr.open()
    self._mgr.next_event()
    self._maxEvent = self._mgr.get_entries()
    self._hasFile=True


  def remove_drawing_process(self,dataProduct):
    if dataProduct in self._daughterProcesses:
      self._daughterProcesses.pop(dataProduct)

  def processEvent(self,force = False):
    if len(self._daughterProcesses) == 0:
      self._mgr.go_to(self._event)
      return
    if self._lastProcessed != self._event or force:
      self._my_proc.process_event(self._event)
      self._mgr.go_to(self._event)
      self._lastProcessed = self._event

  def getRunAndEvent(self):
    if not self._mgr.is_open():
      return 0,0

    # Define the larlite types to get:
    types = dict()
    # types.update({'vertex': fmwk.event_vertex})
    types.update({'hit': fmwk.event_hit})
    types.update({'cluster': fmwk.event_cluster})


    # Get an event vector out of this file, and use it to
    # get the run and event info
    # Any old data product will do, but don't use wires
    keys = self._fileInterface.getListOfKeys()
    for key in keys:
      # print key
      # print keys[key][0]
      if key in types:
        d = self._mgr.get_data(types[key])(keys[key][0])
        return d.run(), d.event_id()
    # d = mgr.get_data(fmwk.event_hit)("cccluster")
