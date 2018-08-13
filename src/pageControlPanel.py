'''
Created on Apr 25, 2018

@author: zhenfengzhao
'''
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox, QLabel, QDoubleSpinBox,\
    QPushButton, QProgressBar, QMessageBox
from QMeter import QMeter
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor
from ledwidget import LedWidget
from functools import partial
from PyQt5.Qt import QIcon
from math import log

STA_EMISS_ON = 1
STA_EMISS_OFF = 0

def num_after_point(x):
        s = str(x)
        if not '.' in s:
            return 0
        return len(s) - s.index('.') - 1
    
class ControlPanel(QWidget):
    def __init__(self, Messenger, RtReads, CmdList):        
        super(ControlPanel, self).__init__()
        self.__comm = Messenger
        self.cmdList = CmdList
        self.Readers = RtReads
        g1 = self.meterGroupBox(RtReads, CmdList)     
        g2 = self.OperaterGroupBox()   
        
        Layout = QVBoxLayout()
        Layout.addWidget(g1) 
        Layout.addWidget(g2) 
        #vbox.addStretch(1)
        self.setLayout(Layout)
        self.timer = QTimer()
        self.timer.timeout.connect(self.timeout)
        self.timer.start(800)      
        self.percentage = 0
        self.isRuningTask = True
        self.HvStatus = 0
            
    def meterGroupBox(self, RtReads, CmdList):       
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
                SetBox.setStyleSheet("color: rgb(100,100,100);background-color: rgb(242,242,242);")
                SetBox.setMinimumWidth(240)
                SetBox.setAlignment(Qt.AlignRight)
                SetBox.setVisible(False)
                #SetBox.setReadOnly(True)
                row = CmdList.getRowbyName(name)
                maxV = row['max']
                minV = row['min']
                step = row['step']
                num = num_after_point(step)
                SetBox.setSingleStep(step)
                SetBox.setDecimals(num)
                SetBox.setRange(minV,maxV)
                #(self, cmd, edit, type1, conversion):
                #SetBox.returnPressed.connect(partial(self.setDemand, SetBox, row))
                SetBox.lineEdit().returnPressed.connect(partial(self.setDemand, SetBox, row))
                self.manual[name] = SetBox
                gridBox.addWidget(SetBox, 1, i,  alignment=Qt.AlignCenter) 
        
        self.meters['IP1'].setTicks(['1e-11','1e-10','1e-9','1e-8','1e-7'])
        GroupBox = QGroupBox("Monitor")
        GroupBox.setLayout(gridBox)
        return GroupBox  
    
    def IPConvAdc2Torr(self, val):
        x =  0.1**(11-(val/1024)*3.9)
        g = float("{0:.3g}".format(x))
        return g
    
    def IPConvTorr2Adc(self, val):
        tmp = log(val, 10)
        return int((11+tmp)*1024/3.9)
    
    def setMyTicks(self):
        row = self.cmdList.getRowbyName('FC1 target')
        value = row['value']
        if( value!= None):
            self.meters['FC1'].setSpecialTick('Target', value, '{0:.3f}'.format(value), QColor(0, 0, 255))
        
        row = self.cmdList.getRowbyName('BV1 target')
        value = row['value']
        if( value!= None):
            self.meters['BV1'].setSpecialTick('Target', value, '{0:.1f}'.format(value), QColor(0, 0, 255))
    
        row = self.cmdList.getRowbyName('Vtip target')
        value = row['value']
        if( value!= None):
            self.meters['Vtip'].setSpecialTick('Target', value, '{0:.1f}'.format(value), QColor(0, 0, 255))
        '''    
        row = self.cmdList.getRowbyName('IP1 Normal')
        value = row['value']
        if( value!= None):
            ADC = self.IPConvTorr2Adc(value)
            self.meters['IP1'].setSpecialTick('Normal', ADC, '{0:.2g}'.format(value), QColor(0, 0, 255))            
            
        row = self.cmdList.getRowbyName('IP1 Alert')
        value = row['value']
        if( value!= None):
            ADC = self.IPConvTorr2Adc(value)
            self.meters['IP1'].setSpecialTick('Alarm', ADC, '{0:.2g}'.format(value), QColor(0, 0, 255))
        '''
        row = self.cmdList.getRowbyName('IP1 threshold')
        value = row['value']
        if( value!= None):
            ADC = self.IPConvTorr2Adc(value)
            self.meters['IP1'].setSpecialTick('Trip', ADC, '{0:.2g}'.format(value), QColor(255, 0, 0))    
            
    def setDemand(self, edit, row):
        type1 = row['type']
        conversion = row['conversion']
        cmd = row['set']
        value = 0
        if(type1 == 't'):
            value = edit.text()
        elif(type1 == 'd'):
            value = edit.value()/conversion
        elif(type1 == 'e'):
            text = edit.currentText()
            args = text.split(':')
            if(args[0].isdigit()):
                value = int(args[0])
            else:
                value = edit.currentIndex()
        self.__comm.setValue(cmd, value, type1)
        #(self, cmd, value, vtype='d', conversion = 1):
        
    def setAllValue(self, values):
        #print(values, self.Readers.values())
        for i, name in enumerate(self.Readers.keys()):    
            value = values[i]
            maxV = self.Readers.getItems(name, 'max')
            percent = 100*value/maxV
            str1 = self.Readers.getItems(name, 'format')
            if(name == 'IP1'):
                value = self.IPConvAdc2Torr(value)
            text1 = str1.format(value)
            self.meters[name].setValue(text1, percent) 
            #print(name, value, percent)  

    def OperaterGroupBox(self):   
        stylesheet = """
            QPushButton { 
                qproperty-iconSize: 48px 48px; 
                min-height: 48px;
                font-size: 12pt;
            }
            """                    
        self.btnAutoHVon = QPushButton('On')
        self.btnAutoHVoff = QPushButton('Off')    
        
        self.btnTaskPause = QPushButton(QIcon('ico/pause.png'),'')
        self.btnTaskPlay = QPushButton(QIcon('ico/play.png'),'')

        self.btnAutoHVon.setStyleSheet(stylesheet)
        self.btnAutoHVoff.setStyleSheet(stylesheet)        
        self.btnTaskPause.setStyleSheet(stylesheet)
        self.btnTaskPlay.setStyleSheet(stylesheet)
        
        self.btnAutoHVon.clicked.connect(self.clickedHvOn)        
        self.btnAutoHVoff.clicked.connect(self.clickedHvOff)   
        self.btnTaskPause.clicked.connect(self.clickedTaskPause)
        self.btnTaskPlay.clicked.connect(self.clickedTaskPlay)
        
        label = QLabel('AutoHV:')
        label.setFont(QFont("Calibri",20))
        label.setStyleSheet("color: rgb(15,34,139);")
        
        self.led = LedWidget()
        self.led.setDiameter(38)
        self.led.setMinimumSize(50,50)
        self.led.setColor(QColor('green'))
        self.AutoStatuebar = QProgressBar()
        self.AutoStatuebar.setMinimumSize(128,38)
        self.AutoStatuebar.setTextVisible(True)
        self.AutoStatuebar.setFormat("idel...")
        self.AutoStatuebar.setAlignment(Qt.AlignCenter);
        self.AutoStatuebar.setValue(50)
        
        self.labelInfo = QLabel('Gun No:ABC123\nTable:BEANCH008')
        self.labelInfo.setFont(QFont("Calibri", 10))
        self.labelInfo.setStyleSheet("color: rgb(15,34,139);")
        
        self.statusInfo = QLabel('\tWellcom to use gun control system...')
        self.statusInfo.setFont(QFont("Calibri",36))
        self.statusInfo.setStyleSheet("color: rgb(15,34,139);")
        
        box =  QHBoxLayout();
        box.addWidget(self.led) 
        box.addWidget(label) 
        box.addWidget(self.btnAutoHVon)
        box.addWidget(self.btnAutoHVoff)
        box.addWidget(self.btnTaskPause)
        box.addWidget(self.btnTaskPlay)      
        box.addWidget(self.AutoStatuebar) 
        box.addWidget(self.statusInfo)     
        box.addStretch(1)  
        box.addWidget(self.labelInfo)      
         
        GroupBox = QGroupBox("Operate")
        GroupBox.setLayout(box)  
        return GroupBox 
       
    def ManualModeEnable(self, flg = True):
        for name in self.manual.keys():
            self.manual[name].setVisible(flg)
            val = self.meters[name].value()
            self.manual[name].setValue(val)
        
    def setLabelInfo(self, GunNo, TableNo):
        text = 'Gun No:{0}\nTable:{1}'.format(GunNo, TableNo)
        self.labelInfo.setText(text)
    
    def popMessage(self):
        if(self.HvStatus == STA_EMISS_OFF) or (self.HvStatus == STA_EMISS_ON):
            ret = QMessageBox.Yes
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Warning")
            msg.setInformativeText('The current task is running!\nContinue?')
            msg.setWindowTitle("MessageBox")
            #msg.setDetailedText("The details are as follows:")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            ret = msg.exec_()
        return ret
    
    def setCmdHV(self, val):
        cmd = self.cmdList.getItems('Task','set')
        self.__comm.setValue(cmd, 1, 'e')     
        cmd = self.cmdList.getItems('Emission','set')
        self.__comm.setValue(cmd, val, 'e')

        self.cmdList.setItems('Emission','value', 'start')
        self.isRuningTask = True
        #self.timer.start(500)   
                
    def clickedHvOn(self):       
        if QMessageBox.Yes == self.popMessage(): 
            self.setCmdHV(STA_EMISS_ON)
    
    def clickedHvOff(self):
        if QMessageBox.Yes == self.popMessage():  
            self.setCmdHV(STA_EMISS_OFF)
     
    def clickedTaskPlay(self):
        cmd = self.cmdList.getItems('Task','set')
        self.__comm.setValue(cmd, 3, 'e')   
        self.isRuningTask = True
        
    def clickedTaskPause(self):
        cmd = self.cmdList.getItems('Task','set')
        self.__comm.setValue(cmd, 2, 'e')
        self.isRuningTask = False  

    def timeout(self):
        val = self.cmdList.getItems('Emission','value')
        self.HvStatus = val
        cmd = self.cmdList.getItems('Emission','read')
        self.__comm.requestValue(cmd)
        
        try:
            str1 = self.cmdList.getItems('Emission','range')
            args = str1.split(';')
            text = args[val]
        except:
            text = str(val)
                
        if val == STA_EMISS_ON:
            self.percentage = 100
            #self.timer.stop()
        elif val == STA_EMISS_OFF:
            self.percentage = 0
            #self.timer.stop()
        else:
            if self.isRuningTask == True:
                self.percentage = (self.percentage+20)%100
            else:
                self.percentage = 50
                                
        self.AutoStatuebar.setFormat(text)        
        self.AutoStatuebar.setValue(self.percentage)    
        
    def setStatusInfo(self, info):
        #date = datetime.datetime.now()
        #text = date.strftime(" %H:%M:%S ")+info
        self.statusInfo.setText(info)
 
        