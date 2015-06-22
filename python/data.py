
from PyQt4 import QtGui
from larlite import larlite as fmwk
from ROOT import evd
import numpy as np
import pyqtgraph as pg


# These classes provide the basic interfaces for drawing objects
# It's meant to be inherited from for specific instances
# There is a class for drawing the following things:
#   - Raw wire data
#   - a collection of rectangles (hits and clusters)
#   - markers (vertices, endpoints, etc)
#   - splines (for projecting tracks, etc.)

class dataBase(object):
  """basic class from which data objects inherit"""
  def __init__(self):
    super(dataBase,self).__init__()
    self._productName = "null"
    self._producerName = "null"
    self._process = None
    
    # This is the (clunky) converter to native python
    self._c2p = evd.Converter()

  def productName(self):
    return self._productName

  def producerName(self):
    return self._producerName

  def setProducer(self,name):
    self._producerName = name


class wire(dataBase):
  """docstring for wire"""
  def __init__(self):
    super(wire, self).__init__()
    self._process = None
    
    # This is the (clunky) converter to native python
    self._c2p = evd.Converter()

  def get_img(self):
    d = []
    for i in range(0,self._nviews):
      d.append(np.array(self._c2p.Convert(self._process.getDataByPlane(i))) )
      # print "got a plane, here is a sample: ", d[i][0][0]
    return d

  def getPlane(self,plane):
    return np.array(self._c2p.Convert(self._process.getDataByPlane(plane)))

  def getWire(self, plane, wire):
    return np.array(self._c2p.Convert(self._process.getWireData(plane,wire)))

class recoWire(wire):
  def __init__(self):
    super(recoWire,self).__init__()
    self._process = evd.DrawRaw()
    self._process.initialize()

class recoBase(dataBase):
  """docstring for recoBase"""
  def __init__(self):
    super(recoBase, self).__init__()
    self._drawnObjects = []
    self._process = None

  def init(self):
    self._process.initialize()


  def clearDrawnObjects(self,view_manager):
    for view in view_manager.getViewPorts():
      thisPlane = view.plane()
      for hit in self._drawnObjects[thisPlane]:
        view._view.removeItem(hit)

    # clear the list:
    self._drawnObjects = [] 

  # override set producer
  def setProducer(self, producer):
    self._producerName = producer
    self._process.setProducer(str(producer))

  def getDrawnObjects(self):
    return self._drawnObjects

  def drawObjects(self,view_manager):
    pass

class hit(recoBase):
  """docstring for hit"""
  def __init__(self):
    super(hit, self).__init__()
    self._productName = 'hit'
    self._process = evd.DrawHit()
    self._brush = (0,0,0)
    self.init()

  # this is the function that actually draws the hits.
  def drawObjects(self,view_manager):

    for view in view_manager.getViewPorts():
      self._drawnObjects.append([])
      thisPlane = view.plane()
      # First get the hit information:
      wireList       = self._c2p.Convert(self._process.getWireByPlane(thisPlane) )
      timeStartList  = self._c2p.Convert(self._process.getHitStartByPlane(thisPlane) )
      timeEndList    = self._c2p.Convert(self._process.getHitEndByPlane(thisPlane) )

      for i in xrange(len(wireList)):
        # Draws a rectangle at (x,y,xlength, ylength)
        r = QtGui.QGraphicsRectItem(wireList[i], timeStartList[i], 1, timeEndList[i]-timeStartList[i])

        # # New Way
        # r.setPen(pg.mkPen(brush,width=2))
        # # r.setBrush(pg.mkColor((255,255,255)))

        # Old Way:
        r.setPen(pg.mkPen(None))
        r.setBrush(pg.mkColor(self._brush))
        self._drawnObjects[thisPlane].append(r)
        view._view.addItem(r)



# This class wraps the hit object to allow them to all function together
class connectedBox(QtGui.QGraphicsRectItem):
  """docstring for connectedBox"""
  def __init__(self, *args, **kwargs):
    super(connectedBox, self).__init__(*args)
    self.setAcceptHoverEvents(True)
    self._isHighlighted = False
      

  def hoverEnterEvent(self, e):
    self._ownerHoverEnter(e)

  def hoverLeaveEvent(self,e):
    self._ownerHoverExit(e) 

  def mouseDoubleClickEvent(self,e):
    self._toggleHighlight()

  def connectOwnerHoverEnter(self, ownerHoverEnter):
    self._ownerHoverEnter = ownerHoverEnter

  def connectOwnerHoverExit(self, ownerHoverExit):
    self._ownerHoverExit = ownerHoverExit

  def connectToggleHighlight(self, ownerTH):
    self._toggleHighlight = ownerTH

