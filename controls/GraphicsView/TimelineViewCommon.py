import sip
sip.setapi("QString", 2)
sip.setapi('QVariant', 2)

from PyQt5 import QtGui, QtWidgets, QtCore, QtOpenGL, uic
from PyQt5.QtCore import Qt, QObject, QEvent, pyqtSignal
from PyQt5.QtCore import QPoint, QRect, QSize
from PyQt5.QtCore import QPointF, QRectF, QSizeF
from PyQt5.QtGui import QColor, QTransform

from controls.GraphicsView.GraphicsViewHelper import *

##----------------------------------------------------------------##
class TimelineCursorItem( QtWidgets.QGraphicsLineItem ):
	_pen  = makePen( color = '#a3ff00', width = 1 )
	def __init__( self ):
		super( TimelineCursorItem, self ).__init__()
		self.setPen( self._pen )

##----------------------------------------------------------------##
class TimelineMarkerLineItem( QtWidgets.QGraphicsLineItem ):
	_pen  = makePen( color = '#7569d0', width = 1 )
	def __init__( self ):
		super( TimelineMarkerLineItem, self ).__init__()
		self.setLine( 0,0,0,1000)
		self.setZValue( 800 )
		self.setPen( self._pen )
		self.parentMarker = None
		self.view = None

	def setMarker( self, marker ):
		self.parentMarker = marker
		self.parentMarker.lineItems.append( self )

	def getTimePos( self ):
		return self.parentMarker.timePos

	def getTimeLength( self ):
		return self.parentMarker.timeLength

	def paint( self, painter, option, widget ):
		painter.setRenderHint( QtGui.QPainter.Antialiasing, False )
		return super( TimelineMarkerLineItem, self ).paint( painter, option, widget )

	def updateShape( self ):
		self.view.updateMarkerPos( self )

	def delete( self ):
		view = self.view
		view.removeMarkerLine( self )
