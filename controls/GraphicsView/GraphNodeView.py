# -*- coding: utf-8 -*-
import sys
import math

from PyQt5 import QtGui, QtWidgets, QtCore, QtOpenGL, uic
from PyQt5.QtCore import Qt, QObject, QEvent, pyqtSignal
from PyQt5.QtCore import QPoint, QRect, QSize
from PyQt5.QtCore import QPointF, QRectF, QSizeF
from PyQt5.QtGui import QColor

from controls.GraphicsView.GraphicsViewHelper import *
from controls.GraphicsView.GraphNodeConnectionItem import *
from controls.GraphicsView.CurveView import *

_PIXEL_PER_UNIT = 100.0  # basic scale

##----------------------------------------------------------------##
class GraphNodeViewRoot(QtWidgets.QGraphicsItemGroup):
    pass


##----------------------------------------------------------------##
class GraphNodeViewScene(GLGraphicsScene):
    zoomRate = 1.1
    zoomX = 2
    zoomY = 1

    cursorX = 0
    cursorY = 0

    offsetX = 0

    scrollX = 0
    scrollY = 0

    def __init__(self, parent):
        super(GraphNodeViewScene, self).__init__(parent=parent)
        dummyPort = GraphNodePortItem()
        dummyPort.setFlag(dummyPort.ItemHasNoContents, True)
        dummyPort.hide()
        self.rootItem = GraphNodeViewRoot()
        self.addItem(self.rootItem)

        self.dummyPort = dummyPort
        self.addItem(dummyPort)

        # self.gridBackground = GridBackground()
        self.axisGridBackground = AxisGridBackground()
        self.addItem(self.axisGridBackground)

        self.connecting = None
        self.sceneRectChanged.connect(self.onRectChanged)
        self.transform = QTransform()

        self.updating = False

    def clear(self):
        super(GraphNodeViewScene, self).clear()

    def onRectChanged(self, rect):
        pass
        # print('sceneRectChanged! %s', self.axisGridBackground.rect())
        # self.gridBackground.setRect(rect)
        # print("self.gridBackground.setRect(rect)")

    def tryStartConnection(self, port):
        targetPort = self.dummyPort
        conn = GraphNodeCurveConnectionItem(port, targetPort)
        if port.dir == -1:
            targetPort.dir = 1
        else:
            targetPort.dir = -1
        self.addItem(conn)
        self.connecting = conn
        return True

    def setZoomX(self, zoom):
        self.zoomX = zoom
        self.onZoomChanged()

    def setZoomY(self, zoom):
        self.zoomY = zoom
        self.onZoomChanged()

    def onZoomChanged(self):
        self.axisGridBackground.setZoom(self.zoomX, self.zoomY)
        # self.updateTransfrom()
        # self.cursorItem.setX( self.valueToX( self.cursorX ) )
        # self.axisGridBackground.setCursorPosX(self.valueToX(self.cursorX))

    def xToValue(self, x):
        return x / (_PIXEL_PER_UNIT * self.zoomX)

    def valueToX(self, v):
        return v * self.zoomX * _PIXEL_PER_UNIT

    def yToValue(self, y):
        return y / (_PIXEL_PER_UNIT * self.zoomY)

    def valueToY(self, v):
        return v * self.zoomY * _PIXEL_PER_UNIT

    def valueToPos(self, x, y):
        return (self.valueToX(x), self.valueToY(y))

    def posToValue(self, xv, yv):
        return (self.xToValue(xv), self.yToValue(yv))

    def updateTransfrom(self):
        if self.updating: return
        self.updating = True
        # trans = QTransform()
        # trans.translate(self.valueToX(-self.scrollX) + self.offsetX, self.valueToY(-self.scrollY))
        # self.setTransform(trans)
        self.update()
        self.updating = False

    def wheelEvent(self, event):
        steps = event.delta() / 120.0
        dx = 0
        dy = 0
        if steps > 0:
            self.setZoomX(self.zoomX * self.zoomRate)
            self.setZoomY(self.zoomY * self.zoomRate)
        else:
            self.setZoomX(self.zoomX / self.zoomRate)
            self.setZoomY(self.zoomY / self.zoomRate)
        # if event.orientation() == Qt.Horizontal:
        #     dy = steps
        #     if dy > 0:
        #         self.setZoomY(self.zoomY * self.zoomRate)
        #     else:
        #         self.setZoomY(self.zoomY / self.zoomRate)
        # else:
        #     dy = steps
        #     if dy > 0:
        #         self.setZoomX(self.zoomX * self.zoomRate)
        #     else:
        #         self.setZoomX(self.zoomX / self.zoomRate)

    def mousePressEvent(self, event):
        item = self.itemAt(event.scenePos().x(), event.scenePos().y(), self.transform)
        if not item: return
        if isinstance(item, GraphNodePortItem):
            self.dummyPort.setPos(event.scenePos())
            if self.tryStartConnection(item): return
        super(GraphNodeViewScene, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.connecting:
            if event.scenePos().x() > self.connecting.srcPort.scenePos().x():
                self.dummyPort.dir = -1
            else:
                self.dummyPort.dir = 1
            self.dummyPort.setPos(event.scenePos())
            self.dummyPort.updateConnections()
        super(GraphNodeViewScene, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.connecting:
            self.dummyPort.setPos(event.scenePos())
            item = self.itemAt(event.scenePos().x(),
                               event.scenePos().y(), self.transform)
            if isinstance(item, GraphNodePortItem):
                if not self.connecting.setDstPort(item):  # not accepted
                    self.connecting.delete()
            else:
                self.connecting.delete()
            self.connecting = None
        super(GraphNodeViewScene, self).mouseReleaseEvent(event)


##----------------------------------------------------------------##
class GraphicsViewDelegate():
    def mousePressEvent(self, view, ev):
        return None

    def mouseReleaseEvent(self, view, ev):
        return None

    def mouseMoveEvent(self, view, ev):
        return None


##----------------------------------------------------------------##
class GraphicsItemMoveTool(GraphicsViewDelegate):
    def mousePressEvent(self, view, ev):
        item = view.itemAt(ev.pos())
        return True

    def mouseReleaseEvent(self, view, ev):
        return True

    def mouseMoveEvent(self, view, ev):
        return True


##----------------------------------------------------------------##
class GraphNodeView(GLGraphicsView):
    def __init__(self, *args, **kwargs):
        super(GraphNodeView, self).__init__(*args, **kwargs)
        self._delegate = GraphicsItemMoveTool()

    def mousePressEvent(self, ev):
        print(ev.pos())
        if self._delegate:
            result = self._delegate.mousePressEvent(self, ev)
        # 		if result: return
        return super(GraphNodeView, self).mousePressEvent(ev)

    def mouseReleaseEvent(self, ev):
        if self._delegate:
            result = self._delegate.mouseReleaseEvent( self, ev )
        # 		if result: return
        return super(GraphNodeView, self).mouseReleaseEvent(ev)

    def mouseMoveEvent(self, ev):
        if self._delegate:
            result = self._delegate.mouseMoveEvent( self, ev )
        # 		if result: return
        return super(GraphNodeView, self).mouseMoveEvent(ev)


##----------------------------------------------------------------##
class GraphNodeViewWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super(GraphNodeViewWidget, self).__init__(*args, **kwargs)
        layout = QtWidgets.QVBoxLayout(self)
        self.scene = GraphNodeViewScene(parent=self)
        self.scene.setBackgroundBrush(Qt.black)
        self.view = GraphNodeView(self.scene, parent=self)
        self.view.setSceneRect(QRectF(0, 0, 10000, 10000))
        layout.addWidget(self.view)
        layout.setSpacing(0)
        layout.setContentsMargins(QtCore.QMargins())

        self.nodeToItem = {}

    def getItemByNode(self, node):
        return self.nodeToItem.get(node)

    def getNodeByItem(self, item):
        return item.node

    def addNode(self, node):
        item = self.createItemForNode(node)
        item.node = node
        self.nodeToItem[node] = item
        return

    def removeNode(self, node):
        item = self.getItemByNode(node)
        if not item: return
        del self.nodeToItem[node]
        item.delete()

    def createItemForNode(self, node):
        item = GraphNodeItem()
        return item

    def rebuild(self):
        pass

    def clear(self):
        self.scene.clear()
        self.nodeToItem = {}

    def closeEvent(self, event):
        self.view.deleteLater()

    def __del__(self):
        self.deleteLater()


if __name__ == '__main__':
    import TestGraphView
