#!/usr/bin/python

import sys
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
from dataInterface import *


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

    def drawRect(self, wire=20, timeStart=20, timeStop=25,brush=(0,0,0)):
        # Draws a rectangle at (x,y,xlength, ylength)
        r1 = pg.QtGui.QGraphicsRectItem(wire, timeStart, 1, timeStop-timeStart)
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
        for hit in self._listOfHits:
            self._view.removeItem(hit)
        self._listOfHits = []        

    def connectWireDrawFunction(self, func):
        self._wdf = func

class dataHandler(QtGui.QWidget):
    """docstring for dataHandler
        This class connects the different types of data to
        the different drawers, and is in charge of updating the options
        to draw
    """
    def __init__(self):
        super(dataHandler, self).__init__()



class evd(QtGui.QWidget):


    def __init__(self):
        super(evd, self).__init__()
        # self._filePath = "/media/cadams/data_linux/argoneut_mc/nue_larlite_all.root"
        self._filePath = ""
        self._baseData = baseDataInterface()
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

        self._fileSelectButton = QtGui.QPushButton("Select File")
        self._fileSelectButton.clicked.connect(self.selectFile)

        # Button to adjust the range to the max:
        self._rangeButton = QtGui.QPushButton("Max Range")
        self._rangeButton.clicked.connect(self.setRangeToMax)

        # ColorMap used to color data:
        self._cmap = pg.GradientWidget(orientation='top')
        # self._cmap.resize(1,1)
        self._colorMapCollection = {'ticks': [(0, (30, 30, 255, 255)), (0.33333, (0, 255, 255, 255)), (0.66666, (255,255,100,255)), (1, (255, 0, 0, 255))], 'mode': 'rgb'}
        self._blankMapCollection = {'ticks': [(0, (255, 255, 255, 255)), (1, (255, 255, 255, 255))], 'mode': 'rgb'}
        self._cmap.restoreState(self._colorMapCollection)
        self._cmap.sigGradientChanged.connect(self.refreshGradient)
        # print self._cmap.size()

        # Area to hold buttons
        self._controlBox = QtGui.QVBoxLayout()
        




        self._controlBox.addWidget(self._nextButton)
        self._controlBox.addWidget(self._prevButton)
        self._controlBox.addWidget(self._fileSelectButton)
        # self._controlBox.addWidget(self._colorButton)
        # self._controlBox.addWidget(self._cmap)
        self._controlBox.addWidget(self._rangeButton)
        

        self._drawRawOption = QtGui.QCheckBox("Draw Raw")
        self._drawRawOption.setCheckState(True)
        self._drawRawOption.setTristate(False)
        self._drawRawOption.stateChanged.connect(self.rawChoiceChanged)

        # Add labels for the hits and clusters:
        # Set up the labels that hold the data:
        self.initDataChoices()
        for key in self._dataListsAndLabels:
            self._controlBox.addWidget(self._dataListsAndLabels[key])


        self._controlBox.addWidget(self._drawRawOption)

        self._controlBox.addStretch(1)
        self._controlBox.addWidget(self._quitButton)

        # Add a status bar for information purposes:
        self.statusBar = QtGui.QStatusBar()


        # Area to hold data:
        self._dataBox = QtGui.QGridLayout()
        self._drawerList = []
        nviews = self._baseData._nviews
        for i in range(0, nviews):
            # These boxes hold the wire/time views:
            self._drawerList.append(evd_drawer())
            # print 
            # add it to the layout:
            self._dataBox.addWidget(self._drawerList[-1], 2*i,1,1,1)
            self._drawerList[-1].connectStatusBar(self.statusBar)
            self._drawerList[-1]._plane = i

        # Make an extra space for wires:
        self._drawerList.append(pg.GraphicsLayoutWidget())
        self._dataBox.addWidget(self._drawerList[-1],2*nviews+1,1,2,1)
        
        self._wirePlot = self._drawerList[-1].addPlot()
        self._wirePlotItem = pg.PlotDataItem()
        self._wirePlot.addItem(self._wirePlotItem)

        # Connect the wire drawing box to the planes so that they may
        # update it
        for i in range(0, nviews):
            self._drawerList[i].connectWireDrawFunction(self.drawWire)

        # Put the layout together
        grid = QtGui.QGridLayout()
        grid.addLayout(self._controlBox,1,0,2*nviews+1,1)
        grid.addLayout(self._dataBox,1,1)
        grid.addWidget(self.statusBar)
        self.setLayout(grid)    

        
        self.setGeometry(800, 300, 800, 800)
        self.setWindowTitle('Buttons')    
        self.show()


        # If there was a file passed on commandline, try to use it:
        # print len(sys.argv)
        if (len(sys.argv) > 1):
            self._filePath = sys.argv[-1]
            self.initData()
            self.updateDataChoices()
            
        self.setRangeToMax()

        self.updateImage()

    def initDataChoices(self):
        # Create a tuple of options and their labels
        # Add the raw, clusters, and hits:
        self._dataListsAndLabels = {'Hits': QtGui.QComboBox(), 'HitsLabel': QtGui.QLabel("Hits:") }
        self._dataListsAndLabels.update({'Clusters': QtGui.QComboBox(), 'ClustersLabel': QtGui.QLabel("Clusters:") })

        self._dataListsAndLabels['Hits'].addItem("--None--")
        self._dataListsAndLabels['Clusters'].addItem("--None--")
        # self._dataListsAndLabels['Hits'].addItem("item 3")
        self._dataListsAndLabels['Hits'].activated[str].connect(self.hitsChoiceChanged)
        self._dataListsAndLabels['Clusters'].activated[str].connect(self.clusterChoiceChanged)

    def updateDataChoices(self):
        # Call this method to refresh the list of available data products to draw
        for key in self._baseData._fileInterface.getListOfKeys():
            # self._dataListsAndLabels['Hits'].addItem(key)
            if key == 'hit':
                self._dataListsAndLabels['Hits'].clear()
                self._dataListsAndLabels['Hits'].addItem("--Select--")
                for item in self._baseData._fileInterface.getListOfKeys()['hit']:
                    self._dataListsAndLabels['Hits'].addItem(item)

            if key == 'cluster':
                self._dataListsAndLabels['Clusters'].clear()
                self._dataListsAndLabels['Clusters'].addItem("--Select--")
                for item in self._baseData._fileInterface.getListOfKeys()['cluster']:
                    self._dataListsAndLabels['Clusters'].addItem(item)

    def hitsChoiceChanged(self, text):
        # This is the only method monitoring the status of hit drawing
        # So it is responsible for cleaning up the hits if the 
        # choice changes
        # if text == '--None--' or text == '--Select--':
        for view in range(0,self._baseData._nviews):
            self._drawerList[view].clearHits()

        # print "Hits choice changed to ", text
        if 'hit' in self._baseData._fileInterface.getListOfKeys():
            if text in self._baseData._fileInterface.getListOfKeys()['hit']:
                # print "Trying to add the hits process ..."
                self._baseData.add_drawing_process('hit',text)
            else:
                self._baseData.remove_drawing_process('hit')
        self.updateImage()

    def clusterChoiceChanged(self,text):
        # This is the only method monitoring the status of hit drawing
        # So it is responsible for cleaning up the hits if the 
        # choice changes
        # if text == '--None--' or text == '--Select--':
        for view in range(0,self._baseData._nviews):
            self._drawerList[view].clearClusters()
                
        # print "Hits choice changed to ", text
        if 'cluster' in self._baseData._fileInterface.getListOfKeys():
            if text in self._baseData._fileInterface.getListOfKeys()['cluster']:
                print "Trying to add the clusters process ..."
                self._baseData.add_drawing_process('cluster',text)
            else:
                self._baseData.remove_drawing_process('cluster')
        self.updateImage()

    def rawChoiceChanged(self):
        if self._drawRawOption.isChecked():
            self.drawRaw()
        else:
            self.drawBlank()       

    def initData(self):
        self._baseData.set_input_file(self._filePath)
        # check for raw data, make a handle for it if available:
        if 'wire' in self._baseData._fileInterface.getListOfKeys():
            # print "Adding wire data"
            # print self._baseData._fileInterface.getListOfKeys()
            # print self._baseData._fileInterface.getListOfKeys()['wire'][0]
            self._baseData.add_drawing_process('wire',self._baseData._fileInterface.getListOfKeys()['wire'][0])
            return
        
        # TODO
        # Here's how I imagine the workflow:
        # 1) Initialize the GUI, no file required
        # 2) Upon loading a file, find out what is available to draw
        # 3) Draw the raw data, if available
        #   a) If no raw, draw hits.  If not hits, draw clusters. etc.
        # 4) As the user selects more things to draw, add the drawing 
        #    to the interface and draw those things!


    # What follows are functions to manage the next, prev events etc.

    def drawRaw(self):
      d = self._baseData._daughterProcesses['wire'].get_img()
      self._cmap.restoreState(self._colorMapCollection)
      for i in range (0, self._baseData._nviews):
          self._drawerList[i]._item.setImage(d[i], scale=self._baseData._aspectRatio)
          self._drawerList[i]._item.setLookupTable(self._cmap.getLookupTable(255))
      self.drawWire(1,1)

    def drawBlank(self):
      # d = self._baseData._blankData  
      self._cmap.restoreState(self._blankMapCollection)
      for i in range (0, self._baseData._nviews):
          # self._drawerList[i]._item.setImage(image=None, scale=self._baseData._aspectRatio)
          self._drawerList[i]._item.setLookupTable(self._cmap.getLookupTable(255))


    def drawWire(self, plane,wire):
      # just testing, draw one wire (plane 0, wire 200)
      if self._drawRawOption.isChecked():
          wire =self._baseData._daughterProcesses['wire'].get_wire(plane,wire)
          self._wirePlotItem.setData(wire)

    def drawHits(self):
        # print self._baseData._daughterProcesses.keys()
        for view in range(0,self._baseData._nviews):
            hits = self._baseData._daughterProcesses['hit'].get_hits(view)
            for hitIndex in range(0, len(hits[0])):
                self._drawerList[view].drawRect(hits[0][hitIndex], hits[1][hitIndex],hits[2][hitIndex])

    def drawClusters(self):
        procs = self._baseData._daughterProcesses
        colors = self._baseData._daughterProcesses['cluster']._clusterColors
        # print procs.keys()
        for view in range(0,self._baseData._nviews):
            colorIndex = 0
            for cluster in range(0, procs['cluster'].get_n_clusters(view)):
                h = procs['cluster'].get_hits(view,cluster)
                for hitIndex in range(0, len(h[0])):
                    self._drawerList[view].drawRect(h[0][hitIndex], h[1][hitIndex],h[2][hitIndex],colors[colorIndex])
                colorIndex += 1
                if colorIndex >= len(colors):
                    colorIndex = 0

    def updateImage(self):
        drawn = False
        if not self._baseData._hasFile:
            self.drawBlank()
            return
        else:
            self._baseData.processEvent()
        if self._drawRawOption.isChecked():
            self.drawRaw()
            drawn = True
            pass
        if self._dataListsAndLabels['Hits'].currentText() != '--Select--':
          if self._dataListsAndLabels['Hits'].currentText() != '--None--':
            self.drawHits()
            drawn = True
            pass
        if self._dataListsAndLabels['Clusters'].currentText() != '--Select--':
          if self._dataListsAndLabels['Clusters'].currentText() != '--None--':
            self.drawClusters()
            drawn = True

        if not drawn:
          self.drawBlank()

    def clearDrawnProducts(self):
        for view in range(0,self._baseData._nviews):
            self._drawerList[view].clearHits()

    def nextEvent(self):
      self._baseData._event += 1
      self.clearDrawnProducts()
      self.updateImage()

    def prevEvent(self):
      if self._baseData._event != 1:
          self._baseData._event -= 1
      self.clearDrawnProducts()
      self.updateImage()

    def refreshGradient(self):
      # print ("Gradient Changed")
      for i in range (0, self._baseData._nviews):
          self._drawerList[i]._item.setLookupTable(self._cmap.getLookupTable(255))

    # def clickImage(self):
        # print

    def setRangeToMax(self):
      for i in range (0, self._baseData._nviews):
        self._drawerList[i]._view.setRange(xRange=(0,240),yRange=(0,1600), padding=0)
        # self._views[i].setXRange(0,240)
        # self._views[i].setYRange(0,2400)

    def selectFile(self):
        self._filePath = str(QtGui.QFileDialog.getOpenFileName())
        self.initData()
        self.updateDataChoices()
        self.updateImage()

def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = evd()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()