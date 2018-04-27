'''
Created on Apr 26, 2018

@author: zhenfengzhao
'''
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QProgressBar, QLineEdit, QLabel
from PyQt5.QtGui import QPainter, QFont, QColor, QPen, QIntValidator
from PyQt5.QtCore import Qt

class CMeter(QWidget):
    def __init__(self, HVObject):        
        super(CMeter, self).__init__()
        self.__Obj = HVObject
        self.__name = 'meter'
        self.__uint = 'V'
        self.__initalLayout()            
        
    def __initalLayout(self):        
        label = QLabel(self.__name+' ('+self.__uint+')')
        label.setFont(QFont("Calibri",24, QFont.Bold))
        label.setStyleSheet("color: rgb(15,34,139);")
        label.setAlignment(Qt.AlignHCenter)
        
        editBox = QLineEdit('18.88')
        editBox.setFont(QFont("Arial",32))
        editBox.setStyleSheet("color: rgb(63,72,204);background-color: rgb(242,242,242);")
        editBox.setMaximumWidth(240)
        editBox.setAlignment(Qt.AlignRight)
        editBox.setReadOnly(True)
        
        ProgressBar = QProgressBar();
        ProgressBar.setOrientation(Qt.Vertical)
        ProgressBar.setMinimumSize(60,360)
        ProgressBar.setAlignment(Qt.AlignHCenter)
        #ProgressBar.setTextVisible(True)
        
        
        vbox=QVBoxLayout()
        vbox.addWidget(label, alignment=Qt.AlignCenter)
        vbox.addWidget(ProgressBar, alignment=Qt.AlignCenter)
        vbox.addWidget(editBox, alignment=Qt.AlignCenter)
        self.setLayout(vbox)
        
    def setValue(self):
        pass
        
        