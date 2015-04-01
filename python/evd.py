#!/usr/bin/python

import sys
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import rawdata as rd


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

    def mouseMoved(self, pos):
        self.q = self._item.mapFromScene(pos)
        # print q.x()
        message= QtCore.QString()
        message.append("Wire: ")
        message.append(str(int(self.q.x())))
        message.append(", Time: ")
        message.append(str(int(self.q.y())))
        # print message
        if self.q.x() > 0 and self.q.x() < 240:
            if self.q.y() > 0 and self.q.y() < 2000:
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

    def drawRect(self):
        # Draws a rectangle at (x,y,xlength, ylength)
        r1 = pg.QtGui.QGraphicsRectItem(10, 20, 1, 5)
        r1.setPen(pg.mkPen(None))
        r1.setBrush(pg.mkBrush('r'))
        self._view.addItem(r1)

    def connectWireDrawFunction(self, func):
        self._wdf = func

class evd(QtGui.QWidget):


    def __init__(self):
        super(evd, self).__init__()
        self.initData()
        self.initUI()

    def initUI(self):
        # Buttons for using the event display:
        self._nextButton = QtGui.QPushButton("Next")
        self._prevButton = QtGui.QPushButton("Previous")
        self._quitButton = QtGui.QPushButton("Quit")
        # Bind quit to the proper functionality
        self._quitButton.clicked.connect(QtCore.QCoreApplication.instance().quit)
        self._nextButton.clicked.connect(self.nextEvent)
        self._prevButton.clicked.connect(self.prevEvent)

        self._nextButton.setToolTip("Move to the next event.")
        self._prevButton.setToolTip("Move to the previous event.")
        self._quitButton.setToolTip("Close the viewer.")

        # Button to adjust the range to the max:
        self._rangeButton = QtGui.QPushButton("Max Range")
        self._rangeButton.clicked.connect(self.setRangeToMax)

        # ColorMap used to color data:
        self._cmap = pg.GradientWidget(orientation='left')
        colorMapDefault = {'ticks': [(0, (30, 30, 255, 255)), (0.33333, (0, 255, 255, 255)), (0.66666, (255,255,100,255)), (1, (255, 0, 0, 255))], 'mode': 'rgb'}
        self._cmap.restoreState(colorMapDefault)
        self._cmap.sigGradientChanged.connect(self.refreshGradient)


        # self._cmap.setFields({(mode: {0,1,2,4})})
        # Area to hold buttons
        self._controlBox = QtGui.QVBoxLayout()
        self._controlBox.addWidget(self._nextButton)
        self._controlBox.addWidget(self._prevButton)
        # self._controlBox.addWidget(self._colorButton)
        self._controlBox.addWidget(self._cmap)
        self._controlBox.addWidget(self._rangeButton)
        self._controlBox.addStretch(1)
        self._controlBox.addWidget(self._quitButton)

        # Add a status bar for information purposes:
        self.statusBar = QtGui.QStatusBar()


        # Area to hold data:
        self._dataBox = QtGui.QGridLayout()
        self._drawerList = []
        nplanes = self.r.nplanes
        for i in range(0, nplanes):
            # These boxes hold the wire/time views:
            self._drawerList.append(evd_drawer())
            # print 
            # add it to the layout:
            self._dataBox.addWidget(self._drawerList[-1], 2*i,1,1,1)
            self._drawerList[-1].connectStatusBar(self.statusBar)
            self._drawerList[-1]._plane = i

        # Make an extra space for wires:
        self._drawerList.append(pg.GraphicsLayoutWidget())
        self._dataBox.addWidget(self._drawerList[-1],2*nplanes+1,1,2,1)
        
        self._wirePlot = self._drawerList[-1].addPlot()
        self._wirePlotItem = pg.PlotDataItem()
        self._wirePlot.addItem(self._wirePlotItem)

        # Connect the wire drawing box to the planes so that they may
        # update it
        for i in range(0, nplanes):
            self._drawerList[i].connectWireDrawFunction(self.drawWire)

        # Put the layout together
        grid = QtGui.QGridLayout()
        grid.addLayout(self._controlBox,1,0,2*nplanes+1,1)
        grid.addLayout(self._dataBox,1,1)
        grid.addWidget(self.statusBar)
        self.setLayout(grid)    

        
        self.setGeometry(800, 300, 800, 800)
        self.setWindowTitle('Buttons')    
        self.show()

        self.setRangeToMax()

        self.initData()
        self.draw()


    def initData(self):
        self.r = rd.RawData()
        self.r.init_proc()
        self.r.add_input_file("/media/cadams/data_linux/argoneut_mc/nue_larlite_all.root")
        self.r.init_geom()
        self.r.config_argo()
        # d = r.get_img()

    # What follows are functions to manage the next, prev events etc.

    def draw(self):
      d = self.r.get_img()
      for i in range (0, self.r.nplanes):
          self._drawerList[i]._item.setImage(d[i], scale=self.r.aspectRatio)
          self._drawerList[i]._item.setLookupTable(self._cmap.getLookupTable(255))

      self.drawWire(1,201)

    def drawWire(self, plane,wire):
      # just testing, draw one wire (plane 0, wire 200)
      wire = self.r.get_wire(plane,wire)
      self._wirePlotItem.setData(wire)

    def nextEvent(self):
      self.r.event += 1
      self.draw()

    def prevEvent(self):
      if self.r.event != 1:
          self.r.event -= 1
      self.draw()

    def refreshGradient(self):
      # print ("Gradient Changed")
      for i in range (0, self.r.nplanes):
          self._drawerList[i]._item.setLookupTable(self._cmap.getLookupTable(255))

    # def clickImage(self):
        # print

    def setRangeToMax(self):
      for i in range (0, self.r.nplanes):
        self._drawerList[i]._view.setRange(xRange=(0,240),yRange=(0,1600), padding=0)
        # self._views[i].setXRange(0,240)
        # self._views[i].setYRange(0,2400)



def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = evd()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()