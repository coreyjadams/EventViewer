#!/usr/bin/env python

import sys
import argparse
import collections
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

# command line options or button to toggle argo or microboone geom


# Just implemented:
# automatically zoom to the region of interest
#  -> Want to add option to set range to max, auto range
#  -> Also want to be able to lock x,y axes to the correct aspect ratio.
#       -> can use view.setAspectLocked(True, ratio=aspectRatio)
# Want to be able to toggle on or off the wire display
# Fixed bug in wire range so that Nwires is a function of plane, now.


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
# Show run, event number and ability to jump to events



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

import threading
class fileWatcher(threading.Thread):
    """docstring for fileWatcher"""
    def __init__(self, event,file):
        super(fileWatcher, self).__init__()
        self.stopped = event
        # keep track of the last file displayed, only send a signal when it changes
        self._prevFile=None
        self._fileToWatch = file

    def run(self):
        while not self.stopped.wait(1.5):
            # print "Thread called"
            # open the file:
            try:
                f = open(self._fileToWatch)
            except Exception, e:
                print "The file selected for watching does not exist!"
                raise e
            # At this point, the file exists.
            fileToDraw = f.readline()
            # print "Contents of file are: ", fileToDraw
            if fileToDraw == self._prevFile:
                # print "Not drawing because file has not changed."
                continue
            if fileToDraw.endswith(".root"):
                # print "Attempting to refresh picture"
                self._func(fileToDraw)
                self._prevFile = fileToDraw
            else:
                print "File has changed but does not appear to be a root file."


    # This sets the function that gets called each iteration        
    def connect(self, func):
        self._func = func

