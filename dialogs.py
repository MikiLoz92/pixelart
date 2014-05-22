#!/usr/bin/env python
#coding: utf-8

import os

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import Qt

## Vista/View
class NewFileDialog(QtGui.QDialog):
	"""
	La ventanita que se abre cuando queremos crear un archivo nuevo.
	"""

	def __init__(self, data, Parent=None):

		super(NewFileDialog,self).__init__(Parent)
		self.data = data
		self.parent = Parent

		dimensionGroup = QtGui.QGroupBox(self.parent.data.getText("dialog_new_image", "dimension"))
		dimensionLayout = QtGui.QVBoxLayout()
		self.width = QtGui.QSpinBox(dimensionGroup)
		self.width.setValue(32)
		self.width.setMinimum(1)
		self.width.setMaximum(1024)
		self.height = QtGui.QSpinBox(dimensionGroup)
		self.height.setValue(32)
		self.height.setMinimum(1)
		self.height.setMaximum(1024)
		dimensionLayout.addWidget(self.width)
		dimensionLayout.addWidget(self.height)
		dimensionGroup.setLayout(dimensionLayout)

		backgroundGroup = QtGui.QGroupBox(self.parent.data.getText("dialog_new_image", "background"))
		backgroundLayout = QtGui.QVBoxLayout()
		self.r1 = QtGui.QRadioButton(self.parent.data.getText("dialog_new_image", "transparent"))
		self.r1.setChecked(True)
		self.r2 = QtGui.QRadioButton(self.parent.data.getText("dialog_new_image", "color"))
		self.cButton = QtGui.QPushButton()
		self.cButton.clicked.connect(self.getColor)
		self.cButton.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
		self.color = QtGui.QColor(255,255,255)
		self.cButton.setStyleSheet("background-color: " + self.color.name() +";")
		self.cButton.setText(self.color.name())
		colorLayout = QtGui.QHBoxLayout()
		colorLayout.addWidget(self.r2)
		colorLayout.addWidget(self.cButton)
		backgroundLayout.addWidget(self.r1)
		#backgroundLayout.addWidget(r2)
		backgroundLayout.addLayout(colorLayout)
		backgroundGroup.setLayout(backgroundLayout)

		buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
		#buttonBox.accepted.connect(self.accept)
		buttonBox.accepted.connect(self.accept)
		buttonBox.rejected.connect(self.reject)
		mainLayout = QtGui.QVBoxLayout()
		mainLayout.addWidget(dimensionGroup)
		mainLayout.addWidget(backgroundGroup)
		mainLayout.addWidget(buttonBox)
		self.setLayout(mainLayout)
		self.setWindowTitle(self.parent.data.getText("dialog_new_image", "title"))
		self.initUI()

	def initUI(self):

		self.show()

	def getColor(self):

		self.color = QtGui.QColorDialog.getColor()
		if self.color.isValid(): 
			self.r2.setChecked(True)
			self.cButton.setStyleSheet("background-color: " + self.color.name() +";")
			self.cButton.setText(self.color.name())

	def accept(self):

		if self.r1.isChecked():
			self.data.newImage(self.width.value(), self.height.value(), QtGui.QColor(0,0,0,0))
		else:
			self.data.newImage(self.width.value(), self.height.value(), self.color)
		super(NewFileDialog, self).accept()


class ResizeImageDialog (QtGui.QDialog):

	def __init__(self, Parent=None):

		super(ResizeImageDialog, self).__init__(Parent)

		self.parent = Parent

		dimensionGroup = QtGui.QGroupBox(self.parent.data.getText("dialog_resize", "dimension"))
		dimensionLayout = QtGui.QVBoxLayout()

		self.width = QtGui.QSpinBox(dimensionGroup)
		self.width.setMinimum(1)
		self.width.setMaximum(1024)
		self.width.setValue(Parent.data.image.width())
		self.height = QtGui.QSpinBox(dimensionGroup)
		self.height.setMinimum(1)
		self.height.setMaximum(1024)
		self.height.setValue(Parent.data.image.height())

		dimensionLayout.addWidget(self.width)
		dimensionLayout.addWidget(self.height)
		dimensionGroup.setLayout(dimensionLayout)
		
		buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
		buttonBox.accepted.connect(self.accept)
		buttonBox.rejected.connect(self.reject)

		mainLayout = QtGui.QVBoxLayout()
		mainLayout.addWidget(dimensionGroup)
		mainLayout.addWidget(buttonBox)

		self.setLayout(mainLayout)
		self.setWindowTitle(self.parent.data.getText("dialog_resize", "title"))
		self.show()

	def accept(self):
	
		self.parent.resizeImage(self.width.value(), self.height.value())
		super(ResizeImageDialog,self).accept()


