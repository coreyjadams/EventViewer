

import sys, signal
import argparse
import collections
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
# from drawingInterface import evd_drawer

# Import the basic event management class
from event import event


class evd_drawer(pg.GraphicsLayoutWidget):
  def __init__(self, geometry,plane=-1):
    super(evd_drawer, self).__init__()
    # add a view box, which is a widget that allows an image to be shown
    self._view = self.addViewBox(border='k')
    # add an image item which handles drawing (and refreshing) the image
    self._item = pg.ImageItem(useOpenGL=True)
    self._view.addItem(self._item)
    # connect the scene to click events, used to get wires
    self.scene().sigMouseClicked.connect(self.mouseClicked)
    # connect the views to mouse move events, used to update the info box at the bottom
    self.scene().sigMouseMoved.connect(self.mouseMoved)
    self._plane = plane
    self._cmSpace = False
    self._geometry = geometry

    # Set up the blank data:
    self._blankData = np.ones((self._geometry.wRange(self._plane),self._geometry.tRange()))

    self.setBackground('w')


    # each drawer contains its own color gradient and levels
    # this class can return a widget containing the right layout for everything
    # Define some color collections:
    self._blankMapCollection    = {'ticks': [(0, (255, 255, 255, 255)), 
                                             (1, (255, 255, 255, 255))], 
                                             'mode': 'rgb'}
    self._daqColorMapCollection = {'ticks': [(0.0,  (30,  30, 255, 255)),
                                             (0.15, (30,  30, 255, 255)), 
                                             (0.6,  (0,  255, 255, 255)), 
                                             (0.8,  (0,  255, 0,   255)), 
                                             (1,    (255,  0, 0,   255))], 
                                             'mode': 'rgb'}
    self._colorMapCollection    = {'ticks': [(0, (30, 30, 255, 255)),
                                             (0.33333, (0, 255, 255, 255)), 
                                             (0.66666, (255,255,100,255)), 
                                             (1, (255, 0, 0, 255))], 
                                             'mode': 'rgb'}

    self._cmap = pg.GradientWidget(orientation='right')
    self._cmap.sigGradientChanged.connect(self.refreshGradient)
    self._cmap.resize(1,1)

    self._blankMap = pg.GradientWidget()
    self._blankMap.restoreState(self._blankMapCollection)

    self._cmap.restoreState(self._colorMapCollection)
    self._item.setLookupTable(self._cmap.getLookupTable(255))

    # These boxes control the levels.
    self._upperLevel = QtGui.QLineEdit()
    self._lowerLevel = QtGui.QLineEdit()

    self._upperLevel.returnPressed.connect(self.levelChanged)
    self._lowerLevel.returnPressed.connect(self.levelChanged)

    self._lowerLevel.setText(str(self._geometry.getLevels(self._plane)[0]))
    self._upperLevel.setText(str(self._geometry.getLevels(self._plane)[1]))

    # Fix the maximum width of the widgets:
    self._upperLevel.setMaximumWidth(35)
    self._cmap.setMaximumWidth(25)
    self._lowerLevel.setMaximumWidth(35)

  def getWidget(self):

    colors = QtGui.QVBoxLayout()
    colors.addWidget(self._upperLevel)
    colors.addWidget(self._cmap)
    colors.addWidget(self._lowerLevel)
    total = QtGui.QHBoxLayout()
    total.addWidget(self)
    total.addLayout(colors)
    widget = QtGui.QWidget()
    widget.setLayout(total)
    return widget

  def levelChanged(self):
    # First, get the current values of the levels:
    lowerLevel = int(self._lowerLevel.text())
    upperLevel = int(self._upperLevel.text())

    # next, set the levels in the geometry:
    self._geometry._levels[self._plane] = (lowerLevel,upperLevel)
    # last, update the levels in the image:
    self._item.setLevels(self._geometry.getLevels(self._plane))

  def refreshGradient(self):
    self._item.setLookupTable(self._cmap.getLookupTable(255))

  def mouseMoved(self, pos):
    self.q = self._item.mapFromScene(pos)
    message= QtCore.QString()
    if self._cmSpace:
      message.append("X: ")
      message.append("{0:.1f}".format(self.q.x()*self._geometry.wire2cm()))
    else:
      message.append("W: ")
      message.append(str(int(self.q.x())))
    if self._cmSpace:
      message.append(", Y: ")
      message.append("{0:.1f}".format(self.q.y()*self._geometry.time2cm()))
    else:
      message.append(", T: ")
      message.append(str(int(self.q.y())))
    # print message
    if self.q.x() > 0 and self.q.x() < self._geometry.wRange(self._plane):
      if self.q.y() > 0 and self.q.y() < self._geometry.tRange():
        self._statusBar.showMessage(message)

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
    self._wdf(self._plane,wire)
    # print "Plane: " + str(self._plane) + ", Wire: " + str(wire)
    # return self.plane,self.wire

  def connectStatusBar(self, _statusBar):
    self._statusBar = _statusBar

  def setRangeToMax(self):
    xR = (0,self._geometry.wRange(self._plane))
    yR = (0,self._geometry.tRange())
    self._view.setRange(xRange=xR,yRange=yR, padding=0)

  def autoRange(self):
    pass

  def lockRatio(self, lockAR ):
    ratio = self._geometry.aspectRatio()
    if lockAR:
      self._view.setAspectLocked(True, ratio=self._geometry.aspectRatio())
    else:
      self._view.setAspectLocked(False)

  def drawPlane(self, image):
    self._item.setImage(image)
    self._item.setLookupTable(self._cmap.getLookupTable(255))
    self._cmap.setVisible(True)
    self._upperLevel.setVisible(True)
    self._lowerLevel.setVisible(True)

  def drawBlank(self):
    print "Trying to draw blank data on plane ", self._plane
    self._item.setImage(self._blankData)
    self._item.setLookupTable(self._blankMap.getLookupTable(255))
    self._cmap.setVisible(False)
    self._upperLevel.setVisible(False)
    self._lowerLevel.setVisible(False)

