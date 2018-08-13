# -*- coding: utf-8 -*-
import pyqtgraph as pg
import numpy as np

WAVE_DATA_DEEP = 600
NUM_AXIS_SICK = 6
X_AXIS_SCALE = int(WAVE_DATA_DEEP/NUM_AXIS_SICK)

class kidPlotItem():
    def __init__(self, name, axis, view, plot, buff):
        self.name = name
        self.axis = axis
        self.view = view
        self.plot = plot
        self.buffer =buff
        self.currVal= 0.0

class myAxisItem(pg.AxisItem):
    def __init__(self, orientation, parent=None):
        super(myAxisItem, self).__init__(orientation)
        
    def resizeEvent(self, ev=None):
        ## Set the position of the label
        nudge = 5
        br = self.label.boundingRect()
        p = QtCore.QPointF(0, 0)
        if self.orientation == 'left':
            p.setY(int(self.size().height()/2 + br.width()/2))
            p.setX(-nudge)
        elif self.orientation == 'right':
            p.setY(int(self.size().height()/2 + br.width()/2))
            p.setX(-br.height()+6)  #rewrite
        elif self.orientation == 'top':
            p.setY(-nudge)
            p.setX(int(self.size().width()/2. - br.width()/2.))
        elif self.orientation == 'bottom':
            p.setX(int(self.size().width()/2. - br.width()/2.))
            p.setY(int(self.size().height()-br.height()+nudge))
        self.label.setPos(p)
        self.picture = None
                                    
class Oscillograph(pg.PlotWidget):
    def __init__(self, parent=None):
        super(Oscillograph, self).__init__()
        self.channels = {}
        self.index = 0
        self.SetSample(10)
        self.timeAxis = [datetime.datetime.now()]*(NUM_AXIS_SICK+1)

        self.plotItem.showAxis('top')
        #self.plotItem.showAxis('right')
        self.plotItem.showGrid(x= True, y= True, alpha = 0.3)
        self.plotItem.setXRange(0, WAVE_DATA_DEEP)
        self.plotItem.setLimits(xMax=WAVE_DATA_DEEP+10,xMin=-10,)
        
        self.plotItem.vb.sigResized.connect(self.updateViews)      
          

    def CreateChanel(self, name, unit='V' , minV=0.0, maxV=10.0, color='#ff0000'):        
        buffer  = np.zeros(WAVE_DATA_DEEP)
        count = len(self.channels)
        if  count == 0:
            axis = myAxisItem('right')
            self.plotItem.layout.addItem(axis, 2, count+2)
            #axis = self.plotItem.getAxis('right')            
            view = self.plotItem.getViewBox()
            axis.linkToView(view)
            plot = self.plotItem.plot(buffer, pen = None, symbolSize=3, symbolPen=pg.mkPen(None), symbolBrush=pg.mkBrush(color), name = name)
        else:
            axis = myAxisItem('right')
            self.plotItem.layout.addItem(axis, 2, count+2)
            view = pg.ViewBox()  
            self.plotItem.scene().addItem(view)
            axis.linkToView(view)
            view.setXLink(self.plotItem)
            plot = pg.PlotDataItem(buffer, pen = None, symbolSize=3, symbolPen=pg.mkPen(None), symbolBrush=pg.mkBrush(color))
            view.addItem(plot)
            
        text= "<span style='color: {!s}'>\u2587</span> {!s} ({!s})".format(color, name, unit)
        labelStyle = {'color': '#FFF', 'font-size': '12pt'}
        axis.setLabel(text, **labelStyle)
        
        view.setYRange(minV, maxV)
        delta = (maxV - minV)*0.05
        view.setLimits(yMin=minV-delta, yMax=maxV+delta)          
         
        self.channels[name] = kidPlotItem(name, axis, view, plot, buffer)
     
        if name == 'IP1':
            self.setIP1AxisTicks(axis, minV, maxV)
       
    def reset(self):
        self.index = 0
        for plot in self.channels.values():
            plot.buffer.fill(0)
            
    def renew(self, datas):
        self.autoSetXAxis(self.index)
        emptyIndex = (self.index + 5)%WAVE_DATA_DEEP
        self.index = (self.index + 1)%WAVE_DATA_DEEP
        #print(emptyIndex, self.index)
        for plot, value in zip(self.channels.values(), datas):
            plot.buffer[self.index:emptyIndex]=[-1]*(emptyIndex-self.index)
            plot.buffer[self.index] = value
            plot.currVal = value
            plot.plot.setData(plot.buffer)   
            
        self.setTitle()

    ## Handle view resizing 
    def updateViews(self):
        for i, plot in enumerate(self.channels.values()):
            if i > 0:
                plot.view.setGeometry(self.plotItem.vb.sceneBoundingRect())
                plot.view.linkedViewChanged(self.plotItem.vb, plot.view.XAxis)

    def IPConvAdc2Torr(self, val):
        return 0.1**(11-(val/1024)*3.9)

    def setTitle(self):
        text = ['%s = %.5g' % (plot.name,plot.currVal) for plot in self.channels.values()]
        if 'IP1' in self.channels:
            text2 = 'IP1 = %.3g'%self.IPConvAdc2Torr(self.channels['IP1'].currVal)
            text.append(text2)
        self.plotItem.setTitle(text)
    
    def setIP1AxisTicks(self, axis, minV, maxV):  
        xdict = {}
        for x in range(int(minV), int(maxV+100), 100):
             xdict[x] = '%.3g'%self.IPConvAdc2Torr(x)
        axis.setTicks([xdict.items()])

    def SetSample(self, microsecond):
        x = ["%.3g(s)" % float(i*microsecond/10) for i in range(NUM_AXIS_SICK+1)]
        self.AxisDict = dict(zip(range(0, WAVE_DATA_DEEP+X_AXIS_SCALE, X_AXIS_SCALE), x))
        self.plotItem.getAxis('bottom').setTicks([self.AxisDict.items()])
        
        self.reset()

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
        self.Oscil.CreateChanel('IP1','torr',0,1000, color='#ff00ff')
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