class ResizeCanvasDialog (QtGui.QDialog):

	def __init__(self, Parent=None):

		super(ResizeCanvasDialog, self).__init__(Parent)

		self.parent = Parent

		dimensionGroup = QtGui.QGroupBox(self.parent.data.getText("dialog_resize_canvas", "dimension"))
		dimensionLayout = QtGui.QVBoxLayout()

		self.width = QtGui.QSpinBox(dimensionGroup)
		self.width.setMinimum(1)
		self.width.setMaximum(1024)
		self.width.setValue(Parent.data.image.width())
		self.height = QtGui.QSpinBox(dimensionGroup)
		self.height.setMinimum(1)
		self.height.setMaximum(1024)
		self.height.setValue(Parent.data.image.height())

		dimensionLayout.addWidget(self.width)
		dimensionLayout.addWidget(self.height)
		dimensionGroup.setLayout(dimensionLayout)
		
		buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
		buttonBox.accepted.connect(self.accept)
		buttonBox.rejected.connect(self.reject)

		mainLayout = QtGui.QVBoxLayout()
		mainLayout.addWidget(dimensionGroup)
		mainLayout.addWidget(buttonBox)

		self.setLayout(mainLayout)
		self.setWindowTitle(self.parent.data.getText("dialog_resize_canvas", "title"))
		self.show()

	def accept(self):
	
		self.parent.data.resizeCanvas(self.width.value(), self.height.value())
		super(ResizeCanvasDialog,self).accept()


