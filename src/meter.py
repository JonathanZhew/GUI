'''
Created on Apr 26, 2018

@author: zhenfengzhao
'''
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QProgressBar, QLineEdit, QLabel
from PyQt5.QtGui import QPainter, QFont, QColor, QPen, QIntValidator
from PyQt5.QtCore import Qt, QSize
from PyQt5.Qt import QPoint


class CAxis():
    def __init__(self, value, text, color):
        self.value = value
        self.text = text
        self.color = color

class CScale(QWidget):
    def __init__(self, width=5, height=30):
        super().__init__()
        self.__width = width
        self.__height = height
        self.__maxvalue = 100
        self.__minvalue = 0
        self.__value = 0
        self.__step = 10
        self.__axis = {}
        
        self.ValidRange = QPoint(20,50)

        self.initUI()
        
        self.setAxis('alarm', 50, str(50), QColor(255, 255, 255))

        
    def initUI(self):
        self.setMinimumSize(10, 30)

    def setValue(self, value):
        self.value = value

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        cw= 15 #width of scale
        font = QFont("Serif", 8, QFont.Light)
        qp.setFont(font)
        
        size = self.size()
        width = size.width()
        height = size.height()
                
        qp.setPen(QColor(255, 255, 255))
        qp.setBrush(QColor(255, 168, 168))
        qp.drawRect(0, 0, cw, height)
        
        qp.setPen(QColor(255, 255, 255))
        qp.setBrush(QColor(168,255,168))
        h = height*(self.ValidRange.y() - self.ValidRange.x())/(self.__maxvalue - self.__minvalue)
        y = (height - height*(self.ValidRange.y() - self.__minvalue)/(self.__maxvalue- self.__minvalue))
        qp.drawRect(0, y, cw, h)
        
        qp.setPen(QColor(100,100,100))
        
        metrics = qp.fontMetrics()
            
        qp.drawLine(0, 0, 0, height)
        
        cell = round(height/self.__step)
        qp.drawText(cw, 0, str(self.__maxvalue))
        
        qp.drawLine(0, height-1, cw, height-1)
        qp.drawText(cw, height, str(self.__minvalue))
        
        qp.drawLine(0, 0, cw, 0)
        ma= metrics.ascent()
        qp.drawText(cw, ma-3, str(self.__maxvalue))
        
        mw= metrics.width(str(self.__maxvalue))
        self.setMinimumWidth(mw+cw)
        
        for stair in range(cell, height, cell):
            y = height - stair
            qp.drawLine(0, y, cw, y)
            #metrics = qp.fontMetrics()
            #fw = metrics.width(str(self.num[j]))
            #qp.drawText(i-fw/2, h/2, str(self.num[j]))
            
        for key in self.__axis:
            axis = self.__axis[key]
            y = (height - height*(axis.value - self.__minvalue)/(self.__maxvalue- self.__minvalue))
            qp.drawText(cw, y+ma/2, str(axis.text))
    
    def setAxis(self, key, value, text, color):        
        self.__axis[key] = CAxis(value, text, color)
                
        

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
        
        progressBar = QProgressBar();
        progressBar.setOrientation(Qt.Vertical)
        progressBar.setMinimumSize(50,360)
        progressBar.setValue(60)
        progressBar.setAlignment(Qt.AlignHCenter)
        #ProgressBar.setTextVisible(True)        
        scale = CScale(60,360)
        hbox=QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(progressBar)
        hbox.addWidget(scale)   
        hbox.addStretch(1)
        
        vbox=QVBoxLayout()
        vbox.addWidget(label, alignment=Qt.AlignCenter)
        vbox.addLayout(hbox)
        vbox.addWidget(editBox, alignment=Qt.AlignCenter)
        self.setLayout(vbox)
        
    def setValue(self):
        pass
        
        
        
        