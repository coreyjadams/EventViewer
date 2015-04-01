import sys
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import rawdata as rd


class Example(QtGui.QWidget):
    
    def __init__(self):
        super(Example, self).__init__()
        
        self.initUI()
        
    def initUI(self):
        
        okButton = QtGui.QPushButton("OK")
        cancelButton = QtGui.QPushButton("Cancel")

        # Buttons for using the event display:
        _nextButton = QtGui.QPushButton("Next")
        _prevButton = QtGui.QPushButton("Previous")
        _quitButton = QtGui.QPushButton("Quit")

        # Bind quit to the proper functionality
        _quitButton.clicked.connect(QtCore.QCoreApplication.instance().quit)


        _controlBox = QtGui.QVBoxLayout()
        _controlBox.addWidget(_nextButton)
        _controlBox.addWidget(_prevButton)
        _controlBox.addStretch(1)
        _controlBox.addWidget(_quitButton)

        grid = QtGui.QGridLayout()
        # grid.setSpacing(10)

        # grid.addWidget(_nextButton,1,0)
        # grid.addWidget(_prevButton,2,0)
        grid.addLayout(_controlBox,1,0,2,1)

        # _emptySpace1 = QtGui.QTextEdit()
        # _emptySpace2 = QtGui.QTextEdit()

        _emptySpace1 = pg.GraphicsLayoutWidget()
        _emptySpace2 = pg.GraphicsLayoutWidget()

        _item1 = pg.ImageItem()
        _item2 = pg.ImageItem()

        _view1 = _emptySpace1.addViewBox()
        _view2 = _emptySpace2.addViewBox()
        _view1.addItem(_item1)
        _view2.addItem(_item2)

        grid.addWidget(_emptySpace1,1,1)
        grid.addWidget(_emptySpace2,2,1)

        r = rd.RawData()
        r.config_argo()
        r.init_proc()
        r.add_input_file("/media/cadams/data_linux/argoneut_mc/nue_larlite_all.root")
        d = r.get_img()

        print type(d[0])
        print len(d[0])

        _item1.setImage(d[0].T)
        _item2.setImage(d[1].T)

        
        self.setLayout(grid)    
        
        self.setGeometry(800, 300, 800, 800)
        self.setWindowTitle('Buttons')    
        self.show()
        
def main():
    
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()