'''
Created on Apr 23, 2018

@author: zhenfengzhao
'''
import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QMessageBox
from HmiProtocol import HmiProtocol
from usb_can_drv import Usb2CanDev
from pcie_drv import PcieDriver

class CMessenger(HmiProtocol):
    def __init__(self, FrameMaker = None):   
        super(CMessenger, self).__init__()    
        self.SendQ=[]
        self.RecvQ=[] 
        self.maker = FrameMaker
        self.__name = ''
        self.__isopen = False
        self.__dev = None
        self.__devUsb = Usb2CanDev()
        try:
            self.__devPCIe = PcieDriver(1600)
        except:
            print("Initial PcieDriver error:", sys.exc_info()[0])
 
        self.repeatFrame = None
        self.timer=QtCore.QTimer()
        self.timer.timeout.connect(self.__MessageHub)        
        self.timerCount = 0
        
    def open(self, name = 'USB-CAN'):
        self.__name = name
        #pcie
        if(self.__name == 'PCIe'):
            try:
                self.__dev = self.__devPCIe
                self.__dev.open()
            except:
                QMessageBox.question(self, 'error', "Fail to open PCIe", QMessageBox.Ok, QMessageBox.Ok)
            if(self.__dev.is_open()):
                self.__isopen = True                    
        #usb-can        
        elif(self.__name == 'USB-CAN'):
            self.__dev = self.__devUsb
            self.__isopen = self.__dev.open()
            print('open', self.__name, self.__isopen)
        
        if self.__isopen:    
            self.timer.start(10)
            
        return self.__isopen
    
    def close(self):
        self.timer.stop()
        self.__dev.close()
        self.__isopen = False  
        print('Comm close!')

    def __read(self):
        if(not self.__isopen):
            return b''
        msg = self.__dev.read() 
        return msg

    def __write(self, msg):
        if(not self.__isopen):
            return False
        self.__dev.write(msg)
        return True
        
    def is_open(self):
        return self.__isopen
    
    def setValue(self, cmd, value, vtype='d'):
        frame = self.maker.setValue(self, cmd, value, vtype)
        self.SendQ.append(frame)
    
    def requestValue(self, cmd):
        frame = self.maker.requestValue(cmd)
        self.SendQ.append(frame)
    
    def repeatRequest(self, cmd, time = 100):
        self.repeatFrame = self.maker.requestValue(cmd)  
        
    def __MessageHub(self):
        #read comm
        self.RecvProcess()
        
        self.timerCount = self.timerCount+1        
        if self.timerCount >= 10:
            self.timerCount = 0
            if(self.repeatFrame!= None):
                self.__write(self.repeatFrame)
        elif len(self.SendQ):
            frame = self.SendQ.pop(0)
            self.__write(frame)
    
    def RegisterReciveHandle(self, func):  
        self.rcvhandle =  func  
        
    def RecvProcess(self):               
        buff = self.__read()
        if len(buff) < 32:
            return
        try:    
            frame = self.maker.parseAck(buff)      
            self.rcvhandle(frame) 
            
        except:
            print("RecvProcess error:", sys.exc_info())
            
    def testCallbcak(self):
        Frame = self.maker.requestValue(3103)  
        try:          
            self.rcvhandle(Frame) 
        except:
            print("RecvProcess error:", sys.exc_info())

    