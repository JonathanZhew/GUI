'''
Created on Apr 26, 2018

@author: zhenfengzhao
'''
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QProgressBar, QLineEdit, QLabel
from PyQt5.QtGui import QPainter, QFont, QColor, QPen
from PyQt5.QtCore import Qt
import re

class CAxis():
    def __init__(self, value, text, color):
        self.value = value
        self.text = text
        self.color = color

class CScale(QWidget):
    def __init__(self, RtRead, parent=None):
        super().__init__()
        self.parent = parent
        self.__maxvalue = RtRead['max']
        self.__minvalue = RtRead['min']
        self.__step = RtRead['step']
        self.__value = 0
        self.CustomerTicks = {}

        self.ValidRange = RtRead['valid']
        #self.setCustomerTicks('Hmin', self.ValidRange.x(), str(self.ValidRange.x()), QColor(0, 0, 255))
        #self.setCustomerTicks('HHHmax', self.ValidRange.y(), str(self.ValidRange.y()), QColor(255, 0, 0))
        self.setMinimumSize(10, 30)
        self.initAxisText()

    def initAxisText(self):
        self.axisText = [] 
        self.axisText.append(str(self.__minvalue))
        cnt = int((self.__maxvalue-self.__minvalue)/self.__step)
        for num in range(1, cnt):
            self.axisText.append(str(self.__step*num+self.__minvalue))
        self.axisText.append(str(self.__maxvalue))
        #print(self.axisText)
        
    def SetAxisText(self, ticks):           
        for i, tick in enumerate(ticks):
            self.axisText[i] = tick

    def setValue(self, value):
        self.value = value

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.drawWidget(qp)
        qp.end()

    def drawWidget(self, qp):
        #print(self.parent.size())
        self.setMinimumWidth(self.parent.size().width()/2)
        
        cw= 15 #width of scale
        font = QFont("Serif", 8, QFont.Light)
        qp.setFont(font)
        
        size = self.size()
        #width = size.width()
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
        qp.drawLine(0, 0, cw, 0) 
        qp.drawLine(0, height-1, cw, height-1)       
        
        ma= metrics.ascent()       
        cnt = len(self.axisText) - 1
        for i, text in enumerate(self.axisText):
            if i == 0:
                qp.drawText(cw, height, text)
            elif i == cnt:
                qp.drawText(cw, ma-3, text)
            else:
                y = height*(cnt-i)/cnt
                qp.drawLine(0, y, cw*2/3, y)
                qp.drawText(cw, y+ma/2 , text)

        font = QFont("Serif", 12, QFont.Light)
        qp.setFont(font)
        metrics = qp.fontMetrics()   
        ma= metrics.ascent()  
        for name, axis in self.CustomerTicks.items():
            qp.setPen(axis.color)
            y = (height - (height*(axis.value - self.__minvalue)/(self.__maxvalue - self.__minvalue)))
            #print(axis.value)
            #str1 = "{0:s} {1:s}".format(name, axis.text)
            qp.drawText(2*cw+5, y-ma, name)
            qp.drawText(2*cw+5, y, axis.text)
            pen = QPen(QColor(100,100,100), 2, Qt.SolidLine)
            qp.setPen(pen)
            qp.drawLine(0, y, 2*cw, y-ma)
            qp.drawLine(2*cw, y, 2*cw, y-2*ma)       
        

class QMeter(QWidget):
    def __init__(self, RtRead):        
        super(QMeter, self).__init__()
        self.__Obj = RtRead
        self.__name = RtRead['name']
        self.__uint = RtRead['uint']        
        self.initLayout()  
   
        
    def initLayout(self):        
        label = QLabel(self.__name+' ('+self.__uint+')')
        label.setFont(QFont("Calibri",24, QFont.Bold))
        label.setStyleSheet("color: rgb(15,34,139);")
        label.setAlignment(Qt.AlignHCenter)
        
        self.editBox = QLineEdit()
        self.editBox.setFont(QFont("Arial",32))
        self.editBox.setStyleSheet("color: rgb(63,72,204);background-color: rgb(242,242,242);")
        self.editBox.setMaximumWidth(240)
        self.editBox.setAlignment(Qt.AlignRight)
        self.editBox.setReadOnly(True)
        
        self.progressBar = QProgressBar();
        self.progressBar.setOrientation(Qt.Vertical)
        self.progressBar.setMinimumSize(50,360)
        self.progressBar.setAlignment(Qt.AlignHCenter)
        #ProgressBar.setTextVisible(True)        
        self.scale = CScale(self.__Obj, self)
        hbox=QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.progressBar)
        hbox.addWidget(self.scale)   
        #hbox.addStretch(1)
        
        vbox=QVBoxLayout()
        vbox.addWidget(label, alignment=Qt.AlignCenter)
        vbox.addLayout(hbox)
        vbox.addWidget(self.editBox, alignment=Qt.AlignCenter)
        self.setLayout(vbox)
        
    def setValue(self, text, percent):
        self.editBox.setText(text)
        self.progressBar.setValue(percent) 

    def setTicks(self, ticks):        
        self.scale.SetAxisText(ticks)
     
    def setSpecialTick(self, name, value, text, color):        
        self.scale.CustomerTicks[name] = CAxis(value, text, color)   
        
def format_float(value):
    """Modified form of the 'g' format specifier."""
    string = "{:g}".format(value).replace("e+", "e")
    string = re.sub("e(-?)0*(\d+)", r"e\1\2", string)
    return string        
        
        