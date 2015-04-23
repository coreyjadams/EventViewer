
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg


# Defining the cluster colors as a global variable:
_clusterColors = [ 
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


class hitDrawer(QtGui.QGraphicsRectItem):
    """docstring for hitDrawer"""
    def __init__(self, *args, **kwargs):
        super(hitDrawer, self).__init__(*args)
        self.setAcceptHoverEvents(True)
        self._isHighlighted = kwargs['highlight']
        # self.arg = arg
        

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

class clusterDrawer(object):

    def __init__(self, **kwargs):
        super(clusterDrawer,self).__init__()
        self._listOfHits = []
        self._inputHits = kwargs['hits']
        self._view = kwargs['view']
        self._color = kwargs['color']
        self._isHighlighted = False


    def drawRect(self, wire=20, timeStart=20, timeStop=25,outline=False):
        # Draws a rectangle at (x,y,xlength, ylength)
        r1 = hitDrawer(wire, timeStart, 1, timeStop-timeStart,highlight=outline)

        if outline:
            r1.setPen(pg.mkPen((0,0,0),width=2))
        else:
            r1.setPen(pg.mkPen(None))
    
        r1.setBrush(pg.mkColor(self._color))
        self._listOfHits.append(r1)
        self._view.addItem(r1)
        return r1

    def drawHits(self,outline=False):
        for i in range(0,len(self._inputHits[0])):
            r = self.drawRect(
                self._inputHits[0][i],
                self._inputHits[1][i],
                self._inputHits[2][i],
                outline
                )

            r.connectOwnerHoverEnter(self.hoverEnter)
            r.connectOwnerHoverExit(self.hoverExit)
            r.connectToggleHighlight(self.toggleHighlight)

    def clearHits(self):
        for hit in self._listOfHits:
            self._view.removeItem(hit)
        self._listOfHits = []
        self._inputHits = []

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

class evd_drawer(pg.GraphicsLayoutWidget):
    def __init__(self):
        super(evd_drawer, self).__init__()
        # add a view box, which is a widget that allows an image to be shown
        self._view = self.addViewBox()
        # add an image item which handles drawing (and refreshing) the image
        self._item = pg.ImageItem()
        self._view.addItem(self._item)
        # connect the scene to click events, used to get wires
        self.scene().sigMouseClicked.connect(self.mouseClicked)
        # connect the views to mouse move events, used to update the info box at the bottom
        self.scene().sigMouseMoved.connect(self.mouseMoved)
        self._plane = -1
        self._listOfHits = []
        self._listOfClusters = []
        self._cmSpace = False
        self._wire2cm = 0.4
        self._time2cm = 0.2
        self._wRange  = []
        self._tRange  = 2000 

    def mouseMoved(self, pos):
        self.q = self._item.mapFromScene(pos)
        # print q.x()
        message= QtCore.QString()
        if self._cmSpace:
            message.append("X: ")
            message.append("{0:.1f}".format(self.q.x()*self._wire2cm))
        else:
            message.append("W: ")
            message.append(str(int(self.q.x())))
        if self._cmSpace:
            message.append(", Y: ")
            message.append("{0:.1f}".format(self.q.y()*self._time2cm))
        else:
            message.append(", T: ")
            message.append(str(int(self.q.y())))
        # print message
        if self.q.x() > 0 and self.q.x() < self._wRange:
            if self.q.y() > 0 and self.q.y() < self._tRange:
                self.statusBar.showMessage(message)

    def mouseClicked(self, event):
        # print self
        # print event
        # print event.pos()
        # Get the Mouse position and print it:
        # print "Image position:", self.q.x()
        # use this method to try drawing rectangles
        # self.drawRect()
        # pdi.plot()
        # For this function, a click should get the wire that is
        # being hovered over and draw it at the bottom
        wire = int( self._item.mapFromScene(event.pos()).x())
        # print "Plane: " + str(self._plane) + ", Wire: " + str(wire)
        self._wdf(self._plane,wire)
        # return self.plane,self.wire

    def connectStatusBar(self, statusBar):
        self.statusBar = statusBar

    def drawRect(self, wire=20, timeStart=20, timeStop=25,brush=(0,0,0)):
        # Draws a rectangle at (x,y,xlength, ylength)
        r1 = QtGui.QGraphicsRectItem(wire, timeStart, 1, timeStop-timeStart)

        # # New Way
        # r1.setPen(pg.mkPen(brush,width=2))
        # # r1.setBrush(pg.mkColor((255,255,255)))

        # Old Way:
        r1.setPen(pg.mkPen(None))
        r1.setBrush(pg.mkColor(brush))
        self._listOfHits.append(r1)
        self._view.addItem(r1)
        return r1

    def clearHits(self):
        for hit in self._listOfHits:
            self._view.removeItem(hit)
        self._listOfHits = []

    def clearClusters(self):
        for clust in self._listOfClusters:
            clust.clearHits()
        self._listOfClusters = []        

    def connectWireDrawFunction(self, func):
        self._wdf = func

    def drawHits(self,hits):
        for hitIndex in range(0, len(hits[0])):
            self.drawRect(
                hits[0][hitIndex], 
                hits[1][hitIndex],
                hits[2][hitIndex])

    def drawClusters(self,clusters):
        colorIndex = 0
        for cluster in clusters:
            self._listOfClusters.append(clusterDrawer(
                view = self._view,
                color = _clusterColors[colorIndex],
                hits = cluster))
            self._listOfClusters[-1].drawHits()
            # print cluster
            # for hitIndex in range(0, len(h[0])):
                # self._drawerList[view].drawRect(h[0][hitIndex], h[1][hitIndex],h[2][hitIndex],colors[colorIndex])
            colorIndex += 1
            if colorIndex >= len(_clusterColors):
                colorIndex = 0