class Preferences (QtGui.QDialog):

	def  __init__(self, data, com, Parent=None):

		super(Preferences, self).__init__(Parent)
		self.data = data
		self.com = com
		self.parent = Parent

		# El QStackedWidget es un tipo de widget muy útil que tiene diferentes "páginas" y podemos ir cambiando entre ellas
		# con sólo llamar a un método. En nuestro caso, conectamos el signal que emite el QListWidget al cambiar de sección
		# con el método self.changeCurrentView, que cambia la página del QStackedWidget.

		self.view = QtGui.QStackedWidget()
		self.view.addWidget(self.createLanguageView())
		self.view.addWidget(self.createUICustomizationView())
		self.view.addWidget(self.createMatrixGridView())

		self.preferences = QtGui.QListWidget()
		self.preferences.addItem(self.data.getText("dialog_preferences", "item_language"))
		self.preferences.addItem(self.data.getText("dialog_preferences", "item_theme"))
		self.preferences.addItem(self.data.getText("dialog_preferences", "item_matrix_grid"))
		self.preferences.setCurrentRow(0)
		self.preferences.currentItemChanged.connect(self.changeCurrentView)
		self.preferences.setFixedWidth(self.preferences.sizeHintForColumn(0) + 24)
		#self.view.setFixedWidth(200)

		self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
		self.buttonBox.accepted.connect(self.accept)
		self.buttonBox.rejected.connect(self.reject)

		self.hbox = QtGui.QHBoxLayout()
		self.hbox.addWidget(self.preferences)
		self.hbox.addWidget(self.view)

		self.vbox = QtGui.QVBoxLayout()
		self.vbox.addLayout(self.hbox)
		self.vbox.addWidget(self.buttonBox)

		self.setLayout(self.vbox)
		self.setWindowTitle(self.data.getText("dialog_preferences", "title"))
		self.adjustSize()
		self.show()

	def changeCurrentView(self):

		self.view.setCurrentIndex(self.preferences.currentRow())

	def createLanguageView(self):

		# Widget de ejemplo

		g = QtGui.QGroupBox(self.data.getText("dialog_preferences", "item_language_language"))

		w = QtGui.QWidget()

		vbox = QtGui.QVBoxLayout()

		self.language = QtGui.QComboBox()
		self.langCodes = []

		j = 0
		for i in self.data.tdatabase.d.keys():
			self.language.addItem(self.data.tdatabase.d[i].name)
			langCode = self.data.tdatabase.d[i].code
			self.langCodes.append(langCode)
			if self.data.lang == langCode:
				self.language.setCurrentIndex(j)
			j += 1

		vbox.addWidget(self.language)
		vbox.setStretch(1,1)
		vbox.setAlignment(Qt.AlignTop)

		w.setLayout(vbox)

		g.setLayout(vbox)

		return g

	def createUICustomizationView(self):

		g = QtGui.QGroupBox(self.data.getText("dialog_preferences", "item_theme"))
		w = QtGui.QWidget()
		vbox = QtGui.QVBoxLayout()
		hbox = QtGui.QHBoxLayout()

		self.theme = QtGui.QComboBox()

		j = 0
		self.themeDirs = [d for d in os.listdir("themes") if os.path.isdir(os.path.join("themes", d))]
		for i in self.themeDirs:
			self.theme.addItem(i)
			if self.data.theme == i:
				self.theme.setCurrentIndex(j)
			j += 1
		print self.themeDirs
		self.theme.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
		#self.theme.setFixedWidth(self.theme.sizeHint().width())

		hbox.addWidget(QtGui.QLabel(self.data.getText("dialog_preferences", "item_theme_theme")))
		hbox.addWidget(self.theme)
		hbox.setAlignment(Qt.AlignLeft)
		vbox.addLayout(hbox)

		vbox.setStretch(1,1)
		vbox.setAlignment(Qt.AlignTop)

		w.setLayout(vbox)
		g.setLayout(vbox)

		return g

	def createMatrixGridView(self):

		g = QtGui.QGroupBox(self.data.getText("dialog_preferences", "item_matrix_grid_dimension"))

		vbox = QtGui.QVBoxLayout()
		
		self.matrixGridWidth = QtGui.QSpinBox()
		self.matrixGridWidth.setMinimum(1)
		self.matrixGridWidth.setMaximum(1024)
		self.matrixGridWidth.setValue(self.data.matrixGridWidth)
		self.matrixGridHeight = QtGui.QSpinBox()
		self.matrixGridHeight.setMinimum(1)
		self.matrixGridHeight.setMaximum(1024)
		self.matrixGridHeight.setValue(self.data.matrixGridHeight)

		vbox.addWidget(self.matrixGridWidth)
		vbox.addWidget(self.matrixGridHeight)
		vbox.setStretch(1,1)
		vbox.setAlignment(Qt.AlignTop)

		g.setLayout(vbox)

		return g

	def accept(self):

		if self.langCodes[self.language.currentIndex()] != self.data.lang:
			QtGui.QMessageBox.information(self, self.data.getText("dialog_preferences", "item_language_changed_title"), self.data.getText("dialog_preferences", "item_language_changed_message"))
		self.data.setDefault("language", "lang", self.langCodes[self.language.currentIndex()])

		self.data.matrixGridWidth = self.matrixGridWidth.value()
		self.data.setDefault("grid", "matrix_grid_width", self.data.matrixGridWidth)
		self.data.matrixGridHeight = self.matrixGridHeight.value()
		self.data.setDefault("grid", "matrix_grid_height", self.data.matrixGridHeight)

		if self.data.getDefault("theme", "theme") != self.themeDirs[self.theme.currentIndex()]:
			QtGui.QMessageBox.information(self, self.data.getText("dialog_preferences", "item_theme_changed_title"), self.data.getText("dialog_preferences", "item_theme_changed_message"))
		self.data.setDefault("theme", "theme", self.themeDirs[self.theme.currentIndex()])

		self.com.updateCanvas.emit()
		super(Preferences, self).accept()