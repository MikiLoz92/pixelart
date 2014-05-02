#!/usr/bin/env python
#coding: utf-8

import ConfigParser

from PyQt4 import QtGui, QtCore
from translation import *

## Model / Modelo
class Data:
	"""
	La clase Data contiene todos los datos, parámetros y configuraciones
	de la aplicación. Por ejemplo, contiene la lista de píxeles pintados en
	la imagen con su correspondiente color. También guarda las variables de
	la anchura del làpiz, los colores en la paleta, el color seleccionado
	actualmente, la altura y anchura de la imagen, etc.
	"""

	color = QtCore.Qt.red
	pencilSize = 1
	brushSize = 3
	brushStyle = 0
	currentTool = 1
	zoom = 1
	defaultFileName = ""
	colorPicker = False

	color_deg_1 = QtCore.Qt.white
	color_deg_2 = QtCore.Qt.black

	def __init__(self, com):

		self.com = com

		# Cargamos TODA la configuración
		self.loadDefaults()

		# Creamos la QImage
		self.newImage(32,32)

		# Creamos los cursores
		self.pencilCur = QtGui.QCursor(QtGui.QPixmap("images/pencilCur.png"), 0, 23)
		self.colorPickerCur = QtGui.QCursor(QtGui.QPixmap("images/dropperCur.png"), 0, 23)

	def loadImage(self, fileName):

		self.defaultFileName = fileName
		self.image = QtGui.QImage(fileName).convertToFormat(QtGui.QImage.Format_ARGB32)
		self.zoom = 1
		self.com.newImage.emit()

	def newImage(self, w, h):

		self.defaultFileName = ""
		self.image = QtGui.QImage(w, h, QtGui.QImage.Format_ARGB32)
		self.image.fill(QtGui.qRgb(255, 255, 255))
		self.zoom = 1
		self.history = [QtGui.QImage(self.image)]
		self.posHistory = 0
		self.com.newImage.emit()

	def changeColor(self, c):

		self.color = c
		self.com.updateColor.emit()

	def getText(self, sect, ident): # Get some text in the current language

		return self.tdatabase.getText(self.lang, sect, ident).decode("utf-8")

	def getTextInLang(self, lang, sect, ident): # Get some text in a specific language

		return self.tdatabase.getText(lang, sect, ident).decode("utf-8")

	def setDefault(self, sect, ident, value):

		try:
			self.cp.set(sect, ident, value)
			f = open("defaults.cfg", "w")
			self.cp.write(f)
			f.close()
		except ConfigParser.NoSectionError:
			print "Trying to set \"" + ident + "\" to \"" + value + "\" on section \"" + sect + "\", but given section does not exist."

	def getDefault(self, sect, ident):

		return self.cp.get(sect, ident)

	def getBoolDefault(self, sect, ident):

		try:
			return self.cp.getboolean(sect, ident)
		except ValueError:
			print "Trying to get boolean value from option \"" + ident + "\" on section \"" + sect + "\", but given option value is not boolean."

	def getIntDefault(self, sect, ident):

		try:
			return self.cp.getint(sect, ident)
		except ValueError:
			print "Trying to get integer value from option \"" + ident + "\" on section \"" + sect + "\", but given option value is not an integer."

	def getFloatDefault(self, sect, ident):

		try:
			return self.cp.getfloat(sect, ident)
		except ValueError:
			print "Trying to get float value from option \"" + ident + "\" on section \"" + sect + "\", but given option value is not a floating point number."

	def loadDefaults(self):

		self.cp = ConfigParser.ConfigParser()
		self.cp.read("defaults.cfg")

		self.loadDefaultsLanguage()
		self.loadDefaultsGrid()
		self.loadDefaultsColor()

	def loadDefaultsLanguage(self):

		self.tdatabase = TDatabase()
		lang = self.getDefault("language", "lang")
		if lang in self.tdatabase.langAvailable:
			self.lang = lang
		else:
			self.lang = "en"

	def loadDefaultsGrid(self):

		self.grid = self.getBoolDefault("grid", "grid")
		self.matrixGrid = self.getBoolDefault("grid", "matrix_grid")
		self.matrixGridWidth = self.getIntDefault("grid", "matrix_grid_width")
		self.matrixGridHeight = self.getIntDefault("grid", "matrix_grid_height")

	def loadDefaultsColor(self):

		self.primaryColor = QtGui.QColor(self.getIntDefault("color", "primary_color"))
		self.secondaryColor = QtGui.QColor(self.getIntDefault("color", "secondary_color"))