class view_manager(object):
  """docstring for view_manager"""
  def __init__(self, geometry):
    super(view_manager, self).__init__()
    self._nviews = 0
    self._drawerList = []
    self._cmapList = []
    self._geometry = geometry

    self._wireDrawer = pg.GraphicsLayoutWidget()
    self._wirePlot = self._wireDrawer.addPlot()
    self._wirePlotItem = pg.PlotDataItem()
    self._wirePlot.addItem(self._wirePlotItem)
    self._wireDrawer.setMaximumHeight(100)

        # # Connect the wire drawing box to the planes so that they may
        # # update it
        # for i in range(0, nviews):
        #     self._drawerList[i].connectWireDrawFunction(self.drawWire)


  def addEvdDrawer(self,plane):
    self._drawerList.append(evd_drawer(self._geometry, plane))
    self._nviews += 1
  




  def getDrawListWidget(self):

    # loop through the list and add the drawing windows and their scale
    self._widget = QtGui.QWidget()
    self._layout = QtGui.QVBoxLayout()

    for view in self._drawerList:
      self._layout.addWidget(view.getWidget())

    self._widget.setLayout(self._layout)
    return self._widget

  def connectStatusBar(self,statusBar):
    for view in self._drawerList:
      view.connectStatusBar(statusBar)


  def setRangeToMax(self):
    print "called range to max"
    for view in self._drawerList:
      view.setRangeToMax()

  def autoRange(self):
    print "called autorange"
    for view in self._drawerList:
      view.autoRange()

  def lockAR(self, lockRatio):
    print "called lock AR"
    for view in self._drawerList:
      view.lockRatio(lockRatio)

  def drawWire(self,wireView):
    if wireView:
      self._layout.addWidget(self._wireDrawer)
      self._wireDrawer.setVisible(True)
    else:
      self._layout.removeWidget(self._wireDrawer)
      self._wireDrawer.setVisible(False)

  def useCM(self,useCM):
    for view in self._drawerList:
      view._cmSpace = useCM


  def drawPlanes(self,event_manager):
    for i in xrange(len(self._drawerList)):
      if event_manager.hasWireData():
        self._drawerList[i].drawPlane(event_manager.getPlane(i))
      else:
        self._drawerList[i].drawBlank()

