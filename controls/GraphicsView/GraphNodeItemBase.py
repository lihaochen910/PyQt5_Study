# -*- coding: utf-8 -*-

from PyQt5 import QtGui, QtWidgets, QtCore, QtOpenGL, uic
from PyQt5.QtCore import Qt, QObject, QEvent, pyqtSignal
from PyQt5.QtCore import QPoint, QRect, QSize
from PyQt5.QtCore import QPointF, QRectF, QSizeF
from PyQt5.QtGui import QColor, QTransform

from controls.GraphicsView.GraphicsViewHelper import *

import sys
import math


##----------------------------------------------------------------##
class GraphNodeItemBase():
    def isGroup(self):
        return False

    def initGraphNode(self):
        pass

    def acceptConnection(self, conn):
        return False

    def createConnection(self, **options):
        return None


if __name__ == '__main__':
    import TestGraphView
