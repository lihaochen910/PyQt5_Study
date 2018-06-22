from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import uic

class SplashScreen(QtWidgets.QWidget):
    def __init__(self, pixmap):
        super(SplashScreen, self).__init__()
        uic.loadUi('../res/splash.ui', self)
        self.resize(600, 200)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.FramelessWindowHint)
        self.title.setStyleSheet("QLabel { background-color: rgba((0, 0, 0, 0%)); color:black; margin: 5px 0px 0px 10px; }")
        self.message = None
        self.painter = QtGui.QPainter()
        self.painterFont = QtGui.QFont('Consolas', 9, QtGui.QFont.Black)
        self.painterFont.setPixelSize(15)
        self.png = pixmap

    def setTitle(self, titleText):
        self.title.setText(titleText)

    def setMessage(self, msgText):
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


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)

    splash = SplashScreen(QtGui.QPixmap('../res/logo2.png'))
    splash.setTitle('Title')
    splash.setMessage('message')
    splash.show()

    app.processEvents()

    import time
    time.sleep(1)

    splash.close()

    sys.exit(app.exec_())