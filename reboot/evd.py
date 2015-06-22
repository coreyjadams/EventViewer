
from gui import gui
from event import *
from data import wire
import argparse, sys, signal
from PyQt4 import QtGui, QtCore

from ROOT import evd

from geometry import *

# This is to allow key commands to work when focus is on a box
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

# This is a widget class that contains the label and combo box
# It also knows what to do when updating
class recoBox(QtGui.QWidget):
  activated = QtCore.pyqtSignal(str)

  """docstring for recoBox"""
  def __init__(self,owner,product,producers):
    super(recoBox, self).__init__()
    self._label = QtGui.QLabel()
    self._label.setText(product.capitalize() + ": ")
    self._box = ComboBoxWithKeyConnect()
    self._box.activated[str].connect(self.emitSignal)
    self._product = product
    if producers == None:
      self._box.addItem("--None--")
    else:
      self._box.addItem("--Select--")
      for producer in producers:
        self._box.addItem(producer)
    
    self._box.connectOwnerKPE(owner.keyPressEvent)

    # This is the widget itself, so set it up
    self._layout = QtGui.QVBoxLayout()
    self._layout.addWidget(self._label)
    self._layout.addWidget(self._box)
    self.setLayout(self._layout)

  def keyPressEvent(self, e):
    self._box.keyPressEvent(e)
    super(ComboBoxWithKeyConnect,self).keyPressEvent(e)

  def emitSignal(self, text):
    self.activated.emit(text)

  def product(self):
    return self._product

# Inherit the basic gui to extend it
# override the gui to give the lariat display special features:
class larlitegui(gui):
  """special larlite gui"""
  def __init__(self, geometry,manager):
    super(larlitegui, self).__init__(geometry,manager)
    manager.fileChanged.connect(self.drawableProductsChanged)
    manager.eventChanged.connect(self.update)

  # override the initUI function to change things:
  def initUI(self):
    super(larlitegui,self).initUI()
    # Change the name of the labels for lariat:
    self.update()


  # This function sets up the eastern widget
  def getEastLayout(self):
    # This function just makes a dummy eastern layout to use.
    label1 = QtGui.QLabel("Larlite EVD")
    geoName = self._geometry.name()
    label2 = QtGui.QLabel(geoName.capitalize())
    font = label1.font()
    font.setBold(True)
    label1.setFont(font)
    label2.setFont(font)


    self._eastWidget = QtGui.QWidget()
    # This is the total layout
    self._eastLayout = QtGui.QVBoxLayout()
    # add the information sections:
    self._eastLayout.addWidget(label1)
    self._eastLayout.addWidget(label2)
    self._eastLayout.addStretch(1)

    # The wires are a special case.
    # Use a check box to control wire drawing
    self._wireDrawBox = QtGui.QCheckBox("Draw Wires")
    self._eastLayout.addWidget(self._wireDrawBox)

    # Now we get the list of items that are drawable:
    drawableProducts = self._event_manager.getDrawableProducts()
    self._listOfRecoBoxes = []
    for product in drawableProducts:
      print "Can draw ", product , " with producers: ", self._event_manager.getProducers(product)
      thisBox = recoBox(self,product,self._event_manager.getProducers(product))
      self._listOfRecoBoxes.append(thisBox)
      thisBox.activated[str].connect(self.recoBoxHandler)
      self._eastLayout.addWidget(thisBox)
    self._eastLayout.addStretch(2)

    self._eastWidget.setLayout(self._eastLayout)
    self._eastWidget.setMaximumWidth(150)
    self._eastWidget.setMinimumWidth(100)
    return self._eastWidget

  def drawableProductsChanged(self):
    print "Called here"
    # self.removeItem(self._eastLayout)
    self._eastWidget.close()
    east = self.getEastLayout()
    self.slave.addWidget(east)
    self.update()

    # self._eastLayout.setVisible(False)
    # self._eastLayout.setVisible(True)


  def recoBoxHandler(self,text):
    sender = self.sender()
    print sender.product(), "was changed to" , text
    if text == "--Select--" or text == "--None--":
      self._event_manager.redrawProduct(sender.product(), None, self._view_manager)
      return
    self._event_manager.redrawProduct(sender.product(), text, self._view_manager)

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
  args = parser.parse_args()

  app = QtGui.QApplication(sys.argv)

  if args.uboone:
    geometry = uboone()
  elif args.lariat:
    geometry = lariat()
  else:
    geometry = argoneut()

  # If a file was passed, give it to the manager:


  manager = larlite_manager(geometry)
  manager.setInputFile(args.file)

  thisgui = larlitegui(geometry,manager)
  thisgui.initUI()
  manager.goToEvent(0)


  signal.signal(signal.SIGINT, sigintHandler)
  timer = QtCore.QTimer()
  timer.start(500)  # You may change this if you wish.
  timer.timeout.connect(lambda: None)  # Let the interpreter run each 500 ms.

  app.exec_()
  # sys.exit(app.exec_())


if __name__ == '__main__':
  main()