class gui(QtGui.QWidget):

  def __init__(self, geometry,manager):
    super(gui, self).__init__()
    # self._filePath = "/media/cadams/data_linux/argoneut_mc/nue_larlite_all.root"
    self._filePath = None
    # initUI should not do ANY data handling, it should only get the interface loaded
    self._geometry = geometry
    self._event_manager = manager
    self._view_manager = view_manager(geometry)

    self.initUI()


    self._watcher = None
    self._stopFlag = None

  def quit(self):
    # if self._running:
      # self.stopRun()
    QtCore.QCoreApplication.instance().quit()


  # This function prepares the buttons such as prev, next, etc and returns a layout
  def getEventControlButtons(self):

    # This is a box to allow users to enter an event
    self._eventEntry = QtGui.QLineEdit()
    self._eventEntry.setToolTip("Enter an event to skip to that event")
    self._eventEntry.returnPressed.connect(self.nextEventWorker)
    # These labels display current events
    self._runLabel = QtGui.QLabel("Run: 0")
    self._eventLabel = QtGui.QLabel("Ev.: 0")

    # Jump to the next event
    self._nextButton = QtGui.QPushButton("Next")
    self._nextButton.clicked.connect(self._event_manager.next)
    self._nextButton.setToolTip("Move to the next event.")
    # Go to the previous event
    self._prevButton = QtGui.QPushButton("Previous")
    self._prevButton.clicked.connect(self._event_manager.prev)
    self._prevButton.setToolTip("Move to the previous event.")
    # Select a file to use
    self._fileSelectButton = QtGui.QPushButton("Select File")
    self._fileSelectButton.clicked.connect(self._event_manager.selectFile)
    
    # pack the buttons into a box
    self._eventControlBox = QtGui.QVBoxLayout()
    self._eventControlBox.addWidget(self._eventEntry)
    self._runEventGrid = QtGui.QHBoxLayout()
    self._runEventGrid.addWidget(self._runLabel)
    self._runEventGrid.addWidget(self._eventLabel)
    self._eventControlBox.addLayout(self._runEventGrid)
    self._eventControlBox.addWidget(self._nextButton)
    self._eventControlBox.addWidget(self._prevButton)
    self._eventControlBox.addWidget(self._fileSelectButton)

    return self._eventControlBox
    
  # this function helps pass the entry of the line edit item to the event control
  def nextEventWorker(self):
    event = self._eventEntry.text()
    self._event_manager.goToEvent(event)

  # This function prepares the range controlling options and returns a layout
  def getDrawingControlButtons(self):

    # Button to set range to max
    self._maxRangeButton = QtGui.QPushButton("Max Range")
    self._maxRangeButton.setToolTip("Set the range of the viewers to show the whole event")
    self._maxRangeButton.clicked.connect(self._view_manager.setRangeToMax)
    # Check box to active autorange
    self._autoRangeBox = QtGui.QCheckBox("Auto Range")
    self._autoRangeBox.setToolTip("Set the range of the viewers to the regions of interest")
    self._autoRangeBox.setTristate(False)
    self._autoRangeBox.stateChanged.connect(self.autoRangeWorker)  

    self._lockAspectRatio = QtGui.QCheckBox("Lock A.R.")
    self._lockAspectRatio.setToolTip("Lock the aspect ratio to 1:1")
    self._lockAspectRatio.stateChanged.connect(self.lockARWorker)

    # check box to toggle the wire drawing
    self._drawWireOption = QtGui.QCheckBox("Wire Drawing")
    self._drawWireOption.setToolTip("Draw the wires when clicked on")
    self._drawWireOption.stateChanged.connect(self.drawWireWorker)
    self._drawRawOption = QtGui.QCheckBox("Draw Raw")
    self._drawRawOption.setToolTip("Draw the raw wire signals in 2D")
    self._drawRawOption.setTristate(False)

    self._unitDisplayOption = QtGui.QCheckBox("Use cm")
    self._unitDisplayOption.setToolTip("Display the units in cm (checked = true)")
    self._unitDisplayOption.setTristate(False)

    # Pack the stuff into a layout

    self._drawingControlBox = QtGui.QVBoxLayout()
    self._drawingControlBox.addWidget(self._maxRangeButton)
    self._drawingControlBox.addWidget(self._autoRangeBox)
    self._drawingControlBox.addWidget(self._lockAspectRatio)
    self._drawingControlBox.addWidget(self._drawWireOption)
    self._drawingControlBox.addWidget(self._unitDisplayOption)

    return self._drawingControlBox

  def autoRangeWorker(self):
    if self._autoRangeBox.isChecked():
      self._view_manager.autoRange()

  def lockARWorker(self):
    if self._lockAspectRatio.isChecked():
      self._view_manager.lockAR(True)
    else:
      self._view_manager.lockAR(False)

  def drawWireWorker(self):
    if self._drawWireOption.isChecked():
      self._view_manager.drawWire(True)
    else:
      self._view_manager.drawWire(False)    

  def useCMWorker(self):
    if self._drawWireOption.isChecked():
      self._view_manager.useCM(True)
    else:
      self._view_manager.useCM(False)    

  # This function prepares the quit buttons layout and returns it
  def getQuitLayout(self):
    self._quitButton = QtGui.QPushButton("Quit")
    self._quitButton.setToolTip("Close the viewer.")
    self._quitButton.clicked.connect(self.quit)
    return self._quitButton

  # This function combines the control button layouts, range layouts, and quit button
  def getWestLayout(self):
    event_control = self.getEventControlButtons()
    draw_control = self.getDrawingControlButtons()

    # Add the quit button?
    quit_control = self.getQuitLayout()
    
    self._westLayout = QtGui.QVBoxLayout()
    self._westLayout.addLayout(event_control)
    self._westLayout.addStretch(1)
    self._westLayout.addLayout(draw_control)
    self._westLayout.addStretch(1)
    self._westLayout.addWidget(quit_control)
    self._westWidget = QtGui.QWidget()
    self._westWidget.setLayout(self._westLayout)
    self._westWidget.setMaximumWidth(200)
    self._westWidget.setMinimumWidth(100)
    return self._westWidget


  def getSouthLayout(self):
    # This layout contains the status bar and the capture screen buttons

    # The screen capture button:
    self._screenCaptureButton = QtGui.QPushButton("Capture Screen")
    self._screenCaptureButton.setToolTip("Capture the entire screen to file")
    self._screenCaptureButton.clicked.connect(self.screenCapture)
    self._southWidget = QtGui.QWidget()
    self._southLayout = QtGui.QHBoxLayout()
    # Add a status bar
    self._statusBar = QtGui.QStatusBar()
    self._statusBar.showMessage("Test message")
    self._southLayout.addWidget(self._statusBar)
    # self._southLayout.addStretch(1)
    self._southLayout.addWidget(self._screenCaptureButton)
    self._southWidget.setLayout(self._southLayout)

    return self._southWidget

  def getEastLayout(self):
    # This function just makes a dummy eastern layout to use.
    label = QtGui.QLabel("Dummy")
    self._eastWidget = QtGui.QWidget()
    self._eastLayout = QtGui.QVBoxLayout()
    self._eastLayout.addWidget(label)
    self._eastLayout.addStretch(1)
    self._eastWidget.setLayout(self._eastLayout)
    self._eastWidget.setMaximumWidth(200)
    self._eastWidget.setMinimumWidth(100)
    return self._eastWidget

  def initUI(self):


    # Get all of the widgets:
    eastWidget  = self.getEastLayout()
    westWidget  = self.getWestLayout()
    southLayout = self.getSouthLayout()

    # Area to hold data:
    print type(self._geometry)
    nviews = self._geometry.nViews()
    # nviews = self._baseData._nviews
    for i in range(0, nviews):
      # These boxes hold the wire/time views:
      self._view_manager.addEvdDrawer(i)

    self._view_manager.connectStatusBar(self._statusBar)

    drawListWidget = self._view_manager.getDrawListWidget()


    # Connect the wire drawing box to the planes so that they may
    # update it
    # for i in range(0, nviews):
        # self._drawerList[i].connectWireDrawFunction(self.drawWire)

    # Put the layout together


    master = QtGui.QVBoxLayout()
    slave = QtGui.QHBoxLayout()
    slave.addWidget(westWidget)
    slave.addWidget(drawListWidget)
    slave.addWidget(eastWidget)
    master.addLayout(slave)
    master.addWidget(southLayout)

    self.setLayout(master)    

    # ask the view manager to draw the planes:
    self._view_manager.drawPlanes(self._event_manager)
    
    self.setGeometry(800, 300, 1200, 800)
    self.setWindowTitle('Event Display')    
    self.setFocus()
    self.show()

  def keyPressEvent(self,e):
    if e.key() == QtCore.Qt.Key_N:
      self._event_manager.next()
      return
    if e.key() == QtCore.Qt.Key_P:
      self._event_manager.prev()
      return
    if e.key() == QtCore.Qt.Key_C:
      # print "C was pressed"
      if e.modifiers() and QtCore.Qt.ControlModifier :
        self.quit()
        return

    # if e.key() == QtCore.Qt.Key_C:
  #     self._dataListsAndLabels['Clusters'].setFocus()
    # if e.key() == QtCore.Qt.Key_H:
  #     self._dataListsAndLabels['Hits'].setFocus()

    if e.key() == QtCore.Qt.Key_R:
      self.setRangeToMax()
      return

    super(gui, self).keyPressEvent(e)

  def screenCapture(self):
    print "Screen Capture!"
    dialog = QtGui.QFileDialog()
    r = self._event_manager.run()
    e = self._event_manager.event()

    name = "evd_" + self._geometry + "_R" + str(r)
    name = name + "_E" + str(e) + ".png"
    f = dialog.getSaveFileName(self,"Save File",name,
        "PNG (*.png);;JPG (*.jpg);;All Files (*)")

    print f
    # print filt
    # Print
    pixmapImage = QtGui.QPixmap.grabWidget(self)
    pixmapImage.save(f,"PNG")



def sigintHandler(*args):
    """Handler for the SIGINT signal."""
    sys.stderr.write('\r')
    sys.exit()

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
  
  ex = gui(geometry,mode,args.file)

  signal.signal(signal.SIGINT, sigintHandler)
  timer = QtCore.QTimer()
  timer.start(500)  # You may change this if you wish.
  timer.timeout.connect(lambda: None)  # Let the interpreter run each 500 ms.

  app.exec_()
  # sys.exit(app.exec_())


if __name__ == '__main__':
  main()


