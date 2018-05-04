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
    def __init__(self, RtRead):
        super().__init__()
        self.__maxvalue = RtRead['max']
        self.__minvalue = RtRead['min']
        self.__value = 0
        self.__axis = {}
        
        self.ValidRange = RtRead['valid']
        self.setAxis('min', self.ValidRange.x(), str(self.ValidRange.x()), QColor(255, 255, 255))
        self.setAxis('max', self.ValidRange.y(), str(self.ValidRange.y()), QColor(255, 255, 255))
        self.initUI()  
        
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
        qp.drawText(cw, 0, str(self.__maxvalue))
        
        qp.drawLine(0, height-1, cw, height-1)
        qp.drawText(cw, height, str(self.__minvalue))
        
        qp.drawLine(0, 0, cw, 0)
        ma= metrics.ascent()
        qp.drawText(cw, ma-3, str(self.__maxvalue))
        
        mw= metrics.width(str(self.__maxvalue))
        self.setMinimumWidth(mw+cw)
        
        for i in range(0, 10):
            y = height*i/10
            #print(y)
            qp.drawLine(0, y, cw*2/3, y)
            #metrics = qp.fontMetrics()
            #fw = metrics.width(str(self.num[j]))
            #qp.drawText(i-fw/2, h/2, str(self.num[j]))
            
        for key in self.__axis:
            axis = self.__axis[key]
            y = (height - (height*(axis.value - self.__minvalue)/(self.__maxvalue - self.__minvalue)))
            #print(axis.value)
            qp.drawText(cw, y+ma/2, str(axis.text))
    
    def setAxis(self, key, value, text, color):        
        self.__axis[key] = CAxis(value, text, color)
                
        

class QMeter(QWidget):
    def __init__(self, RtRead):        
        super(QMeter, self).__init__()
        self.__Obj = RtRead
        self.__name = RtRead['name']
        self.__uint = RtRead['uint']
        self.__value = 0
        self.__initalLayout()            
        
    def __initalLayout(self):        
        label = QLabel(self.__name+' ('+self.__uint+')')
        label.setFont(QFont("Calibri",24, QFont.Bold))
        label.setStyleSheet("color: rgb(15,34,139);")
        label.setAlignment(Qt.AlignHCenter)
        
        editBox = QLineEdit()
        editBox.setFont(QFont("Arial",32))
        editBox.setStyleSheet("color: rgb(63,72,204);background-color: rgb(242,242,242);")
        editBox.setMaximumWidth(240)
        editBox.setAlignment(Qt.AlignRight)
        editBox.setReadOnly(True)
        
        progressBar = QProgressBar();
        progressBar.setOrientation(Qt.Vertical)
        progressBar.setMinimumSize(50,360)
        progressBar.setValue(self.__value)
        progressBar.setAlignment(Qt.AlignHCenter)
        #ProgressBar.setTextVisible(True)        
        scale = CScale(self.__Obj)
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
        
    def setValue(self, value):
        self.__value = value
        
        
        
        