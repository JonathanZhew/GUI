'''
Created on Apr 25, 2018

@author: zhenfengzhao
'''
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox, QSlider, QLabel,\
    QDoubleSpinBox
from QMeter import QMeter
from PyQt5.Qt import QLineEdit
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPainter, QFont, QColor, QPen, QIntValidator
from QSliderButton import QSliderButton
from ledwidget import LedWidget

class ControlPanel(QWidget):
    def __init__(self, Messenger, RtReads):        
        super(ControlPanel, self).__init__()
        self.__comm = Messenger
        g1 = self.meterGroupBox(RtReads)     
        g2 = self.OperaterGroupBox()   
        
        Layout = QVBoxLayout()
        Layout.addWidget(g1) 
        Layout.addWidget(g2) 
        #vbox.addStretch(1)
        self.setLayout(Layout)
    
    def meterGroupBox(self, RtReads):       
        gridBox = QGridLayout()
        self.meters = {}
        self.manual = {}
        for i, name in enumerate(RtReads.keys()):
            self.meters[name] = QMeter(RtReads.getRowbyName(name))
            gridBox.addWidget(self.meters[name], 0, i) 
            Enable = RtReads.getItems(name, 'wr')
            if Enable:
                SetBox = QDoubleSpinBox()
                SetBox.setFont(QFont("Arial",28))
                SetBox.setStyleSheet("color: rgb(200,200,200);background-color: rgb(242,242,242);")
                SetBox.setMinimumWidth(240)
                SetBox.setAlignment(Qt.AlignRight)
                SetBox.setVisible(False)
                #SetBox.setReadOnly(True)
                self.manual[name] = SetBox
                gridBox.addWidget(SetBox, 1, i,  alignment=Qt.AlignCenter) 

        GroupBox = QGroupBox("Monitor")
        GroupBox.setLayout(gridBox)
        return GroupBox  
        
    def OperaterGroupBox(self):             
        self.AutoE = QSliderButton(Qt.Horizontal)
        self.AutoE.setMaximum(1)
        self.AutoE.setTickPosition(QSlider.TicksBelow)
        self.AutoE.setFocusPolicy(Qt.NoFocus)
        self.AutoE.setMinimumSize(100, 50)

        label = QLabel('Auto Emission:')
        label.setFont(QFont("Calibri",20))
        label.setStyleSheet("color: rgb(15,34,139);")
        
        self.led = LedWidget()
        self.led.setDiameter(30)
        self.led.setMinimumSize(50,50)
        
        labelInfo = QLabel('Gun No:ABC123\nTable:BEANCH008')
        labelInfo.setFont(QFont("Calibri",18))
        labelInfo.setStyleSheet("color: rgb(15,34,139);")
        
        box =  QHBoxLayout();
        box.addWidget(label)  
        box.addWidget(self.AutoE)   
        box.addWidget(self.led)  
        box.addStretch(1)  
        box.addWidget(labelInfo)      
         
        GroupBox = QGroupBox("Operate")
        GroupBox.setLayout(box)  
        return GroupBox   
       
    def ManualModeEnable(self, flg = True):
        for name in self.manual.keys():
            self.manual[name].setVisible(flg)
        
        
        