#!/usr/bin/env python
#coding: utf-8

from PyQt4 import QtCore

class Communication(QtCore.QObject):
	"""
	La clase Communication hace de puente entre diferentes
	instancias de todo el programa.
	"""

	dadesActualitzada = QtCore.pyqtSignal()
	zoomIn = QtCore.pyqtSignal()
	zoomOut = QtCore.pyqtSignal()