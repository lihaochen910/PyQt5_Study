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



##----------------------------------------------------------------##
class GraphNodeViewRoot(QtWidgets.QGraphicsItemGroup):
    pass


##----------------------------------------------------------------##
class GraphNodeViewScene(GLGraphicsScene):

    def __init__(self, parent):
        super(GraphNodeViewScene, self).__init__(parent=parent)
        dummyPort = GraphNodePortItem()
        dummyPort.setFlag(dummyPort.ItemHasNoContents, True)
        dummyPort.hide()
        self.rootItem = GraphNodeViewRoot()
        self.addItem(self.rootItem)

        self.dummyPort = dummyPort
        self.addItem(dummyPort)

        self.gridBackground = GridBackground()
        # self.axisGridBackground = AxisGridBackground()
        self.addItem(self.gridBackground)

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

    def contextMenuEvent(self, qContextMenuEvent):
        item = self.itemAt(qContextMenuEvent.scenePos().x(), qContextMenuEvent.scenePos().y(), self.transform)

        print(item)

        if not item:
            self.cmenu = QtWidgets.QMenu()
            newItemAct = self.cmenu.addAction('New Node')
            newItemAct.triggered.connect(lambda: self.createNodeItem(qContextMenuEvent.scenePos()))
            newGpAct = self.cmenu.addAction('New Group')
            newGpAct.triggered.connect(lambda: self.createNodeGroup(qContextMenuEvent.scenePos()))

        elif isinstance(item, GraphNodeItem):
            self.cmenu = QtWidgets.QMenu()
            inAct = self.cmenu.addAction('Add inPort')
            inAct.triggered.connect(lambda: self.createNodeInPort(item))
            outAct = self.cmenu.addAction('Add outPort')
            outAct.triggered.connect(lambda: self.createNodeOutPort(item))
            delAct = self.cmenu.addAction('Delete this item')
            delAct.triggered.connect(lambda: item.delete())

        elif isinstance(item, GraphNodeHeaderItem):
            self.cmenu = QtWidgets.QMenu()
            delAct = self.cmenu.addAction('Delete this item')
            delAct.triggered.connect(lambda: item.parentItem().delete())

        elif isinstance(item, GraphNodePortItem):
            self.cmenu = QtWidgets.QMenu()
            delAct = self.cmenu.addAction('Delete this port')
            delAct.triggered.connect(lambda: item.parentItem().removePort(item))
            print("!!! ", item.parentItem())

        elif isinstance(item, GraphNodeGroupItem):
            self.cmenu = QtWidgets.QMenu()
            editAct = self.cmenu.addAction('Edit Group Name')
            editAct.triggered.connect(lambda: self.showEditGroupNameDialog(item))
            delAct = self.cmenu.addAction('Delete this group')
            delAct.triggered.connect(lambda: self.removeItem(item))


        if self.cmenu:
            selectedAct = self.cmenu.exec_(qContextMenuEvent.screenPos())

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

    def showEditGroupNameDialog(self, item):
        str, okPressed = QtWidgets.QInputDialog.getText(self.cmenu, "Edit", "New Group Name:",
                                                        QtWidgets.QLineEdit.Normal, item.getTitle())
        if okPressed and str.strip():
            item.setTitle(str)

    def createNodeItem(self, pos):
        node = GraphNodeItem()
        node.setPos(pos)
        self.addItem(node)

    def createNodeInPort(self, node):
        str, okPressed = QtWidgets.QInputDialog.getText(self.cmenu, "Add", "InPort Name:",
                                                        QtWidgets.QLineEdit.Normal, 'port')
        if okPressed and str.strip():
            if node.getInPort(str) == None:
                node.addInPort(str, GraphNodePortItem())
                node.updateShape()

    def createNodeOutPort(self, node):
        str, okPressed = QtWidgets.QInputDialog.getText(self.cmenu, "Add", "OutPort Name:",
                                                        QtWidgets.QLineEdit.Normal, 'port')
        if okPressed and str.strip():
            if node.getOutPort(str) == None:
                node.addOutPort(str, GraphNodePortItem())
                node.updateShape()

    def createNodeGroup(self, pos):
        group = GraphNodeGroupItem()
        group.setPos(pos)
        self.addItem(group)


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
            result = self._delegate.mouseReleaseEvent(self, ev)
        # 		if result: return
        return super(GraphNodeView, self).mouseReleaseEvent(ev)

    def mouseMoveEvent(self, ev):
        if self._delegate:
            result = self._delegate.mouseMoveEvent(self, ev)
        # 		if result: return
        return super(GraphNodeView, self).mouseMoveEvent(ev)

