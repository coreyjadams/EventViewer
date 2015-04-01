#!/usr/bin/python

import sys
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import rawdata as rd

# class window(QtGui.QMainWindow):
#     def __init__(self):
#         super(window,self).__init__()
#         self.evd = evd()
#         self.statusBa

# class evd_drawer(pg.GraphicsLayoutWidget):
#     def __init__(self):
#         super(evd_drawer, self).__init__()

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

        # Button to adjust the range to the max:
        self._rangeButton = QtGui.QPushButton("Max Range")
        self._rangeButton.clicked.connect(self.setRangeToMax)

        # ColorMap used to color data:
        self._cmap = pg.GradientWidget(orientation='left')
        self._cmap.loadPreset('spectrum')
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


        # Area to hold data:
        self._dataBox = QtGui.QGridLayout()
        self._emptySpaceList = []
        self._views = []
        self._items = []
        nplanes = self.r.nplanes
        for i in range(0, nplanes):
            # These boxes hold the wire/time views:
            self._emptySpaceList.append(pg.GraphicsLayoutWidget())
            # add it to the layout:
            self._dataBox.addWidget(self._emptySpaceList[-1], i,1,1,2)
            # add a view box, which is a widget that allows an image to be shown
            self._views.append(self._emptySpaceList[-1].addViewBox())
            # add an image item which handles drawing (and refreshing) the image
            self._items.append(pg.ImageItem())
            # connect the scene to click events, used to get wires
            self._emptySpaceList[-1].scene().sigMouseClicked.connect(self.mouseClicked)
            # connect the views to mouse move events, used to update the info box at the bottom
            self._emptySpaceList[-1].scene().sigMouseMoved.connect(self.mouseMoved)
            self._views[-1].addItem(self._items[-1])
            # self._items[-1].clicked.connect(self.mousePressEvent)

        # Make an extra space for wires:
        # self._emptySpaceList.append(pg.GraphicsLayoutWidget())
        # self._dataBox.addWidget(self._emptySpaceList[-1],i+1,1,1,2)



        # Put the layout together
        grid = QtGui.QGridLayout()
        grid.addLayout(self._controlBox,1,0,2,1)
        grid.addLayout(self._dataBox,1,1)
        self.setLayout(grid)    

        # Add a status bar for information purposes:
        self.statusBar = QtGui.QStatusBar()
        grid.addWidget(self.statusBar)

        
        self.setGeometry(800, 300, 800, 800)
        self.setWindowTitle('Buttons')    
        self.show()

        self.initData()
        self.draw()

    def initData(self):
        self.r = rd.RawData()
        self.r.init_proc()
        self.r.add_input_file("/media/cadams/data_linux/argoneut_mc/electrons_0_all.root")
        self.r.init_geom()
        self.r.config_argo()
        # d = r.get_img()

    # What follows are functions to manage the next, prev events etc.

    def draw(self):
      d = self.r.get_img()
      for i in range (0, self.r.nplanes):
          self._items[i].setImage(d[i], scale=self.r.aspectRatio)
          self._items[i].setLookupTable(self._cmap.getLookupTable(255))
      
      # table = pg.makeARGB(d[0],self._cmap.colorMap())


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
          self._items[i].setLookupTable(self._cmap.getLookupTable(255))

    # def clickImage(self):
        # print

    def setRangeToMax(self):
      for i in range (0, self.r.nplanes):
        self._views[i].setRange(xRange=(0,240),yRange=(0,2000), padding=-0.1)
        # self._views[i].setXRange(0,240)
        # self._views[i].setYRange(0,2400)


    def mouseMoved(self, pos):
        self.q = self._items[0].mapFromScene(pos)
        # print q.x()
        message= QtCore.QString()
        message.append("Wire: ")
        message.append(str(int(self.q.x())))
        if self.q.x() > 0 and self.q.x() < 240:
            self.statusBar.showMessage(message)

    def mouseClicked(self, event):
        print self
        print event
        print event.pos()
        # Get the Mouse position and print it:
        # print "Image position:", self.q.x()
        # use this method to try drawing rectangles
        r1 = pg.QtGui.QGraphicsRectItem(10, 20, 11, 30)
        r1.setPen(pg.mkPen(None))
        r1.setBrush(pg.mkBrush('r'))
        self._views[0].addItem(r1)
        # pdi.plot()

def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = evd()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()