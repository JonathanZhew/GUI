'''
Created on Apr 23, 2018

@author: zhenfengzhao
'''
import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QTabWidget,QMessageBox
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
from PyQt5.QtCore import QTimer

class App(QMainWindow): 
    def __init__(self):
        super().__init__()
        self.title = 'EE_GUI V2.00 PyQt5 zhenfeng.zhao@asml.com'
        
        #Log
        self.startTime = datetime.datetime.now()
        name = 'Log' + self.startTime.strftime("%Y-%m-%d")+'.txt'
        file = os.path.join('log', name)  
        logging.basicConfig(filename=file,level=logging.DEBUG,format='%(asctime)s:%(name)s - %(levelname)s - %(message)s')
        logging.debug('Start app ...')

                
        self.StatusInfo = 'Wellcom'
        self.initDat()
        self.initUI()
        
        self.SendQueue=[]
        self.errMessage = b''
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.handleErrMessage)
        self.timer.start(2800)  

                
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
        
        self.SaveName = b''
        #self.InitialSaveDat()
        #test
        #self.comm.testCallbcak()
        #self.fleshDbValue(3131, 1)        
                     
    def newSaveFile(self, name):
        if not os.path.lexists('log'):
            os.makedirs('log')
        
        self.SaveName = name  
        self.SaveFile = os.path.join('log', name)     
        if not os.path.lexists(self.SaveFile):
            with open(self.SaveFile, 'w', newline='') as csvfile:
                headline = ['datetime']+ self.OscilPanel.Oscil.names
                writer = csv.writer(csvfile)
                writer.writerow(headline) 
        print('newSaveFile:', self.SaveFile)
                    
    def SaveRtData(self, values):
        date = datetime.datetime.now()        
        name = date.strftime("%Y-%m-%d")+'.csv'
        if name != self.SaveName:
            self.newSaveFile(name)
      
        with open(self.SaveFile, 'a', newline='') as csvfile:
            datas = [str(date)]+ values
            writer = csv.writer(csvfile)
            writer.writerow(datas) 
    
    def handleErrMessage(self):        
        if self.errMessage != b'':
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setInformativeText(self.errMessage)
            date = datetime.datetime.now()
            message = "<font size = 5 color = red >{0}<br/>Firmware protection is triggered!</font>".format(str(date))
            msg.setText(message)
            msg.setWindowTitle("MessageBox")
            msg.setStandardButtons(QMessageBox.Yes)
            msg.exec_() 
            self.errMessage = b''
        self.timer.start(4800)  
                    
    def handleReceive(self, frame): 
        self.ControlPanel.led.toggleState()
              
        if(frame.err):
            log = 'frame ACK err:{0:d} cmd:{1:d}, seq:{2:d}, {3}'.format(frame.err, frame.cmd, frame.sequence, frame.data.decode("utf-8"))
            logging.error(log)  
            print(log)
            self.errMessage = log
            return
                
        if(frame.cmd == self.cmdRtRead):
            self.fleshRtData(frame.data)
        else:
            self.fleshDbValue(frame.cmd, frame.data)

    def fleshDbValue(self, cmdID, data):   
        try:      
            row = self.CmdList.getRowbyCmd(cmdID)        
            if(cmdID == row['read']):
                typ = row['type']
                row['value'] = self.comm.maker.unpack(typ, data, row['conversion'])
                #value =self.CmdList.getItems('Vtip target', 'value')
                #print('read', cmdID, 'value', row['value'])
                
            if cmdID == self.CmdList.getItems('Emission','read'):                
                try:
                    str1 = self.CmdList.getItems('Emission','range')
                    args = str1.split(';')
                    str2 = args[row['value']]
                    args = str2.split(':')
                    text = 'Emission {0}'.format(args[1])
                except:
                    text = str(row['value'])
                 
                if self.StatusInfo != text: 
                    logging.info(self.ControlPanel.statusInfo.text()) 
                    self.startTime = datetime.datetime.now()
                    self.StatusInfo = text
                    log = 'Rx: cmd:{0:d} {1}'.format(cmdID, text)
                    logging.info(log) 
                delta = datetime.datetime.now() - self.startTime     
                str1 = str(delta)
                str1 = str1.split('.')[0]
                info = "{0}  ({1})".format(text, str1)
                self.ControlPanel.setStatusInfo(info)      
                
            else:
                log = 'Rx: cmd:{0:d} {1} data:{2} '.format(cmdID, row['name'], str(row['value']))
                if(data!=None):
                    log = log+' raw:'+data.hex()
                logging.info(log)                
            
        except:
            log = 'fleshDbValue cmd{0:d} err {1}'.format(cmdID, sys.exc_info())
            logging.error(log)
            print(log)
            
    def fleshRtData(self, data): 
        try:
            values = struct.unpack('dddddd', data)
            #for i, row in enumerate(self.RtReadList.values()):
            #    values[i] = values[i]*row['conversion']
            values = [abs(number) for number in values]
            values[4] = values[4]*1000000
            orderVal = [values[1],values[2],values[5],values[3],values[4],values[0]]
            saveVal = orderVal[:]
            saveVal[5] =  self.ControlPanel.IPConvAdc2Torr(saveVal[5])
            self.SaveRtData(saveVal)
            #print(values)
            orderVal[5] = self.filter.conv(orderVal[5])         
            self.ControlPanel.setAllValue(orderVal) 
            self.OscilPanel.setAllValue(orderVal)   
                  
        except:
            log = 'fleshRtData err {0}'.format(sys.exc_info())
            logging.error(log)
            print(log)     

                        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
    
