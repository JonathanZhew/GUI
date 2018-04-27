'''
Created on Apr 25, 2018

@author: zhenfengzhao
'''
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout,QGridLayout, QProgressBar, QLineEdit, QLabel
from meter import CMeter

class ControlPanel(QWidget):
    def __init__(self, Messenger):        
        super(ControlPanel, self).__init__()
        self.__comm = Messenger
        
        grid = QGridLayout()
        grid.addWidget(QProgressBar(),0, 1,alignment= QtCore.Qt.AlignCenter)
        grid.addWidget(QLineEdit(),1,1)
        grid.addWidget(QLabel('hello'),2,1)
        
        meter = CMeter('HV1')
        vbox=QVBoxLayout()
        vbox.addWidget(meter) 
        vbox.addStretch(1)
        self.setLayout(vbox)
    
    