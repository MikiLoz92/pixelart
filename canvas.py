#!/usr/bin/env python
#coding: utf-8

import sys

from PyQt4 import QtGui, QtCore, QtOpenGL
from PyQt4.QtCore import Qt


class Selection(QtGui.QRubberBand):

	def __init__(self, origin, data, parent=None):

		super(Selection, self).__init__(QtGui.QRubberBand.Rectangle, parent)

		self.data = data

		self.origin = QtCore.QPoint(origin)
		self.originTopLeft = QtCore.QPoint()
		self.finished = False
		self.moving = False
		self.image = None
		self.rect = QtCore.QRect()

	def setGeometry(self, x, y, w, h): # Todos los argumentos son el imagen, no en el Canvas

		self.rect = QtCore.QRect(x, y, w, h)
		super(Selection, self).setGeometry( x * self.data.zoom - 1, y * self.data.zoom - 1, w * self.data.zoom + 2, h * self.data.zoom + 2 )

"""
class ToolHint(QtGui.QRubberBand):

	def __init__(self, origin, data, parent=None):

		super(ToolHint, self).__init__(QtGui.QRubberBand.Rectangle, parent)

		self.data = data

		self.origin = origin
		self.rect = QtCore.QRect()

	def setGeometry(self, x, y):

		self.rect = QtCore.QRect(x, y, 1, 1)
		super(ToolHint, self).setGeometry( x * self.data.zoom, y * self.data.zoom, 1 * self.data.zoom + 1, 1 * self.data.zoom + 1 )
"""		


