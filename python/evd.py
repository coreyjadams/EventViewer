#!/usr/bin/python

import sys
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
from dataInterface import *
from drawingInterface import *

# Making notes here of things that need to be addressed:
# The scale setting might disturb the aspect ratio
# Seems to be a small bug when zooming in, making wires offset.
# Add other 2d reco objects: vertex, mctrack/mcshower.  Print mctruth
# hit enter to go to the next event
#   --- even better: bind keys to buttons!
# automatically zoom to the region of interest

# Current list of features:
# Draws hits, clusters, wires
# Zoom in and out of the image with scrolling, click and drag to pan
# Click on an image to draw the wire the mouse clicked on, if wire data available
# use the max range button to set the view to the whole readout and wire set
# select file will let you choose a file to open
# With clusters drawn, hover the mouse over a cluster to highlight it
#   double click sets the highlight to stick, double click again to undo it
# Hot Keys:
#  n - next event
#  p - prev event
#  c - set focus to clusters
#  h - set focus to hits



class ComboBoxWithKeyConnect(QtGui.QComboBox):

    def __init__(self):
        super(ComboBoxWithKeyConnect,self).__init__()

    def connectOwnerKPE(self, kpe):
        self._owner_KPE = kpe

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_N:
            self._owner_KPE(e)
            pass
        if e.key() == QtCore.Qt.Key_P:
            self._owner_KPE(e)
            pass
        else:
            super(ComboBoxWithKeyConnect,self).keyPressEvent(e)

class evd(QtGui.QWidget):


    def __init__(self):
        super(evd, self).__init__()
        # self._filePath = "/media/cadams/data_linux/argoneut_mc/nue_larlite_all.root"
        self._filePath = ""
        self._baseData = baseDataInterface(argo=True)
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
        self._drawRawOption.setTristate(False)
        self._drawRawOption.stateChanged.connect(self.rawChoiceChanged)

        self._unitDisplayOption = QtGui.QCheckBox("Use cm")
        self._unitDisplayOption.setTristate(False)
        self._unitDisplayOption.stateChanged.connect(self.unitChoicedChanged)

        # Add labels for the hits and clusters:
        # Set up the labels that hold the data:
        self.initDataChoices()
        for key in self._dataListsAndLabels:
            self._controlBox.addWidget(self._dataListsAndLabels[key])


        self._controlBox.addWidget(self._drawRawOption)

        self._controlBox.addStretch(1)
        self._controlBox.addWidget(self._unitDisplayOption)
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
            self._drawerList[-1]._wRange = self._baseData._wRange
            self._drawerList[-1]._tRange = self._baseData._tRange
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
        self._dataListsAndLabels = {
                'Hits': ComboBoxWithKeyConnect(), 
                'HitsLabel': QtGui.QLabel("Hits:") }
        self._dataListsAndLabels['Hits'].connectOwnerKPE(self.keyPressEvent)

        self._dataListsAndLabels.update({
                'Clusters': ComboBoxWithKeyConnect(), 
                'ClustersLabel': QtGui.QLabel("Clusters:") })
        self._dataListsAndLabels['Clusters'].connectOwnerKPE(self.keyPressEvent)


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
                # print "Trying to add the clusters process ..."
                self._baseData.add_drawing_process('cluster',text)
            else:
                self._baseData.remove_drawing_process('cluster')
        self.updateImage()

    def rawChoiceChanged(self):
        if self._drawRawOption.isChecked():
            self.drawRaw()
        else:
            self.drawBlank()       

    def unitChoicedChanged(self):
        if self._unitDisplayOption.isChecked():
            for i in range (0, self._baseData._nviews):
                self._drawerList[i]._cmSpace = True;
                self._drawerList[i]._wire2cm = self._baseData._wire2Cm
                self._drawerList[i]._time2cm = self._baseData._time2Cm
        else:
            for i in range (0, self._baseData._nviews):
                self._drawerList[i]._cmSpace = False;           

    def initData(self):
        self._baseData.set_input_file(self._filePath)
        # print self._baseData._fileInterface.getListOfKeys()
        # check for raw data, make a handle for it if available:
        if 'wire' in self._baseData._fileInterface.getListOfKeys():
            # print "Adding wire data"
            # print self._baseData._fileInterface.getListOfKeys()
            # print self._baseData._fileInterface.getListOfKeys()['wire'][0]
            self._baseData.add_drawing_process('wire',self._baseData._fileInterface.getListOfKeys()['wire'][0])
            self._drawRawOption.setCheckState(True)
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
      if not 'wire' in self._baseData._daughterProcesses:
          print "No wire data available to draw!"
          return
      d = self._baseData._daughterProcesses['wire'].get_img()
      self._cmap.restoreState(self._colorMapCollection)
      for i in range (0, self._baseData._nviews):
          self._drawerList[i]._item.setImage(d[i], scale=self._baseData._aspectRatio)
          self._drawerList[i]._item.setLookupTable(self._cmap.getLookupTable(255))
      self.drawWire(1,1)

    def drawBlank(self):
      d = self._baseData._blankData  
      self._cmap.restoreState(self._blankMapCollection)
      for i in range (0, self._baseData._nviews):
          self._drawerList[i]._item.setImage(image=d, scale=self._baseData._aspectRatio)
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
            self._drawerList[view].drawHits(hits)

            # print hits[0]
            # for hitIndex in range(0, len(hits[0])):
                # self._drawerList[view].drawRect(hits[0][hitIndex], hits[1][hitIndex],hits[2][hitIndex])

    def drawClusters(self):
        procs = self._baseData._daughterProcesses
        # print procs.keys()
        for view in range(0,self._baseData._nviews):
            clusters = procs['cluster'].get_clusters(view)
            self._drawerList[view].drawClusters(clusters)


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
      xR = (0,self._baseData._wRange)
      yR = (0,self._baseData._tRange)
      for i in range (0, self._baseData._nviews):
        self._drawerList[i]._view.setRange(xRange=xR,yRange=yR, padding=0)


    def selectFile(self):
        self._filePath = str(QtGui.QFileDialog.getOpenFileName())
        self.initData()
        self.updateDataChoices()
        self.updateImage()

    def keyPressEvent(self,e):
        # print "A key was pressed!"
        # print e.key()
        if e.key() == QtCore.Qt.Key_N:
            self.nextEvent()
        if e.key() == QtCore.Qt.Key_P:
            self.prevEvent()

        if e.key() == QtCore.Qt.Key_C:
            self._dataListsAndLabels['Clusters'].setFocus()
        if e.key() == QtCore.Qt.Key_H:
            self._dataListsAndLabels['Hits'].setFocus()

        if e.key() == QtCore.Qt.Key_R:
            self.setRangeToMax()

    def keyPressInterrupt(self,e):
        print "Interrupting function!"


def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = evd()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()