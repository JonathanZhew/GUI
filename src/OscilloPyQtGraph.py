# -*- coding: utf-8 -*-

import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
import numpy as np

WAVE_DATA_DEEP = 600
NUM_AXIS_SICK = 6
X_AXIS_SCALE = int(WAVE_DATA_DEEP/NUM_AXIS_SICK)
class CWave:
    def __init__(self, name, maxV, minV, color):
        self.data = np.zeros(WAVE_DATA_DEEP)
        self.name = name
        self.color = color
        self.maxV = maxV
        self.minV = minV
        self.currV = 0
        #self.index = 0
        
class Oscillograph(pg.PlotWidget):
    def __init__(self, parent=None):
        super(Oscillograph, self).__init__(parent)
        self.show()

        self.views = []
        self.plots = []
        self.waves=[]
        self.names=[]
        self.count = 0
        self.index = 0
        self.SetSample(10)
        self.timeAxis = [datetime.datetime.now()]*(NUM_AXIS_SICK+1)

        self.plotItem.showAxis('top')
        self.plotItem.showAxis('right')
        self.plotItem.showGrid(x= True, y= True, alpha = 0.3)
        self.plotItem.setXRange(0, WAVE_DATA_DEEP)
        self.plotItem.setLimits(xMax=WAVE_DATA_DEEP+10,xMin=-10,)
        
        self.plotItem.vb.sigResized.connect(self.updateViews)
                
    def CreateChanel(self, name, unit='V' , minV=0.0, maxV=10.0, color='#ff0000'):
        wave = CWave(name, maxV, minV, color)
        self.waves.append(wave)
        self.names.append(name)
        if(self.count == 0):
            ax = self.plotItem.getAxis('right')            
            view = self.plotItem
            plot = self.plotItem.plot(self.waves[0].data,pen = None, symbolSize=3, symbolPen=pg.mkPen(None), symbolBrush=pg.mkBrush(self.waves[0].color), name = self.waves[0].name)
        else:
            #create axis, view
            view = pg.ViewBox()            
            ax = pg.AxisItem('right')
            self.plotItem.layout.addItem(ax, 2, self.count+2)
            self.plotItem.scene().addItem(view)
            ax.linkToView(view)
            view.setXLink(self.plotItem)
            plot = pg.PlotDataItem(wave.data, pen = None, symbolSize=3, symbolPen=pg.mkPen(None), symbolBrush=pg.mkBrush(color))
            view.addItem(plot)
        
        text= "<span style='color: {!s}'>\u2587</span> {!s} ({!s})".format(color, name, unit)
        labelStyle = {'color': '#FFF', 'font-size': '12pt'}
        ax.setLabel(text, **labelStyle)

        view.setYRange(minV, maxV)
        delta = (maxV - minV)*0.05
        view.setLimits(yMin=minV-delta, yMax=maxV+delta)
        
        self.views.append(view)
        self.plots.append(plot)
        
        self.count= self.count+1       
        
                
    def renew(self, datas):
        self.autoSetXAxis(self.index)
        emptyIndex = (self.index + 5)%WAVE_DATA_DEEP
        self.index = (self.index + 1)%WAVE_DATA_DEEP
        print(emptyIndex, self.index)
        for ch in range(0,len(datas)):
            self.waves[ch].data[self.index:emptyIndex]=[-1]*(emptyIndex-self.index)
            self.waves[ch].data[self.index] = datas[ch]
            self.waves[ch].currV = datas[ch]

        self.plots[0].setData(self.waves[0].data)

    def renew_ch(self, ch, data):
        self.autoSetXAxis(self.index)
        self.index = (self.index + 1)%WAVE_DATA_DEEP
        self.waves[ch].data[self.index] = data
        self.waves[ch].currV = data          

    ## Handle view resizing 
    def updateViews(self):
        for index in range(1, self.count):
            self.views[index].setGeometry(self.plotItem.vb.sceneBoundingRect())
            self.views[index].linkedViewChanged(self.plotItem.vb, self.views[index].XAxis)

    def mydraw(self):
        for index in range(0, self.count):
            self.plots[index].setData(self.waves[index].data)
        text = ['%s = %.6g' % (wase.name,wase.currV) for wase in self.waves]
        self.plotItem.setTitle(text)

    def SetSample(self, microsecond):
        x = ["%.3g(s)" % float(i*microsecond/10) for i in range(NUM_AXIS_SICK+1)]
        self.AxisDict = dict(zip(range(0, WAVE_DATA_DEEP+X_AXIS_SCALE, X_AXIS_SCALE), x))
        self.plotItem.getAxis('bottom').setTicks([self.AxisDict.items()])

    def autoSetXAxis(self, index):
        if(index%X_AXIS_SCALE==0):
            self.plotItem.getAxis('bottom').setTicks([self.AxisDict.items()])   
            if(index):
                self.timeAxis[int(index/X_AXIS_SCALE)] = datetime.datetime.now()
                time = self.timeAxis[int(index/X_AXIS_SCALE)]-self.timeAxis[0]                
                self.AxisDict[index] = "%.3g(s)" % float(time.total_seconds())
            else:
                self.timeAxis[NUM_AXIS_SICK] = datetime.datetime.now()
                time = self.timeAxis[NUM_AXIS_SICK]-self.timeAxis[0]                
                self.AxisDict[WAVE_DATA_DEEP] = "%.3g(s)" % float(time.total_seconds())
                self.timeAxis[0] = self.timeAxis[NUM_AXIS_SICK]
"""test"""
# Make sure that we are using QT5
from PyQt5 import QtCore, QtWidgets
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QIcon
import random
import time
import datetime

class Window(QWidget):  
    def __init__(self):
        super().__init__()
        self.title = 'PyQt5 simple window - pythonspot.com'
        self.left = 60
        self.top = 60
        self.width = 1540
        self.height = 880
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
           
        self.Oscil = Oscillograph()
        self.Oscil.CreateChanel('BV2','V', -35000,0)
        self.Oscil.CreateChanel('HV2','uA',0,5000, color='#00ff00')
        self.Oscil.CreateChanel('HV1','V',0,2000, color='#0000ff')
        #self.Oscil.mydraw()
        button = QPushButton('PyQt5 button', self)

        layout = QHBoxLayout()
        layout.addWidget(button)
        layout.addWidget(self.Oscil)
        self.setLayout(layout)
        
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.myTimerEvent)
        self.timer.start(50)
        self.Oscil.SetSample(50)
        #self.show()

        self.timer1 = QtCore.QTimer()
        self.timer1.timeout.connect(self.Oscil.mydraw)
        self.timer1.start(100)
        
    def myTimerEvent(self):
        datas = [random.randint(-100, 200)-15000, random.randint(0, 20)+10.12346468, random.randint(0, 100)+2000]
        self.Oscil.renew(datas)        
        #log = datetime.datetime.now().strftime('[%H:%M:%S] ')
        #print(log)
        
    
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    clock = Window()
    clock.show()
    sys.exit(app.exec_())
    #qApp.exec_()