_PIXEL_PER_UNIT = 100.0  # basic scale

class GraphNodeView2(GLGraphicsView):
    zoomRate = 1.1
    zoomX = 2
    zoomY = 1

    cursorX = 0
    cursorY = 0

    offsetX = 0

    scrollX = 0
    scrollY = 0

    def __init__(self, *args, **kwargs):
        super(GraphNodeView2, self).__init__(*args, **kwargs)
        self._delegate = GraphicsItemMoveTool()
        self.panning = False
        self.updating = False

    def wheelEvent(self, ev):
        # QtCore.QPoint().y()
        # print(ev.angleDelta())
        steps = ev.angleDelta().y() / 120.0
        if steps > 0:
            self.setZoomX(self.zoomX * self.zoomRate)
            self.setZoomY(self.zoomY * self.zoomRate)
        else:
            self.setZoomX(self.zoomX / self.zoomRate)
            self.setZoomY(self.zoomY / self.zoomRate)

    def mousePressEvent(self, ev):
        if ev.button() == Qt.MidButton:
            offX0, offY0 = self.valueToPos(self.scrollX, self.scrollY)
            self.panning = (ev.pos(), (offX0, offY0))

        if self._delegate:
            result = self._delegate.mousePressEvent(self, ev)
        # 		if result: return
        return super(GraphNodeView2, self).mousePressEvent(ev)

    def mouseReleaseEvent(self, ev):
        if ev.button() == Qt.MidButton:
            if self.panning:
                self.panning = False

        if self._delegate:
            result = self._delegate.mouseReleaseEvent(self, ev)
        # 		if result: return
        return super(GraphNodeView2, self).mouseReleaseEvent(ev)

    def mouseMoveEvent(self, ev):
        if self.panning:
            p1 = ev.pos()
            p0, off0 = self.panning
            # print("%s --> %s" % (p0, p1))
            dx = p0.x() - p1.x()
            dy = p0.y() - p1.y()
            offX0, offY0 = off0
            offX1 = offX0 + dx
            offY1 = offY0 + dy
            self.setScroll(self.xToValue(offX1), self.yToValue(offY1))

        if self._delegate:
            result = self._delegate.mouseMoveEvent(self, ev)
        # 		if result: return
        return super(GraphNodeView2, self).mouseMoveEvent(ev)

    def setScroll(self, x, y):
        self.scrollX = x
        self.scrollY = y
        self.updateTransfrom()

    def setZoomX(self, zoom):
        self.zoomX = zoom
        self.onZoomChanged()

    def setZoomY(self, zoom):
        self.zoomY = zoom
        self.onZoomChanged()

    def onZoomChanged(self):
        self.updateTransfrom()
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
        trans = QTransform()
        trans.translate(self.valueToX(-self.scrollX) + self.offsetX, self.valueToY(-self.scrollY))
        # print('scrollX: %f scrollY: %f', self.scrollX, self.scrollY)
        self.setTransform(trans)
        self.update()
        self.updating = False



##----------------------------------------------------------------##
class GraphNodeViewWidget(QtWidgets.QWidget):

    def __init__(self, *args, **kwargs):
        super(GraphNodeViewWidget, self).__init__(*args, **kwargs)
        layout = QtWidgets.QVBoxLayout(self)
        self.scene = GraphNodeViewScene(parent=self)
        self.scene.setBackgroundBrush(Qt.black)
        self.view = GraphNodeView2(self.scene, parent=self)
        self.view.setScene(self.scene)
        self.view.setSceneRect(QRectF(-1000, -1000, 10000, 10000))
        self.view.centerOn(0, 0)
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
