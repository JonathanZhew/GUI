'''
Created on Apr 23, 2018

@author: zhenfengzhao
'''
import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QTabWidget
from menu import myMenu
from toolBar import myToolBar
from Communication import CMessenger
from statusBar import myStatusBar
from pageControlPanel import ControlPanel
from CDatabase import RtReadDataBase, CommandDataBase
from HmiProtocol import HmiProtocol
from DlgConfigure import ConfigureData
import struct
from pageGraph import QOscilPanel
from DigitalFilter import KaiserFilter
import datetime
import csv
import os
import logging

class App(QMainWindow): 
    def __init__(self):
        super().__init__()
        self.title = 'EE_GUI V2.00 PyQt5 zhenfeng.zhao@asml.com'
        
        #Log
        date = datetime.datetime.now()
        name = 'Log' + date.strftime("%Y-%m-%d")+'.txt'
        file = os.path.join('log', name)  
        logging.basicConfig(filename=file,level=logging.DEBUG,format='%(asctime)s:%(name)s - %(levelname)s - %(message)s')
        logging.debug('Start app ...')
        
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
        self.cfgData.requestAll()    
        self.filter = KaiserFilter()
        
 
    def initUI(self):
        self.setWindowTitle(self.title)       
        
        #CentralWidget layout        
        self.ControlPanel = ControlPanel(self.comm, self.RtReadList, self.CmdList)
        self.OscilPanel = QOscilPanel(self.RtReadList)   
        self.tabs = QTabWidget()
        self.tabs.addTab(self.ControlPanel, "    Panel    ")
        self.tabs.addTab(self.OscilPanel.page, "    Chart    ")
        
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
        
        self.InitialSaveDat()
        #test
        #self.comm.testCallbcak()
        #self.fleshDbValue(3131, 1)        
               
    def InitialSaveDat(self):
        date = datetime.datetime.now()
        name = date.strftime("%Y-%m-%d_%H_%M_%S")+'.csv'
        file = os.path.join('log', name)
        self.fileSaveDat = file
        with open(self.fileSaveDat, 'w', newline='') as csvfile:
            datas = ['datetime']+ self.OscilPanel.Oscil.names
            writer = csv.writer(csvfile)
            writer.writerow(datas) 
        
    def SaveRtData(self, values):
        if(self.fileSaveDat==''):
            return
        with open(self.fileSaveDat, 'a', newline='') as csvfile:
            datas = [str(datetime.datetime.now())]+ values
            writer = csv.writer(csvfile)
            writer.writerow(datas) 
                
    def handleReceive(self, frame): 
        self.ControlPanel.led.toggleState() 
        if(frame.cmd == self.cmdRtRead):
            self.fleshRtData(frame.data)
        else:
            self.fleshDbValue(frame.cmd, frame.data)

    def fleshDbValue(self, cmdID, data):         
        row = self.CmdList.getRowbyCmd(cmdID)        
        if(cmdID == row['read']):
            typ = row['type']
            row['value'] = self.comm.maker.unpack(typ, data, row['conversion'])
            #value =self.CmdList.getItems('Vtip target', 'value')
            #print('read', cmdID, 'value', row['value'])
            
        log = 'Rx: cmd:{0:d} {1} data:{2} raw:'.format(cmdID, row['name'], str(row['value']))
        if(data!=None):
            log = log+ data.hex()
        logging.info(log)
        
    def fleshRtData(self, data): 
        values = struct.unpack('dddddd', data)
        for i, row in enumerate(self.RtReadList.values()):
            values[i] = values[i]*row['conversion']
        self.SaveRtData(values)
        #print(values)
        values[0] = self.filter.conv(values[0]) 
        new_value = [values[1],values[2],values[5],values[3],values[4],values[0]]
        self.ControlPanel.setAllValue(new_value) 
        self.OscilPanel.setAllValue(new_value)         
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
    