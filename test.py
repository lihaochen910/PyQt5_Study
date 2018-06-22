import sys

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import uic

from PyQt5.QtCore import *

from PyQt5.QtWidgets import QApplication, QMenu
from PyQt5.QtGui import QIcon

class MyWidget(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWidget, self).__init__()
        self.resize(500, 500)
        self.initUi()

    def initUi(self):
        self.setWindowTitle('MyWindow')

        openAct = QtWidgets.QAction(QIcon('res/exit.png'), 'Open', self)
        openAct.triggered.connect(self.openFile)

        exitAct = QtWidgets.QAction(QIcon('res/exit.png'), 'Exit', self)
        exitAct.triggered.connect(self.close)

        menubar = self.menuBar()

        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(openAct)
        fileMenu.addAction(exitAct)

        toolbar = QtWidgets.QToolBar()
        toolbar.resize(300, 300)
        toolbar.addAction(exitAct)

        self.textWidget = QtWidgets.QTextEdit()
        self.textWidget.acceptRichText()
        self.setCentralWidget(self.textWidget)

        self.addToolBar(toolbar)

    def openFile(self):
        print("openFile")
        fname = QtWidgets.QFileDialog.getOpenFileName(self, 'open file', './')


        if fname[0]:
            txt = open(fname[0], 'r').read()
            print(txt)
            self.textWidget.setText(txt)

    def closeEvent(self, QCloseEvent):
        print('closeEvent')
        # result = QMessageBox(QIcon('is.png'), 'yes', 'no')

    def contextMenuEvent(self, qContextMenuEvent):

        cmenu = QMenu()
        newAct = cmenu.addAction('New')
        newAct.triggered.connect(self.close)

        selectedAct = cmenu.exec_(self.mapToGlobal(qContextMenuEvent.pos()))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(open('res/QtDarkOrange.qss').read())

    splashPix = QtGui.QPixmap('res/logo2.png')

    from controls.SplashScreen import *

    splash = SplashScreen(splashPix)
    splash.setTitle('GraphNode')
    splash.show()
    splash.setMessage("v0.1")
    app.processEvents()

    import time
    time.sleep(0.3)

    # splash.setMessage("Load Editor...")
    # time.sleep(0.3)
    #
    # splash.setMessage("Load TimeLine...")
    # time.sleep(0.4)

    # widget = MyWidget()
    # widget.show()

    from controls.GraphicsView.TestGraphView import *
    g = TestGraphNodeViewWidget()
    g.resize(600, 300)
    g.show()
    g.raise_()

    splash.close()

    sys.exit(app.exec_())