class boxCollection(QtGui.QGraphicsItem):
  # This class wraps a collection of hits and connects them together
  # it can draw and delete itself when provided with view_manager
  def __init__(self):
    self._color = (0,0,0)
    self._plane = -1
    self._listOfHits = []
    self._isHighlighted = False

  def setColor(self,color):
    self._color = color

  def setPlane(self,plane):
    self._plane = plane

  def hoverEnter(self, e):
    for hit in self._listOfHits:
      hit.setPen(pg.mkPen((0,0,0),width=1))

  def hoverExit(self, e):
      if self._isHighlighted:
          return
      for hit in self._listOfHits:
          hit.setPen(pg.mkPen(None))

  def toggleHighlight(self):
      self._isHighlighted = not self._isHighlighted

  def drawHits(self,view_manager,wireList,timeStartList,timeEndList):
    view = view_manager.getViewPorts()[self._plane]
    for i in xrange(len(wireList)):
      # Draws a rectangle at (x,y,xlength, ylength)
      r = connectedBox(wireList[i], timeStartList[i], 1, timeEndList[i]-timeStartList[i])
      r.setPen(pg.mkPen(None))
      r.setBrush(pg.mkColor(self._color))
      self._listOfHits.append(r)
      view._view.addItem(r)

      # Connect the hit's actions with the clusters functions
      r.connectOwnerHoverEnter(self.hoverEnter)
      r.connectOwnerHoverExit(self.hoverExit)
      r.connectToggleHighlight(self.toggleHighlight)

  def clearHits(self,view_manager):
    view = view_manager.getViewPorts()[self._plane]
    for hit in self._listOfHits:
      view._view.removeItem(hit)
    self._listOfHits = []

class cluster(recoBase):
  """docstring for cluster"""
  def __init__(self):
    super(cluster, self).__init__()
    self._productName = 'cluster'
    self._process = evd.DrawCluster()
    self.init()

    self._listOfClusters = []
    # Defining the cluster colors:
    self._clusterColors = [ 
                            (0,147,147),  # dark teal
                            (0,0,252),   # bright blue
                            (156,0,156), # purple
                            (255,0,255), # pink
                            (255,0,0),  #red
                            (175,0,0),  #red/brown
                            (252,127,0), # orange
                            (102,51,0), # brown
                            (127,127,127),  # dark gray
                            (210,210,210),  # gray
                            (100,253,0) # bright green
                          ]   

  # this is the function that actually draws the cluster.
  def drawObjects(self,view_manager):
    for view in view_manager.getViewPorts():
      colorIndex = 0
      # get the plane
      thisPlane = view.plane()
      # extend the list of clusters
      self._listOfClusters.append([])
      # loop over the clusters in this plane:
      for i_cluster in xrange(self._process.getNClustersByPlane(thisPlane)):

        wireList       = self._c2p.Convert(self._process.getWireByPlaneAndCluster(thisPlane,i_cluster))
        timeStartList  = self._c2p.Convert(self._process.getHitStartByPlaneAndCluster(thisPlane,i_cluster))
        timeEndList    = self._c2p.Convert(self._process.getHitEndByPlaneAndCluster(thisPlane,i_cluster))

        # Now make the cluster
        cluster = boxCollection()
        cluster.setColor(self._clusterColors[colorIndex])
        cluster.setPlane(thisPlane)

        # draw the hits in this cluster:
        cluster.drawHits(view_manager,wireList,timeStartList,timeEndList)

        self._listOfClusters[thisPlane].append(cluster)

        colorIndex += 1
        if colorIndex >= len(self._clusterColors):
          colorIndex = 0

  def clearDrawnObjects(self,view_manager):
    for plane in self._listOfClusters:
      for cluster in plane:
        cluster.clearHits(view_manager)


import collections
class drawableItems(object):
  """This class exists to enumerate the drawableItems"""
  # If you make a new drawing class, add it here
  def __init__(self):
    super(drawableItems,self).__init__()
    # items are stored as pointers to the classes (not instances)
    self._drawableClasses = collections.OrderedDict()
    self._drawableClasses.update({'hit':hit})
    self._drawableClasses.update({'cluster':cluster})

  def getListOfItems(self):
    return self._drawableClasses.keys()

  def getDict(self):
    return self._drawableClasses