class Canvas(QtGui.QLabel):
	"""
	La clase Canvas representa el lienzo donde pintaremos.
	Se expande de tamaño a medida que aumentamos el zoom.
	"""

	def __init__(self, w, h, data, com, color, parent=None):

		#super(Canvas, self).__init__(QtOpenGL.QGLFormat(QtOpenGL.QGL.SampleBuffers), parent)
		super(Canvas, self).__init__(parent)

		self.setBackgroundRole(QtGui.QPalette.Base)
		self.setAttribute(Qt.WA_TranslucentBackground)
		self.setMouseTracking(True)
		self.setAcceptDrops(True)
		self.setObjectName("Canvas")

		self.com = com
		self.com.zoom.connect(self.zoom)
		self.com.updateCanvas.connect(self.update)
		self.com.resizeCanvas.connect(self.resize)
		self.com.updateTool.connect(self.applySelection)
		self.com.updateTool.connect(self.changeCursor)
		self.com.newImage.connect(self.resizeToNewImage)
		#self.com.onClickPalette.connect(self.hideToolHint)

		self.com.cutImage.connect(self.cutImage)
		self.com.copyImage.connect(self.copyImage)
		self.com.pasteImage.connect(self.pasteImage)
		self.com.clearImage.connect(self.clearImage)

		self.parent = parent
		self.data = data

		self.setPixmap(QtGui.QPixmap.fromImage(self.data.image))

		self.drawing = False
		self.selecting = False
		self.data.selection = None
		#self.toolHint = None

	def enterEvent(self, event): # Cuando entra el ratón en el Canvas cambiamos el cursor

		super(Canvas, self).enterEvent(event)
		if not self.data.colorPicker:
			self.changeCursor()
		self.com.enterCanvas.emit()

	def leaveEvent(self, event): # Si el ratón se va, lo reiniciamos

		super(Canvas, self).leaveEvent(event)
		self.unsetCursor()
		self.com.leaveCanvas.emit()

	def changeCursor(self):

		cursors = [0, self.data.pencilCur, self.data.eraserCur, self.data.colorPickerCur, self.data.fillCur, 0, 0]
		for i in range(7):
			if self.data.currentTool == i:
				if cursors[i] == 0:
					self.unsetCursor()
				else:
					self.setCursor(cursors[i])
	"""
	def dragEnterEvent(self, event):

		event.acceptProposedAction()
		print event.mimeData()

	def dragMoveEvent(self, event):

		event.acceptProposedAction()

	def dropEvent(self, event):

		mimeData = event.mimeData()
		if mimeData.hasImage() and not mimeData.imageData().isNull():
			self.data.image = QtGui.QImage(mimeData.imageData())
			self.com.updateCanvas.emit()
			self.com.resizeCanvas.emit()
		event.acceptProposedAction()
	"""
	def mousePressEvent(self, event):

		pos = event.pos()
		x = pos.x() / self.data.zoom # x de la imagen
		y = pos.y() / self.data.zoom # y de la imagen

		# Selección
		if self.data.currentTool == 0:
			if event.button() == Qt.LeftButton:
				if not self.data.selection:
					# Crear una nueva selección
					self.data.selection = Selection(QtCore.QPoint(x, y), self.data, self)
				else:
					if self.data.selection.rect.contains(QtCore.QPoint(x, y)):
						# Mover selección
						self.data.selection.moving = True
						#self.data.selectionGrabPoint = pos
						self.data.selectionGrabPoint = QtCore.QPoint(x - self.data.selection.rect.x(), y - self.data.selection.rect.y())
					else:
						if self.data.selection.image != None:
							# Pintamos la imagen seleccionada en la imagen final
							self.applySelection()
						self.data.selection = Selection(QtCore.QPoint(x, y), self.data, self)
			elif event.button() == Qt.RightButton:
				pass

		# Lápiz
		elif self.data.currentTool == 1:
			self.lastPoint = QtCore.QPoint(x,y)
			if self.drawing:
				self.drawing = False
				self.data.image = QtGui.QImage(self.data.history[self.data.posHistory])
			elif event.button() == Qt.LeftButton or event.button() == Qt.RightButton:
				color = self.data.primaryColor if event.button() == Qt.LeftButton else self.data.secondaryColor
				size = self.data.pencilSize
				if event.button() == Qt.RightButton and self.data.secondaryColorEraser:
					color = self.data.bgColor
					size = self.data.eraserSize
				self.data.paintPoint(x, y, color)
				self.drawing = True
			self.com.updateCanvas.emit()

		# Goma
		elif self.data.currentTool == 2:
			if event.button() == Qt.LeftButton or event.button() == Qt.RightButton:
				self.lastPoint = QtCore.QPoint(x,y)
				self.data.paintPoint(x, y, self.data.bgColor)
				self.com.updateCanvas.emit()
				self.drawing = True

		# Pipeta de color
		elif self.data.currentTool == 3:
			if event.button() == Qt.LeftButton:
				self.data.changePrimaryColor( QtGui.QColor(self.data.image.pixel(QtCore.QPoint(x,y))) )
			elif event.button() == Qt.RightButton:
				self.data.changeSecondaryColor( QtGui.QColor(self.data.image.pixel(QtCore.QPoint(x,y))) )
			self.com.updateColor.emit()

		# Cubo
		elif self.data.currentTool == 4:
			if event.button() == Qt.LeftButton:
				self.fillImage( (x, y), self.data.primaryColor, self.data.image.pixel(x,y), self.data.image )
			elif event.button() == Qt.RightButton:
				self.fillImage( (x, y), self.data.secondaryColor, self.data.image.pixel(x,y), self.data.image )
			self.data.addHistoryStep()
			self.com.updateCanvas.emit()

		# Degradado
		elif self.data.currentTool == 5:
			if event.button() == Qt.LeftButton:
				self.data.gradient = Selection(QtCore.QPoint(x, y), self.data, self)

		# Mover canvas
		if event.button() == Qt.MiddleButton:
			self.grabPoint = event.pos()

		self.update()

		# DEBUG
		# print self.width(), self.height()
		# print self.data.image.width(), self.data.image.height()
		# print x,y

	def mouseMoveEvent(self, event):

		pos = event.pos()
		x = pos.x() / self.data.zoom # x de la imagen
		y = pos.y() / self.data.zoom # y de la imagen
		self.data.xcursor = x
		self.data.ycursor = y

		self.com.overCanvas.emit(x, y)

		# Selección
		if self.data.currentTool == 0:
			if event.buttons() == Qt.LeftButton:
				if not self.data.selection.finished:
					self.selecting = True
					self.resizeSelection(self.data.selection, event.pos().x(), event.pos().y())
				if self.data.selection.moving:
					self.moveSelection(event.pos().x(), event.pos().y())

		# Lápiz
		elif self.data.currentTool == 1:
			endPoint = QtCore.QPoint(x,y)
			if event.buttons() == Qt.LeftButton and self.drawing:
				self.drawLineTo(QtCore.QPoint(x,y), self.data.primaryColor)
				self.com.updateCanvas.emit()
				self.lastPoint = QtCore.QPoint(endPoint)
			elif event.buttons() == Qt.RightButton and self.drawing:
				color = self.data.secondaryColor
				if self.data.secondaryColorEraser:
					color = self.data.bgColor
				self.drawLineTo(QtCore.QPoint(x,y), color)
				self.com.updateCanvas.emit()
				self.lastPoint = QtCore.QPoint(endPoint)

		# Goma
		elif self.data.currentTool == 2:
			if event.buttons() == Qt.LeftButton or event.buttons() == Qt.RightButton:
				endPoint = QtCore.QPoint(x,y)
				self.drawLineTo(QtCore.QPoint(x,y), self.data.bgColor)
				self.com.updateCanvas.emit()
				self.lastPoint = QtCore.QPoint(endPoint)

		# Degradado
		if self.data.currentTool == 5:
			if event.buttons() == Qt.LeftButton:
				if self.data.gradient and not self.data.gradient.finished:
					self.selecting = True
					self.resizeSelection(self.data.gradient, event.pos().x(), event.pos().y())

		if event.buttons() == Qt.MiddleButton:
			
			self.move(self.mapToParent(event.pos() - self.grabPoint))

			"""
			print "event pos:", self.mapToParent(pos).x(), "parent.width:", self.parent.width(), "width:", self.width()
			if (self.mapToParent(pos).x() + self.width() - self.grabPoint.x()) > (self.parent.width() ):
				self.move(self.parent.width()-self.width(), self.y())
			elif (self.mapToParent(pos).x() - self.grabPoint.x()) < 0:
				self.move(0, self.y())
			if (self.mapToParent(pos).y() + self.height() - self.grabPoint.y()) > (self.parent.height() ):
				self.move(self.x(), self.parent.height()-self.height())
			elif (self.mapToParent(pos).y() - self.grabPoint.y()) < 0:
				self.move(self.x(), 0)
			"""

			w = self.parent.frameGeometry().width()
			h = self.parent.frameGeometry().height()

			"""
			if self.width() > w:
				self.move( self.mapToParent(event.pos().x() - self.grabPoint.x()), self.y() )
			if self.height() > h:
				self.move( self.x(), self.mapToParent(event.pos().y() - self.grabPoint.y()))
			"""

		self.update()

	def drawToolHint(self, x, y):

		if self.data.currentTool == 1: m = self.data.circles[self.data.pencilSize-1]
		elif self.data.currentTool == 2: m = self.data.circles[self.data.eraserSize-1]

		painter = QtGui.QPainter(self)
		#painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
		pen = QtGui.QPen(QtGui.QColor(0,0,0,96))
		#pen.setStyle(Qt.DotLine)
		painter.setPen(pen)
		size = len(m)

		for i in range(size):
			for j in range(size):
				if m[i][j]:
					if j == 0 or not m[i][j-1]:
						x0 = (x-size/2+j)*self.data.zoom
						y0 = (y-size/2+i)*self.data.zoom
						y1 = (y-size/2+i+1)*self.data.zoom-1
						painter.drawLine(x0, y0, x0, y1)
					if j == size-1 or not m[i][j+1]:
						x0 = (x+size/2+(j-size)+2)*self.data.zoom-1
						y0 = (y-size/2+i)*self.data.zoom
						y1 = (y-size/2+i+1)*self.data.zoom-1
						painter.drawLine(x0, y0, x0, y1)
					if i == 0 or not m[i-1][j]:
						x0 = (x-size/2+j)*self.data.zoom
						x1 = (x-size/2+j+1)*self.data.zoom-1
						y0 = (y-size/2+i)*self.data.zoom
						painter.drawLine(x0, y0, x1, y0)
					if i == size-1  or not m[i+1][j]:
						x0 = (x+size/2+(j-size)+1)*self.data.zoom
						x1 = (x+size/2+(j-size)+2)*self.data.zoom-1
						y0 = (y+size/2+(i-size)+2)*self.data.zoom-1
						painter.drawLine(x0, y0, x1, y0)
			
	def mouseReleaseEvent(self, event):

		pos = event.pos()
		x = pos.x() / self.data.zoom # x de la imagen
		y = pos.y() / self.data.zoom # y de la imagen

		# Selección
		if self.data.currentTool == 0 and event.button() == QtCore.Qt.LeftButton:
			
			if self.selecting:
				#print "Selection made starting at (" + str(self.data.selection.origin.x()) + ", " + str(self.data.selection.origin.y()) + ") and ending at (" + str(x) + ", " + str(y) + ") (both included)"
				self.data.selection.originTopLeft = QtCore.QPoint(self.data.selection.rect.x(), self.data.selection.rect.y())
				self.data.selection.finished = True
				self.data.selection.image = self.data.image.copy(self.data.selection.rect)
				painter = QtGui.QPainter(self.data.image)
				painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
				painter.fillRect(self.data.selection.rect, self.data.bgColor)
			else:
				if self.data.selection != None and self.data.selection.finished:
					#print "Moved selection"
					pass
				else:
					#print "No selection was made"
					self.data.selection = None
			self.selecting = False

		# Lápiz
		elif self.data.currentTool == 1 and self.drawing:
			if event.button() == Qt.LeftButton or event.button() == Qt.RightButton:
				self.data.addHistoryStep()
				self.drawing = False

		# Goma
		elif self.data.currentTool == 2:
			if event.button() == Qt.LeftButton or event.button() == Qt.RightButton:
				self.data.addHistoryStep()
				self.drawing = False

		# Degradado
		if self.data.currentTool == 5 and event.button() == QtCore.Qt.LeftButton:
			
			if self.selecting:
				#print "Gradient made starting at (" + str(self.data.gradient.origin.x()) + ", " + str(self.data.gradient.origin.y()) + ") and ending at (" + str(x) + ", " + str(y) + ") (both included)"
				x1,y1 = self.data.gradient.origin.x(), self.data.gradient.origin.y()
				x2,y2 = x,y
				xm,ym = max(x1,x2),max(y1,y2)
				if xm == x2 : 
					lx = range(x1,x2+1)
				else:
					lx = range(x1,x2-1,-1)
				if ym == y2:
					ly = range(y1,y2+1)
				else:
					ly = range(y1,y2-1,-1)
				self.data.gradient.originTopLeft = QtCore.QPoint(self.data.gradient.rect.x(), self.data.gradient.rect.y())
				self.data.gradient.finished = True
				self.data.gradient.image = self.data.image.copy(self.data.gradient.rect)
				self.data.gradient.hide()
				self.data.gradient = None
				# OPERACIONES DE PINTADO AQUí ABAJO
				painter = QtGui.QPainter(self.data.image)
				painter.setCompositionMode(QtGui.QPainter.CompositionMode_Source)
				#painter.fillRect(x1,y1,x2,y2, self.data.bgColor)
				if self.data.DegState == 2:
					if self.data.DegDir == 'H':
						for i in ly:
							self.Grad2Colors( (x1,i) , (x2,i) )
					else:
						for i in lx:
							self.Grad2Colors( (i,y1) , (i,y2) )
				elif self.data.DegState == 1:
					if self.data.DegDir == 'H':
						for i in ly:
							self.GradColorAlpha( (x1,i) , (x2,i) )
					else:
						for i in lx:
							self.GradColorAlpha( (i,y1) , (i,y2) )
				self.data.addHistoryStep()
				self.com.updateCanvas.emit()

			self.selecting = False
	
	def paintEvent(self, event):
		
		#super(Canvas, self).paintEvent(event)

		painter = QtGui.QPainter(self)

		# Transparency
		if self.data.bgColor == QtGui.QColor(0,0,0,0):
			painter.fillRect(self.rect(), QtGui.QBrush(QtGui.QImage("images/transparent.png")))
		
		# Image
		painter.drawImage(self.rect(), self.data.image)

		# Selection
		if not self.selecting and self.data.selection != None and self.data.selection.finished and self.data.selection.image != None:
			rect = QtCore.QRect(self.data.selection.rect.topLeft()*self.data.zoom, self.data.selection.rect.size()*self.data.zoom)
			painter.drawImage(rect, self.data.selection.image)

		# Pixel Grid
		if self.data.grid and self.data.zoom > 3:
			r = self.data.bgColor.red()
			g = self.data.bgColor.green()
			b = self.data.bgColor.blue()
			gridColor = QtGui.QColor(255-r, 255-g, 255-b, 128)
			pen = QtGui.QPen(gridColor)
			if self.data.zoom < 9:
				pen.setStyle(Qt.SolidLine)
			else:
				pen.setStyle(Qt.DotLine)
			painter.setPen(pen)
			w = self.data.image.width()
			h = self.data.image.height()
			for i in range(w)[1:]:
				painter.drawLine(i*self.data.zoom-1, 0, i*self.data.zoom-1, h*self.data.zoom)
			for i in range(h)[1:]:
				painter.drawLine(0, i*self.data.zoom-1, w*self.data.zoom, i*self.data.zoom-1)

		# Matrix Grid
		if self.data.matrixGrid and self.data.zoom >= 3:
			painter.setPen(QtGui.QColor(127,67,167,128))
			w = self.data.image.width()
			h = self.data.image.height()
			for i in range(w)[1:]:
				if i % self.data.matrixGridWidth == 0:
					painter.drawLine(i*self.data.zoom, 0, i*self.data.zoom, h*self.data.zoom)
			for i in range(h)[1:]:
				if i % self.data.matrixGridHeight == 0:
					painter.drawLine(0, i*self.data.zoom, w*self.data.zoom, i*self.data.zoom)

		if self.data.currentTool == 1 or self.data.currentTool == 2:
			# Draw ToolHint
			xcursor = self.mapFromGlobal(QtGui.QCursor().pos()).x()/self.data.zoom
			ycursor = self.mapFromGlobal(QtGui.QCursor().pos()).y()/self.data.zoom
			self.drawToolHint(xcursor, ycursor)

	"""
	def hideToolHint(self):

		if self.toolHint != None:
			self.toolHint.hide()
			self.toolHint = None
	"""

	def zoom(self): # Cosas que hacer cuando se aplica un zoom

		if self.data.selection != None: # Calcular la nueva geometría de la selección, en caso que haya
			self.calcNewSelectionGeometry()

	def resize(self):

		super(Canvas, self).resize(QtCore.QSize(self.data.image.width()*self.data.zoom, self.data.image.height()*self.data.zoom))
	
	def drawLineTo(self, endPoint, color):

		steep = 0

		dx = abs(endPoint.x() - self.lastPoint.x())
		if (endPoint.x() - self.lastPoint.x()) > 0: sx = 1
		else: sx = -1

		dy = abs(endPoint.y() - self.lastPoint.y())
		if (endPoint.y() - self.lastPoint.y()) > 0: sy = 1
		else: sy = -1

		x = self.lastPoint.x()
		y = self.lastPoint.y()

		if dy > dx:
		    steep = 1
		    x,y = y,x
		    dx,dy = dy,dx
		    sx,sy = sy,sx
		d = (2 * dy) - dx

		for i in range(0,dx):
		    if steep: self.data.paintPoint(y, x, color)
		    else: self.data.paintPoint(x, y, color)
		    while d >= 0:
		        y = y + sy
		        d = d - (2 * dx)
		    x = x + sx
		    d = d + (2 * dy)

		self.data.paintPoint(endPoint.x(), endPoint.y(), color)

	def applySelection(self):
		if self.data.selection != None:
			#print "Applying selection"
			painter = QtGui.QPainter(self.data.image)
			painter.drawImage(self.data.selection.rect.topLeft(), self.data.selection.image)
			if self.data.selection.originTopLeft != self.data.selection.rect.topLeft():
				self.data.addHistoryStep()
			self.com.updateCanvas.emit()
			self.data.selection.hide()
			self.data.selection = None

	def cutImage(self):

		clipboard = QtGui.QApplication.clipboard()
		if self.data.selection != None: # Copiar selección
			clipboard.setImage(self.data.selection.image)
			self.data.selection.hide()
			self.data.selection = None
			self.data.addHistoryStep()
			self.com.updateCanvas.emit()
		else: # Copiar imagen entera
			clipboard.setImage(self.data.image)

	def copyImage(self):

		clipboard = QtGui.QApplication.clipboard()
		if self.data.selection != None: # Copiar selección
			clipboard.setImage(self.data.selection.image)
		else: # Copiar imagen entera
			clipboard.setImage(self.data.image)

	def pasteImage(self):

		image = QtGui.QApplication.clipboard().image()
		self.data.currentTool = 0
		if self.data.selection != None:
			self.applySelection()
		self.data.selection = Selection(QtCore.QPoint(0,0), self.data, self)
		self.data.selection.setGeometry(0, 0, image.width(), image.height())
		self.data.selection.show()
		self.data.selection.finished = True
		self.data.selection.image = image

	def clearImage(self):

		if self.data.selection != None:
			self.data.selection.hide()
			self.data.selection = None
			self.data.addHistoryStep()
			self.com.updateCanvas.emit()

	def resizeToNewImage(self):

		if self.data.selection != None:
			self.data.selection.hide()
			self.data.selection = None
		self.resize()
		self.setPixmap(QtGui.QPixmap.fromImage(self.data.image))
		self.com.updateCanvas.emit()

	def fillImage(self, begin, paint, current, imagen):

		if paint.rgb() == current :
			#print "pass activated"
			pass
		else:
			queue = [begin]
			for x,y in queue:
				if imagen.pixel(x,y) == current:
					cond = True
					nodes = [(x,y)]
					xt = x-1
					while xt>=0 and cond: 
						cond = imagen.pixel(xt,y)==current
						if cond:
							nodes.append( (xt,y) ) 
							xt = xt-1

					cond = True
					xt = x+1
					while xt<imagen.width() and cond : 
						cond = imagen.pixel(xt,y)==current
						if cond:
							nodes.append( (xt,y) ) 
							xt = xt+1

					for xp,yp in nodes:
						imagen.setPixel(xp,yp,paint.rgb())
						if yp<imagen.width()-1:
							if imagen.pixel(xp,yp+1) == current: 
								queue.append( (xp,yp+1) )
						if yp>0:
							if imagen.pixel(xp,yp-1) == current:
								queue.append( (xp,yp-1) )

	def Grad2Colors(self, pi, pf):

		alpha = self.data.DegAlpha

		if pf[0] == pi[0]:

			Var_y = pf[1] - pi[1]
			if Var_y > 0 :
				dy = +1
			elif Var_y < 0 :
				dy = -1
			else:
				return 0

			color1 = self.data.primaryColor.getRgb()
			color2 = self.data.secondaryColor.getRgb()
			#print color1,color2

			Var_r = color2[0] - color1[0]
			dr = float(Var_r)/abs(Var_y)
			Var_g = color2[1] - color1[1]
			dg = float(Var_g)/abs(Var_y)
			Var_b = color2[2] - color1[2]
			db = float(Var_b)/abs(Var_y)
			#print dr, dg, db

			for i in range(0,abs(Var_y)+1):
				R = color1[0] + i*dr
				G = color1[1] + i*dg
				B = color1[2] + i*db
				R = int( round(R) )
				G = int( round(G) )
				B = int( round(B) )
				#print R,G,B

				tmp_c = QtGui.QColor(R,G,B,alpha)
				#print "changed color"
				self.data.image.setPixel(pi[0],pi[1]+i*dy,tmp_c.rgba())

			return 0

		elif pf[1] == pi[1]:

			Var_x = pf[0] - pi[0]
			if Var_x > 0 :
				dx = +1
			elif Var_x < 0 :
				dx = -1
			else:
				return 0

			color1 = self.data.primaryColor.getRgb()
			color2 = self.data.secondaryColor.getRgb()
			#print color1,color2

			Var_r = color2[0] - color1[0]
			dr = float(Var_r)/abs(Var_x)
			Var_g = color2[1] - color1[1]
			dg = float(Var_g)/abs(Var_x)
			Var_b = color2[2] - color1[2]
			db = float(Var_b)/abs(Var_x)
			#print dr, dg, db

			for i in range(0,abs(Var_x)+1):
				R = color1[0] + i*dr
				G = color1[1] + i*dg
				B = color1[2] + i*db
				R = int( round(R) )
				G = int( round(G) )
				B = int( round(B) )
				#print R,G,B

				tmp_c = QtGui.QColor(R,G,B,alpha)
				self.data.image.setPixel(pi[0]+i*dx,pi[1],tmp_c.rgba())
			return 0

		else:
			return 1

	def GradColorAlpha(self, pi, pf):

		alpha = self.data.DegAlpha

		if pf[0] == pi[0]:

			Var_y = pf[1] - pi[1]
			if Var_y > 0 :
				dy = +1
			elif Var_y < 0 :
				dy = -1
			else:
				return 0

			color = self.data.primaryColor
			da = 255/abs(Var_y)

			for i in range(0,abs(Var_y)+1):

				color.setAlpha(255-da*i)
				#print "changed color"
				self.data.image.setPixel(pi[0],pi[1]+i*dy,color.rgba())

			return 0

		elif pf[1] == pi[1]:

			Var_x = pf[0] - pi[0]
			if Var_x > 0 :
				dx = +1
			elif Var_x < 0 :
				dx = -1
			else:
				return 0

			color = self.data.primaryColor
			da = 255/abs(Var_x)

			for i in range(0,abs(Var_x)+1):

				color.setAlpha(255-da*i)
				self.data.image.setPixel(pi[0]+i*dx,pi[1],color.rgba())

			return 0

		else:
			return 1

	def resizeSelection(self, selection, xevent, yevent):

		# En la imagen
		x = xevent / self.data.zoom
		y = yevent / self.data.zoom

		if x >= selection.origin.x() and y >= selection.origin.y():
			selection.setGeometry( selection.origin.x(), selection.origin.y(), x - selection.origin.x() + 1, y - selection.origin.y() + 1 )
		elif x < selection.origin.x() and y >= selection.origin.y():
			selection.setGeometry( x, selection.origin.y(), selection.origin.x() - x + 1, y - selection.origin.y() + 1 )
		elif x < selection.origin.x() and y < selection.origin.y():
			selection.setGeometry( x, y, selection.origin.x() - x + 1, selection.origin.y() - y + 1 )
		elif x >= selection.origin.x() and y < selection.origin.y():
			selection.setGeometry( selection.origin.x(), y, x - selection.origin.x() + 1, selection.origin.y() - y + 1 )
		else:
			selection.setGeometry( xorig, yorig, 1, 1 )

		selection.show()

	def calcNewSelectionGeometry(self):

		if self.data.selection != None and self.data.selection.finished:
			self.data.selection.setGeometry(self.data.selection.rect.x(), self.data.selection.rect.y(), self.data.selection.rect.width(), self.data.selection.rect.height())

	def moveSelection(self, xevent, yevent):

		# En la imagen
		x = xevent / self.data.zoom
		y = yevent / self.data.zoom

		xx = self.data.selectionGrabPoint.x()
		yy = self.data.selectionGrabPoint.y()

		self.data.selection.setGeometry(x - xx, y - yy, self.data.selection.rect.width(), self.data.selection.rect.height())