'''
Created on Apr 23, 2018

@author: zhenfengzhao
'''
import sys
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QAction, QTabWidget, QVBoxLayout,QLineEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot
from menu import myMenu
from toolBar import myToolBar
from Communication import CMessenger
from statusBar import myStatusBar
from pageControlPanel import ControlPanel
from CDatabase import RtReadDataBase, CommandDataBase
from HmiProtocol import HmiProtocol
from cfgDialog import ConfigureData
import struct

class App(QMainWindow):
 
    def __init__(self):
        super().__init__()
        self.title = 'EE_GUI V2.00 PyQt5 zhenfeng.zhao@asml.com'
        self.initDat()
        self.initUI()
        
        self.SendQueue=[]
        
    def initDat(self):
        #initial backstage
        maker = HmiProtocol()
        self.comm = CMessenger(maker)
        self.comm.RegisterReciveHandle(self.handleReceive)
        self.comm.open()
                     
        self.RtReadList = RtReadDataBase('RtRead.csv')      
        self.CmdList = CommandDataBase('CmdList.csv')    
         
        self.cfgData = ConfigureData(self.comm, self.CmdList)      
 
    def initUI(self):
        self.setWindowTitle(self.title)
        
        #CentralWidget layout
        self.tabs = QTabWidget()
        self.ControlPanel = ControlPanel(self.comm, self.RtReadList)
        self.tab2 = QWidget()
        self.tabs.addTab(self.ControlPanel, "    Panel    ")
        self.tabs.addTab(self.tab2, "    Chart    ")
        
        self.setCentralWidget(self.tabs)    
        
        self.mainMenu = myMenu(self) 
        self.toolBar = myToolBar(self, self.comm)         
                
        self.statusBar = myStatusBar(self.comm)
        self.setStatusBar(self.statusBar)   
        #self.show()
        self.showMaximized()   
        
        #Event
        self.cmdRtRead = self.CmdList.getItems('RtRead', 'read')
        self.comm.repeatRequest(self.cmdRtRead)
        
        #test
        #self.comm.testCallbcak()
        #self.fleshDbValue(3131, 1)
        
                
    def handleReceive(self, frame): 
        if(frame.cmd == self.cmdRtRead):
            self.fleshRtData(frame.data)
        else:
            self.fleshDbValue(frame.cmd, frame.data)

    def fleshDbValue(self, cmdID, data): 
        row = self.CmdList.getRowbyCmd(cmdID)
        type = row['type']
        row['value'] = self.comm.maker.unpack(type, data)
        #value =self.CmdList.getItems('Vtip target', 'value')
        #print(value)
     
    def fleshRtData(self, data): 
        head = struct.unpack('dddddd', data)    
        for i, meter in enumerate(self.ControlPanel.meters.values()):
            meter.setValue(head[i])
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
    