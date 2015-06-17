
from gui import gui
from event import lariat_manager
import argparse, sys, signal
from PyQt4 import QtGui, QtCore

from geometry import *
    
def sigintHandler(*args):
    """Handler for the SIGINT signal."""
    sys.stderr.write('\r')
    sys.exit()


def main():
    
  parser = argparse.ArgumentParser(description='Python based event display.')
  parser.add_argument('file',nargs='?',help="Optional input file to use")
  args = parser.parse_args()

  app = QtGui.QApplication(sys.argv)

  geom = lariat()
  manager = lariat_manager(geom)

  thisgui = gui(geom,manager)

  signal.signal(signal.SIGINT, sigintHandler)
  timer = QtCore.QTimer()
  timer.start(500)  # You may change this if you wish.
  timer.timeout.connect(lambda: None)  # Let the interpreter run each 500 ms.

  app.exec_()
  # sys.exit(app.exec_())


if __name__ == '__main__':
  main()