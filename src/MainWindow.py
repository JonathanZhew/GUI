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
import struct

class App(QMainWindow):
 
    def __init__(self):
        super().__init__()
        self.title = 'EE_GUI V2.00 PyQt5 zhenfeng.zhao@asml.com'
        self.initUI()
        
        self.SendQueue=[]

 
    def initUI(self):
        self.setWindowTitle(self.title)
        #initial backstage
        maker = HmiProtocol()
        self.comm = CMessenger(maker)
        self.comm.open()
             
        self.RtReadList = RtReadDataBase('RtRead.csv')      
        self.CmdList = CommandDataBase('CmdList.csv')    
                
        #initial the front desk GUI
    
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
        self.timerMessageHub=QtCore.QTimer()
        self.timerMessageHub.timeout.connect(self.MessageHub)
        self.timerMessageHub.start(10)
        self.count = 0
        self.cmdRtRead = self.CmdList.getItems('RtRead', 'read')
        
        self.fleshDbValue(3131, 1)
           
    def MessageHub(self):
        if not self.comm.is_open():
            return 
        
        #read comm
        self.RecvProcess()
        
        self.count = self.count+1        
        if self.count >= 10:
            self.count = 0
            frame = self.comm.requestValue(self.cmdRtRead)
            self.comm.write(frame)
        elif len(self.SendQueue):
            frame = self.self.SendQueue.pop(0)
            self.comm.write(frame)
            
    def RecvProcess(self):               
        frame = self.comm.read()
        if len(frame) < 32:
            return
        
        head_section = frame[:32]
        value_section = frame[32: ]
        
        info = self.comm.parseAck(head_section)

        if(info.cmd == self.cmdRtRead):
            self.fleshRtData(value_section)
        else:
            self.fleshDbValue(info.cmd, value_section)

    def fleshDbValue(self, cmdID, value_section): 
        row = self.CmdList.getRowbyCmd(cmdID)
        #type = row['type']
        #row['value'] = self.FrameMaker.unpack(type, value_section)
        #value =self.CmdList.getItems('Vtip target', 'value')
        #print(value)
     
    def fleshRtData(self, value_section): 
        pass  

         
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
    