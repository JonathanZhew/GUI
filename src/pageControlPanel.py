'''
Created on Apr 25, 2018

@author: zhenfengzhao
'''
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox, QLabel, QDoubleSpinBox,\
    QPushButton
from QMeter import QMeter
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ledwidget import LedWidget
from functools import partial
from PyQt5.Qt import QIcon

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
                SetBox.valueChanged.connect(partial(self.setDemand, SetBox, row))
                self.manual[name] = SetBox
                gridBox.addWidget(SetBox, 1, i,  alignment=Qt.AlignCenter) 

        GroupBox = QGroupBox("Monitor")
        GroupBox.setLayout(gridBox)
        return GroupBox  
    
    def setDemand(self, edit, row):
        type1 = row['type']
        conversion = row['conversion']
        cmd = row['set']
        value = 0
        if(type1 == 't'):
            value = edit.text()
        elif(type1 == 'd'):
            value = edit.value()
        elif(type1 == 'e'):
            text = edit.currentText()
            args = text.split(':')
            if(args[0].isdigit()):
                value = int(args[0])
            else:
                value = edit.currentIndex()
        self.__comm.setValue(cmd, value, type1, conversion)
        #(self, cmd, value, vtype='d', conversion = 1):
        
    def setAllValue(self, values):
        #print(values, self.Readers.values())
        for i, name in enumerate(self.Readers.keys()):    
            value = values[i]
            maxV = self.Readers.getItems(name, 'max')
            percent = 100*value/maxV
            str1 = self.Readers.getItems(name, 'format')
            text1 = str1.format(value)
            self.meters[name].setValue(text1, percent) 
            #print(name, value, percent)  

    def OperaterGroupBox(self):   
        stylesheet = """
            QPushButton { qproperty-iconSize: 48px 48px; 
                          min-height: 48px;
                          font-size: 12pt;
                        }
            """                    
        self.btnAutoHVon = QPushButton('On')
        self.btnAutoHVoff = QPushButton('Off')    
        
        self.btnTaskStop = QPushButton(QIcon('ico/stop.png'),'')
        self.btnTaskPause = QPushButton(QIcon('ico/pause.png'),'')
        self.btnTaskPlay = QPushButton(QIcon('ico/play.png'),'')

        self.btnAutoHVon.setStyleSheet(stylesheet)
        self.btnAutoHVoff.setStyleSheet(stylesheet)        
        self.btnTaskStop.setStyleSheet(stylesheet)
        self.btnTaskPause.setStyleSheet(stylesheet)
        self.btnTaskPlay.setStyleSheet(stylesheet)
        self.btnTaskStop.setVisible(False)
        self.btnTaskPause.setVisible(False)
        self.btnTaskPlay.setVisible(False)
        
        self.btnAutoHVon.clicked.connect(self.clickedHvOn)        
        self.btnAutoHVoff.clicked.connect(self.clickedHvOff)   
        self.btnTaskStop.clicked.connect(self.clickedTaskStop) 
        self.btnTaskPause.clicked.connect(self.clickedTaskPause)
        self.btnTaskPlay.clicked.connect(self.clickedTaskPlay)
        
        label = QLabel('AutoHV:')
        label.setFont(QFont("Calibri",20))
        label.setStyleSheet("color: rgb(15,34,139);")
        
        self.led = LedWidget()
        self.led.setDiameter(30)
        self.led.setMinimumSize(50,50)
        
        self.labelInfo = QLabel('Gun No:ABC123\nTable:BEANCH008')
        self.labelInfo.setFont(QFont("Calibri",18))
        self.labelInfo.setStyleSheet("color: rgb(15,34,139);")
        
        box =  QHBoxLayout();
        box.addWidget(label)  
        
        box.addWidget(self.btnAutoHVon)
        box.addWidget(self.btnAutoHVoff)
        box.addWidget(self.btnTaskPause)
        box.addWidget(self.btnTaskPlay)
        box.addWidget(self.btnTaskStop)
        
        box.addWidget(self.led)  
        box.addStretch(1)  
        box.addWidget(self.labelInfo)      
         
        GroupBox = QGroupBox("Operate")
        GroupBox.setLayout(box)  
        return GroupBox   
       
    def ManualModeEnable(self, flg = True):
        for name in self.manual.keys():
            self.manual[name].setVisible(flg)
                        
        self.btnTaskStop.setVisible(flg)
        self.btnTaskPause.setVisible(flg)
        self.btnTaskPlay.setVisible(flg)
        
    def setLabelInfo(self, GunNo, TableNo):
        text = 'Gun No:{0}\nTable:{1}'.format(GunNo, TableNo)
        self.labelInfo.setText(text)
        
    def clickedHvOn(self):
        cmd = self.cmdList.getItems('Emission','set')
        self.__comm.setValue(cmd, 1, 'e')
    
    def clickedHvOff(self):
        cmd = self.cmdList.getItems('Emission','set')
        self.__comm.setValue(cmd, 0, 'e')
     
    def clickedTaskPlay(self):
        cmd = self.cmdList.getItems('Task','set')
        self.__comm.setValue(cmd, 3, 'e')           
     
    def clickedTaskStop(self):
        cmd = self.cmdList.getItems('Task','set')
        self.__comm.setValue(cmd, 1, 'e')  
        
    def clickedTaskPause(self):
        cmd = self.cmdList.getItems('Task','set')
        self.__comm.setValue(cmd, 2, 'e')     
        
        
        
        
        
        