class evd(QtGui.QWidget):


    def __init__(self, geometry,mode,fileName=None):
        super(evd, self).__init__()
        # self._filePath = "/media/cadams/data_linux/argoneut_mc/nue_larlite_all.root"
        self._filePath = None
        # initUI should not do ANY data handling, it should only get the interface loaded
        self._mode = mode
        self._geometry = geometry
        self._baseData = baseDataInterface(geometry,mode)
        self.initUI()

        self._watcher = None
        self._stopFlag = None
        self.updateFile(fileName)


    def closeEvent(self,event):
        if self._running:
            self.stopRun()

    def parseFileName(self,fileName):
        if self._running:
            self.stopRuns()
        if type(fileName) != str:
            self._filePath = None
            return

        if fileName.endswith(".root"):
            # this is a data file, set it to display:
            self._filePath = fileName
            self.setRangeToMax()
            self.initData()
            self.updateDataChoices()
            self.goToEvent(0)

        elif fileName.endswith(".txt"):
            # parse the txt file to get the file name
            # automatically start a run of autoupdates
            self._monitorFile = fileName
            self.startRun(fileName)
        else:
            self._filePath = None

    def startRun(self,fileName=None):
        # this function can be triggered by a button push, which implies it was stopped before;
        # In that case, refresh the thread and start over.
        # It can also be called by the parsefileName function, which implies a file is ready
        if self._watcher == None and fileName == None:
            print "ERROR: there is no file to watch, can not start a run."
            return
        self._stopFlag = threading.Event()
        self._watcher = fileWatcher(self._stopFlag, self._monitorFile)
        self._watcher.connect(self.autoUpdateFile)        
        self._runControlButton.setText("Stop Run")
        self._running = True
        self._watcher.start()
        pass

    def stopRun(self):
        self._runControlButton.setText("Start Run")
        self._running = False
        self._stopFlag.set()
        pass

    def runControl(self):
        if not self._running:
            self.startRun()
            return
        else:
            self.stopRun()

    def updateFile(self, file):
        if self._running:
            self.stopRun()
        self.parseFileName(file)
        self._filePath = file

    # this function is ONLY meant to be called by a thread for auto updating.
    # Do not call this yourself, use updateFile instead
    def autoUpdateFile(self,file):
        # Checking that the file is a .root file is left to the thread
        # print "Called function to update image ", file
        self._filePath = file
        self.initData()
        self.updateDataChoices()
        self.goToEvent(0)
        for view in range(0,self._baseData._nviews):
            self._drawerList[view].setVisible(False)
            self._drawerList[view].setVisible(True)


    def quit(self):
        if self._running:
            self.stopRun()
        QtCore.QCoreApplication.instance().quit()

    def initUI(self):


        # Buttons for using the event display:
        self._nextButton = QtGui.QPushButton("Next")
        self._prevButton = QtGui.QPushButton("Previous")
        self._quitButton = QtGui.QPushButton("Quit")
        # Bind quit to the proper functionality
        self._quitButton.clicked.connect(self.quit)
        self._nextButton.clicked.connect(self.nextEvent)
        self._prevButton.clicked.connect(self.prevEvent)

        self._nextButton.setToolTip("Move to the next event.")
        self._prevButton.setToolTip("Move to the previous event.")
        self._quitButton.setToolTip("Close the viewer.")

        self._fileSelectButton = QtGui.QPushButton("Select File")
        self._fileSelectButton.clicked.connect(self.selectFile)

        self._screenCaptureButton = QtGui.QPushButton("Capture Screen")
        self._screenCaptureButton.clicked.connect(self.screenCapture)

        self._runControlButton = QtGui.QPushButton("Start Run")
        self._runControlButton.clicked.connect(self.runControl)
        self._runControlButton.setStyleSheet("background-color: red")
        self._running = False

        # Labels and text entry to display the event number

        self._eventEntry = QtGui.QLineEdit()
        self._eventEntry.returnPressed.connect(self.eventEntryChanged)
        self._runLabel = QtGui.QLabel("Run: -")
        self._eventLabel = QtGui.QLabel("Ev.: -")

        # Button to adjust the range to the max:
        self._maxRangeButton = QtGui.QPushButton("Max Range")
        self._maxRangeButton.clicked.connect(self.setRangeToMax)
        #Button to Auto Range:
        self._autoRangeButton = QtGui.QCheckBox("Auto Range")
        self._autoRangeButton.setTristate(False)
        self._autoRangeButton.stateChanged.connect(self.autoRange)
        self._lockAspectRatio = QtGui.QCheckBox("Lock A.R.")
        self._lockAspectRatio.stateChanged.connect(self.lockAspectRatio)
        self._drawWireOption = QtGui.QCheckBox("Wire Drawing")
        self._drawWireOption.stateChanged.connect(self.drawWireOption)

        # ColorMap used to color data:
        self._cmap = pg.GradientWidget(orientation='left')
        self._cmap.resize(1,1)
        if self._mode == "daq":
          self._colorMapCollection = {'ticks': [(0.0,  (30,  30, 255, 255)),
                                                (0.15, (30,  30, 255, 255)), 
                                                (0.6,  (0,  255, 255, 255)), 
                                                (0.8,  (0,  255, 0,   255)), 
                                                (1,    (255,  0, 0,   255))], 
                                                'mode': 'rgb'}
        else:
          self._colorMapCollection = {'ticks': [(0, (30, 30, 255, 255)),
                                                (0.33333, (0, 255, 255, 255)), 
                                                (0.66666, (255,255,100,255)), 
                                                (1, (255, 0, 0, 255))], 
                                                'mode': 'rgb'}
        self._blankMapCollection = {'ticks': [(0, (255, 255, 255, 255)), (1, (255, 255, 255, 255))], 'mode': 'rgb'}
        self._cmap.restoreState(self._colorMapCollection)
        # print self._cmap.size()


        self._drawRawOption = QtGui.QCheckBox("Draw Raw")
        self._drawRawOption.setTristate(False)
        self._drawRawOption.stateChanged.connect(self.rawChoiceChanged)
        if self._mode == "daq":
            self._drawRawOption.setCheckState(True)

        self._unitDisplayOption = QtGui.QCheckBox("Use cm")
        self._unitDisplayOption.setTristate(False)
        self._unitDisplayOption.stateChanged.connect(self.unitChoicedChanged)

        # Area to hold buttons to control the events
        self._eventControlBox = QtGui.QVBoxLayout()
        self._eventControlBox.addWidget(self._eventEntry)
        self._runEventGrid = QtGui.QHBoxLayout()
        self._runEventGrid.addWidget(self._runLabel)
        self._runEventGrid.addWidget(self._eventLabel)
        self._eventControlBox.addLayout(self._runEventGrid)
        self._eventControlBox.addWidget(self._nextButton)
        self._eventControlBox.addWidget(self._prevButton)
        self._eventControlBox.addWidget(self._fileSelectButton)
        if self._mode == "daq":
            self._eventControlBox.addWidget(self._runControlButton)
        # self._eventControlBox.addWidget(self._colorButton)
        # if self._mode == "daq":
            # self._eventControlBox.addWidget(self._cmap)
            # self._cmap.sigGradientChanged.connect(self.refreshGradient)
        
        # Add labels for the hits and clusters:
        # Set up the labels that hold the data:
        if self._mode != "daq":
            self.initDataChoices()
            for key in self._dataListsAndLabels:
                self._eventControlBox.addWidget(self._dataListsAndLabels[key])
                print "Adding ", key

            self._eventControlBox.addWidget(self._drawRawOption)

        self._eventControlBox.addStretch(1)


        # Area to hold buttons to control the view
        self._eventControlBox.addWidget(self._maxRangeButton)
        if self._mode != "daq":
            self._eventControlBox.addWidget(self._autoRangeButton)
        self._eventControlBox.addWidget(self._lockAspectRatio)
        self._eventControlBox.addWidget(self._drawWireOption)
        self._eventControlBox.addStretch(1)

        self._eventControlBox.addWidget(self._unitDisplayOption)
        self._eventControlBox.addWidget(self._quitButton)
        # Add a status bar for information purposes:
        self.statusBar = QtGui.QStatusBar()


        # Area to hold data:
        self._dataBox = QtGui.QVBoxLayout()
        self._drawerList = []
        nviews = self._baseData._nviews
        for i in range(0, nviews):
            # These boxes hold the wire/time views:
            self._drawerList.append(evd_drawer())
            # print 
            # add it to the layout:
            self._dataBox.addWidget(self._drawerList[-1])
            # self._dataBox.addWidget(self._drawerList[-1], 2*i,1,1,1)
            self._drawerList[-1]._wRange = self._baseData._wRange
            self._drawerList[-1]._tRange = self._baseData._tRange
            self._drawerList[-1].connectStatusBar(self.statusBar)
            self._drawerList[-1]._plane = i
            self._drawerList[-1]._item.setLookupTable(self._cmap.getLookupTable(255))


        # Make an extra space for wires:
        self._drawerList.append(pg.GraphicsLayoutWidget())
        # self._dataBox.addWidget(self._drawerList[-1])
        # self._dataBox.addWidget(self._drawerList[-1],2*nviews+1,1,2,1)
        
        self._wirePlot = self._drawerList[-1].addPlot()
        self._wirePlotItem = pg.PlotDataItem()
        self._wirePlot.addItem(self._wirePlotItem)


        # Connect the wire drawing box to the planes so that they may
        # update it
        for i in range(0, nviews):
            self._drawerList[i].connectWireDrawFunction(self.drawWire)

        # Put the layout together
        grid = QtGui.QGridLayout()
        grid.addLayout(self._eventControlBox,0,0)
        # grid.addLayout(self._eventControlBox,2,0,nviews+1,1)
        grid.addLayout(self._dataBox,0,1,2,2)
        grid.addWidget(self.statusBar,2,0,1,2)
        grid.addWidget(self._screenCaptureButton,2,2,1,1)
        self.setLayout(grid)    

        
        self.setGeometry(800, 300, 800, 800)
        self.setWindowTitle('Event Display')    
        self.show()


    def initDataChoices(self):
        # Create a tuple of options and their labels
        # Add the raw, clusters, and hits:
        self._dataListsAndLabels = collections.OrderedDict()

        self._dataListsAndLabels.update({'HitsLabel': QtGui.QLabel("Hits:")})
        self._dataListsAndLabels.update({'Hits': ComboBoxWithKeyConnect()})
        self._dataListsAndLabels['Hits'].connectOwnerKPE(self.keyPressEvent)

        self._dataListsAndLabels.update({'ClustersLabel': QtGui.QLabel("Clusters:")})
        self._dataListsAndLabels.update({'Clusters': ComboBoxWithKeyConnect()})
        self._dataListsAndLabels['Clusters'].connectOwnerKPE(self.keyPressEvent)

        self._dataListsAndLabels.update({'VertexLabel': QtGui.QLabel("Vertex:")})
        self._dataListsAndLabels.update({'Vertex': ComboBoxWithKeyConnect()})
        self._dataListsAndLabels['Vertex'].connectOwnerKPE(self.keyPressEvent)

        self._dataListsAndLabels['Hits'].addItem("--None--")
        self._dataListsAndLabels['Clusters'].addItem("--None--")
        self._dataListsAndLabels['Vertex'].addItem("--None--")
        # self._dataListsAndLabels['Hits'].addItem("item 3")
        self._dataListsAndLabels['Hits'].activated[str].connect(self.hitsChoiceChanged)
        self._dataListsAndLabels['Clusters'].activated[str].connect(self.clusterChoiceChanged)
        self._dataListsAndLabels['Vertex'].activated[str].connect(self.vertexChoiceChanged)

    def updateDataChoices(self):
        if self._mode == "daq":
            return
        else:
            # Call this method to refresh the list of available data products to draw
            for key in self._baseData._dataHandle._fileInterface.getListOfKeys():
                # self._dataListsAndLabels['Hits'].addItem(key)
                if key == 'hit':
                    self._dataListsAndLabels['Hits'].clear()
                    self._dataListsAndLabels['Hits'].addItem("--Select--")
                    for item in self._baseData._dataHandle._fileInterface.getListOfKeys()['hit']:
                        self._dataListsAndLabels['Hits'].addItem(item)

                if key == 'cluster':
                    self._dataListsAndLabels['Clusters'].clear()
                    self._dataListsAndLabels['Clusters'].addItem("--Select--")
                    for item in self._baseData._dataHandle._fileInterface.getListOfKeys()['cluster']:
                        self._dataListsAndLabels['Clusters'].addItem(item)

                if key == 'vertex':
                    self._dataListsAndLabels['Vertex'].clear()
                    self._dataListsAndLabels['Vertex'].addItem("--Select--")
                    for item in self._baseData._dataHandle._fileInterface.getListOfKeys()['vertex']:
                        self._dataListsAndLabels['Vertex'].addItem(item)

    def hitsChoiceChanged(self, text):        # This is the only method monitoring the status of hit drawing
        # So it is responsible for cleaning up the hits if the 
        # choice changes
        # if text == '--None--' or text == '--Select--':
        for view in range(0,self._baseData._nviews):
            self._drawerList[view].clearHits()

        # print "Hits choice changed to ", text
        if 'hit' in self._baseData._dataHandle._fileInterface.getListOfKeys():
            if text in self._baseData._dataHandle._fileInterface.getListOfKeys()['hit']:
                # print "Trying to add the hits process ..."
                self._baseData._dataHandle.add_drawing_process('hit',text)
            else:
                self._baseData._dataHandle.remove_drawing_process('hit')
        self.updateImage()

    def clusterChoiceChanged(self,text):
        # This is the only method monitoring the status of cluster drawing
        # So it is responsible for cleaning up the clusters if the 
        # choice changes
        # if text == '--None--' or text == '--Select--':
        for view in range(0,self._baseData._nviews):
            self._drawerList[view].clearClusters()
                
        # print "Cluster choice changed to ", text
        if 'cluster' in self._baseData._dataHandle._fileInterface.getListOfKeys():
            if text in self._baseData._dataHandle._fileInterface.getListOfKeys()['cluster']:
                # print "Trying to add the clusters process ..."
                self._baseData._dataHandle.add_drawing_process('cluster',text)
            else:
                self._baseData._dataHandle.remove_drawing_process('cluster')
        self.updateImage()

    def vertexChoiceChanged(self,text):
        # This is the only method monitoring the status of vertex drawing
        # So it is responsible for cleaning up the clusters if the 
        # choice changes
        # if text == '--None--' or text == '--Select--':
        for view in range(0,self._baseData._nviews):
            self._drawerList[view].clearVertices()
                
        # print "vertex choice changed to ", text
        if 'vertex' in self._baseData._dataHandle._fileInterface.getListOfKeys():
            if text in self._baseData._dataHandle._fileInterface.getListOfKeys()['vertex']:
                # print "Trying to add the clusters process ..."
                self._baseData._dataHandle.add_drawing_process('vertex',text)
            else:
                self._baseData._dataHandle.remove_drawing_process('vertex')
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
        self._baseData._dataHandle.set_input_file(self._filePath)
        # print self._baseData._fileInterface.getListOfKeys()
        # check for raw data, make a handle for it if available:
        if self._mode == "daq":
            # self._baseData._dataHandle
            pass
        else:
            if 'wire' in self._baseData._dataHandle._fileInterface.getListOfKeys():
                # print "Adding wire data"
                # print self._baseData._fileInterface.getListOfKeys()
                # print self._baseData._fileInterface.getListOfKeys()['wire'][0]
                self._baseData._dataHandle.add_drawing_process('wire',
                  self._baseData._dataHandle._fileInterface.getListOfKeys()['wire'][0])
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



    def drawRaw(self):
      if self._mode != "daq":
          if not 'wire' in self._baseData._dataHandle._daughterProcesses:
              print "No wire data available to draw!"
              return
          d = self._baseData._dataHandle._daughterProcesses['wire'].get_img()
          self._cmap.restoreState(self._colorMapCollection)
          for i in range (0, self._baseData._nviews):
            # print len(d[i])
            self._drawerList[i]._item.setImage(d[i], scale=self._baseData._aspectRatio)
            self._drawerList[i]._item.setLookupTable(self._cmap.getLookupTable(255))
          self.drawWire(1,1)
      elif self._mode == "daq":
        if self._baseData._dataHandle._hasFile:
          d = self._baseData._dataHandle.get_img()
          self._cmap.restoreState(self._colorMapCollection)
          for i in range (0, self._baseData._nviews):

            self._drawerList[i]._item.setImage(d[i], 
                                                scale=self._baseData._aspectRatio,
                                                levels=self._baseData._levels[i])
            self._drawerList[i]._item.updateImage()
            self._drawerList[i]._item.setLookupTable(self._cmap.getLookupTable(255))
          self.drawWire(1,1)



    def drawBlank(self):
      d = self._baseData._blankData  
      self._cmap.restoreState(self._blankMapCollection)
      for i in range (0, self._baseData._nviews):
          self._drawerList[i]._item.setImage(image=None, scale=self._baseData._aspectRatio)
          self._drawerList[i]._item.setLookupTable(self._cmap.getLookupTable(255))


    def drawWire(self, plane,wire):
      # just testing, draw one wire (plane 0, wire 200)
      if self._mode == "daq":
        wire = self._baseData._dataHandle.get_wire(plane,wire)
        if wire != None:
          self._wirePlotItem.setData(wire)
      else:
        if self._drawRawOption.isChecked():
          wire =self._baseData._dataHandle._daughterProcesses['wire'].get_wire(plane,wire)
          if wire != None:
            self._wirePlotItem.setData(wire)

    def drawHits(self):
      # print self._baseData._daughterProcesses.keys()
      for view in range(0,self._baseData._nviews):
        hits = self._baseData._dataHandle._daughterProcesses['hit'].get_hits(view)
        self._drawerList[view].drawHits(hits)

        # print hits[0]
        # for hitIndex in range(0, len(hits[0])):
          # self._drawerList[view].drawRect(hits[0][hitIndex], hits[1][hitIndex],hits[2][hitIndex])

    def drawClusters(self):
        procs = self._baseData._dataHandle._daughterProcesses
        if 'cluster' not in procs:
            # This means clusters aren't being drawn, bail
            return
        # print procs.keys()
        for view in range(0,self._baseData._nviews):
            clusters = procs['cluster'].get_clusters(view)
            self._drawerList[view].drawClusters(clusters)

    def drawVertices(self):
        procs = self._baseData._dataHandle._daughterProcesses
        if 'vertex' not in procs:
            # This means clusters aren't being drawn, bail
            return
        # print procs.keys()
        for view in range(0,self._baseData._nviews):
            vertices = procs['vertex'].get_vertices(view)
            # print vertices
            self._drawerList[view].drawVertices(vertices)


    def updateImage(self):
        drawn = False
        if not self._baseData._dataHandle._hasFile:
            self.drawBlank()
            return
        else:
            self._baseData._dataHandle.processEvent()
            drawn = True
        if self._drawRawOption.isChecked():
          self.drawRaw()
          drawn = True
        else:
          self.drawBlank()

        if self._mode != "daq":
            if self._dataListsAndLabels['Hits'].currentText() != '--Select--':
              if self._dataListsAndLabels['Hits'].currentText() != '--None--':
                self.drawHits()
                drawn = True
            if self._dataListsAndLabels['Clusters'].currentText() != '--Select--':
              if self._dataListsAndLabels['Clusters'].currentText() != '--None--':
                self.drawClusters()
                drawn = True
            if self._dataListsAndLabels['Vertex'].currentText() != '--Select--':
              if self._dataListsAndLabels['Vertex'].currentText() != '--None--':
                self.drawVertices()
                drawn = True

        if not drawn:
          self.drawBlank()




    def clearDrawnProducts(self):
        for view in range(0,self._baseData._nviews):
            self._drawerList[view].clearHits()
            self._drawerList[view].clearClusters()
            self._drawerList[view].clearVertices()

    def nextEvent(self):
      # if self._mode == "daq":
      #   self._baseData._dataHandle.next()
      # else:
        if self._baseData._dataHandle._event != self._baseData._dataHandle._maxEvent:
          self.goToEvent(self._baseData._dataHandle._event + 1)

    def prevEvent(self):
      # if self._mode == "daq":
      #   self._baseData._dataHandle.prev()
      # else:
        if self._baseData._dataHandle._event != 0:
          self.goToEvent(self._baseData._dataHandle._event - 1)

    def eventEntryChanged(self):
        if not self._baseData._dataHandle._hasFile:
            print "Please select a file before trying to view events."
            self._eventEntry.setText(str(self._baseData._event))
            return
        # Find out what event was requested, attempt to parse to int:
        s = self._eventEntry.displayText()
        # see if it's an int:
        try:
            ev = int(s)
        except Exception, e:
            print "Must enter a number!"
            self._eventEntry.setText(str(self._baseData._event))
            return

        # First, check if this event is valid
        if ev < 0 or ev > self._baseData._dataHandle._maxEvent:
            print "Event must be between 0 and ", self._baseData._maxEvent
            self._eventEntry.setText(str(self._baseData._event))
            return

        self.goToEvent(ev)


    def goToEvent(self, event):
      self._baseData._dataHandle._event = event

      # clear the viewer
      self.clearDrawnProducts()
      # redraw:
      self.updateImage()
      self._eventEntry.setText(str(event))

      r,e = self._baseData._dataHandle.getRunAndEvent()
      self._runLabel.setText("Run: " + str(r))
      self._eventLabel.setText("Ev.: " + str(e))
      # autorange the viewer if selected:
      if self._autoRangeButton.isChecked():
        self.autoRange()

    def refreshGradient(self):
      # print ("Gradient Changed")
      for i in range (0, self._baseData._nviews):
          self._drawerList[i]._item.setLookupTable(self._cmap.getLookupTable(255))

    # def clickImage(self):
        # print

    def setRangeToMax(self):
      for i in range (0, self._baseData._nviews):
        xR = (0,self._baseData._wRange[i])
        yR = (0,self._baseData._tRange)
        self._drawerList[i]._view.setRange(xRange=xR,yRange=yR, padding=0)

    def autoRange(self):
      if self._mode == "daq":
        return
      if self._autoRangeButton.isChecked():
        procs = self._baseData._dataHandle._daughterProcesses
        if 'cluster' not in procs:
            # This means clusters aren't being drawn, bail
            return
        for v in range(0, self._baseData._nviews):
            xR,yR = procs['cluster'].get_range(v)
            self._drawerList[v]._view.setRange(xRange=xR,yRange=yR, padding=0.05)

    def lockAspectRatio(self):
        if self._lockAspectRatio.isChecked():
            ratio = 1.0/self._baseData._aspectRatio
            for v in range(0, self._baseData._nviews):
                self._drawerList[v]._view.setAspectLocked(True, ratio=ratio)
            # self.
        else:
            for v in range(0, self._baseData._nviews):
                self._drawerList[v]._view.setAspectLocked(False)

    def drawWireOption(self):
        if self._drawWireOption.isChecked():
            self._dataBox.addWidget(self._drawerList[-1])
            self._drawerList[-1].setVisible(True)
        else:
            self._dataBox.removeWidget(self._drawerList[-1])
            self._drawerList[-1].setVisible(False)
            self.update()

    def selectFile(self):
        filePath = str(QtGui.QFileDialog.getOpenFileName())
        self.updateFile(filePath)


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


    def screenCapture(self):
        print "Screen Capture!"
        dialog = QtGui.QFileDialog()
        r,e = self._baseData._dataHandle.getRunAndEvent()
        name = "evd_" + self._geometry + "_R" + str(r)
        name = name + "_E" + str(e) + ".png"
        f = dialog.getSaveFileName(self,"Save File",name,
            "PNG (*.png);;JPG (*.jpg);;All Files (*)")

        print f
        # print filt
        # Print
        pixmapImage = QtGui.QPixmap.grabWidget(self)
        pixmapImage.save(f,"PNG")

def main():
    
    parser = argparse.ArgumentParser(description='Python based event display.')
    geom = parser.add_mutually_exclusive_group()
    geom.add_argument('-A', '--argoneut',action='store_true',help="Run with the argoneut geometry")
    geom.add_argument('-U', '--uboone',action='store_true',help="Run with the microboone geometry")
    geom.add_argument('-L', '--lariat',action='store_true',help="Run with the lariat geometry")
    parser.add_argument('file',nargs='?',help="Optional input file to use")
    parser.add_argument('-d',"--daq",action='store_true',help="Run the evd in daq mode.")
    args = parser.parse_args()

    app = QtGui.QApplication(sys.argv)
    geometry = "uboone"
    if args.argoneut:
        geometry = "argoneut"
    elif args.lariat:
        geometry = "lariat"
    if args.daq:
        mode = "daq"
        print "Running in daq mode"
    else:
      mode = ""
    
    ex = evd(geometry,mode,args.file)

    app.exec_()
    # sys.exit(app.exec_())


if __name__ == '__main__':
    main()