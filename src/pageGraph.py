'''
Created on May 29, 2018

@author: zhenfengzhao
'''
from PyQt5.QtWidgets import QHBoxLayout, QPushButton, QLabel, QLineEdit, QVBoxLayout,\
    QWidget, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QFont
from OscilloPyQtGraph import Oscillograph
import pyqtgraph as pg
import pyqtgraph.exporters
import datetime
import os

class QOscilPanel():
    def __init__(self, ReadObjs):
        super(QOscilPanel, self).__init__()
        self.Objs = ReadObjs
        self.Trigerflg = False
        
        self.Panel = QHBoxLayout()
        self.btnSample = QPushButton('start')
        
        self.btnSaveImage = QPushButton('save image')
        self.btnResetDat = QPushButton('reset')
        self.fileSaveDat = ''
        
        self.editSampleRate = QLineEdit()       
        #self.editSampleRate.setMaxLength(4)
        self.editSampleRate.setAlignment(Qt.AlignRight)
        self.editSampleRate.setMaximumWidth(60)
        self.editSampleRate.setText("1000")
        self.editSampleRate.setValidator(QtGui.QIntValidator())
        self.editSampleRate.setFont(QFont("Arial",12))
           
        self.Panel.addWidget(QLabel('Sample time (ms):'))       
        self.Panel.addWidget(self.editSampleRate)
        self.Panel.addWidget(self.btnSample)
        self. Panel.addWidget(self.btnSaveImage)
        self.Panel.addWidget(self.btnResetDat)
        self.Panel.addStretch(1)
        
        #Oscillograph  
        self.Oscil = Oscillograph()        
        for row in ReadObjs.values():
            self.Oscil.CreateChanel(row['name'], row['uint'], row['min'],row['max'],row['color'])
            
        # inital second tab
        self.page = QWidget()
        Layout = QVBoxLayout()
        Layout.addWidget(self.Oscil)
        Layout.addLayout(self.Panel)        
        self.page.setLayout(Layout)
        
        self.btnSample.clicked.connect(self.ClickSampleStart)
        self.btnResetDat.clicked.connect(self.ClickResetDat)
        self.btnSaveImage.clicked.connect(self.ClickSaveImage)
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.RenewOscil)
               
        self.ClickSampleStart()

    def setAllValue(self, values):
        if self.Trigerflg:
            self.Trigerflg = False
            self.Oscil.renew(values)    
            #self.Oscil.mydraw()
    
    def ClickResetDat(self):
        self.Oscil.reset()
         
    def ClickSampleStart(self):
        if self.btnSample.text() == 'start':
            self.btnSample.setText('stop')
            ms = int(self.editSampleRate.text())
            self.timer.start(ms) 
            self.Oscil.SetSample(ms)            
            #print(self.editSampleRate.text())            
        else:           
            self.btnSample.setText('start')
            self.timer.stop()
    
    def RenewOscil(self):
        self.Trigerflg = True        
        
    def saveFileDialog(self, myfilter="All files (*.*)"):
        date = datetime.datetime.now()
        name = date.strftime("%Y-%m-%d_%H_%M_%S")
        file = os.path.join('log', name)        
        fileName, _ = QFileDialog.getSaveFileName(None, "Save", file , myfilter)
        return fileName
      
    def ClickSaveImage(self):
        fileName = self.saveFileDialog("image(*.png)")
        if fileName:
            exporter = pg.exporters.ImageExporter(self.Oscil.plotItem)
            #exporter.parameters()['width'] = 100  
            # save to file        
            print("ClickSaveImage", fileName)
            try:
                exporter.export(fileName)
            except Exception as e:
                print (e)        
    