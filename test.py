import sys

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import uic

from PyQt5.QtCore import *

from PyQt5.QtWidgets import QApplication, QMenu
from PyQt5.QtGui import QIcon

class mySplashScreen(QtWidgets.QWidget):
    def __init__(self, pixmap):
        super(mySplashScreen, self).__init__()
        uic.loadUi('res/splash.ui', self)
        self.resize(600, 200)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.title.setStyleSheet("QLabel { background-color: rgba((0, 0, 0, 0%)); color:black; margin: 5px 0px 0px 10px; }")
        self.message = None
        self.painter = QtGui.QPainter()
        self.painterFont = QtGui.QFont('Consolas', 9, QtGui.QFont.Black)
        self.painterFont.setPixelSize(15)
        self.png = pixmap

    def setTitle(self, titleText):
        self.title.setText(titleText)

    def showMessage(self, msgText):
        self.message = msgText
        self.repaint()

    def paintEvent(self, qPaintEvent):
        self.painter.begin(self)
        self.painter.drawPixmap(0, 0, 600, 200, self.png)
        self.painter.setFont(self.painterFont)
        self.painter.setPen(QtGui.QColor(0, 0, 0))
        if self.message != None:
            self.painter.drawText(475, 190, self.message)
        self.painter.end()

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

    splash = mySplashScreen(splashPix)
    splash.setTitle('Kanbaru')
    splash.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
    splash.show()
    splash.showMessage("v0.0.1")
    app.processEvents()

    import time
    time.sleep(2)

    splash.showMessage("Load Editor...")
    time.sleep(0.3)

    splash.showMessage("Load TimeLine...")
    time.sleep(0.4)

    widget = MyWidget()
    widget.show()

    splash.close()

    sys.exit(app.exec_())



