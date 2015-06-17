
from PyQt4.QtGui import QFileDialog
from data import wire

from ROOT import evd

# This class exists as the basic interface for controlling events
# Defines a lot of functions but the final implementation needs to be done
# by a specific mode of running
# This base class is meant to provide information interface
# This class is also the manager for file interface, and contains the general functions.
# It needs to be extended independently for daq or reco viewing
class event(object):
  """docstring for event"""
  def __init__(self,):
    super(event, self).__init__()
    self._run = 0
    self._event = 0


    self._lastProcessed = -1

  def next(self):
    print "Called next event"

  def prev(self):
    print "Called prev event"

  def run(self):
    return self._run

  def event(self):
    return self._event

  def setRun(self, r):
    self._run = r

  def setEvent(self,e):
    self._event = e

  def goToEvent(self,e):
    print "Requested jump to event ", e




class lariat_manager(event, wire):
  """docstring for lariat_manager"""
  def __init__(self, geom, file=None):
    super(lariat_manager, self).__init__()

    # override the wire drawing process for lariat
    self._process = evd.DrawLariatDaq()
    self._hasFile = False
    self._file = ""

    self._geom = geom


    if file != None:
      self.setInputFile(file)

  def selectFile(self):
    filePath = str(QFileDialog.getOpenFileName())
    self.setInputFile(filePath)
    print "Selected file is ", filePath

  # override the functions from manager as needed here
  def next(self):
    # print "Called next"
    self._process.nextEvent()  

  def prev(self):
    # print "Called prev"
    self._process.prevEvent()    

  def setInputFile(self, file):
    self._file = file
    if file == None:
      return
    else:
      self._process.setInput(file)
      self._hasFile = True

  def processEvent(self,force = False):
    if not self._hasFile:
      return
    if self._lastProcessed != self._event or force:
      self._process.goToEvent(self._event)
      self._lastProcessed = self._event



  def getPlane(self,plane):
    if self._hasFile:
      return self.getPlane(plane)


  def hasWireData(self):
    if self._hasFile:
      return True
    return False

class rawDaqInterface(object):
  """docstring for rawDataInterface"""
  def __init__(self):
    super(rawDaqInterface, self).__init__()
    # gSystem.Load("libEventViewer_RawViewer.so")
    self._process = fmwk.DrawLariatDaq(LARIAT_TIME_TICKS)
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

