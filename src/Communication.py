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
from PyQt5.QtCore import QThread, pyqtSignal
import logging
class CMessenger(QThread):    
    sig1 = pyqtSignal(bytes, int, int)    
    sig2 = pyqtSignal()  
    def __init__(self, FrameMaker = None):   
        #QThread.__init__(self)
        super(CMessenger, self).__init__()    
        self.SendQ=[]
        self.RecvQ=[] 
        self.recvbuf = b'' 
        self.maker = FrameMaker
        self.__name = ''
        self.__isopen = False
        self.__dev = None

        self.__devUsb = Usb2CanDev()

        """
        try:
            self.__devPCIe = PcieDriver(1600)
        except:
            print("Initial PcieDriver error:", sys.exc_info()[0])
         """
        self.repeatFrame = None
         
        self.timerCount = 0          
        
        self.start()  
        self.sig1.connect(self.RecvProcess)
        self.sig2.connect(self.__MessageHub)
        #self.timer=QtCore.QTimer()
        #self.timer.timeout.connect(self.__MessageHub)        
 
        
    def open(self, name = 'USB-CAN'):
        self.__name = name
        #pcie
        if(self.__name == 'PCIe'):
            try:
                self.__dev = self.__devPCIe
                self.__dev.open()
            except:
                QMessageBox.question(self, 'error', "Fail to open PCIe", QMessageBox.Ok, QMessageBox.Ok)
                log = 'open PCIe {0}'.format(sys.exc_info())
                logging.error(log)
            if(self.__dev.is_open()):
                self.__isopen = True                    
        #usb-can        
        elif(self.__name == 'USB-CAN'):
            self.__dev = self.__devUsb
            self.__isopen = self.__dev.open()
            print('open', self.__name, self.__isopen)
            
        return self.__isopen
    
    def close(self):
        #self.timer.stop()
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
        if not self.__isopen:
            txt = 'setValue() error port is not open setValue()'
            print(txt)
            logging.info(txt)
            return             
        frame = self.maker.DemandFrame(cmd, value, vtype)
        self.SendQ.append(frame)
        
        txt = 'TX: set cmd {0:d} value {1}'.format(cmd, str(value))
        logging.info(txt)
    
    def requestValue(self, cmd):
        frame = self.maker.RequestFrame(cmd)
        self.SendQ.append(frame)
    
    def repeatRequest(self, cmd, time = 100):
        self.repeatFrame = self.maker.RequestFrame(cmd)  
     
    def run(self):  
        while(1):
            QThread.msleep(10)
            if self.__isopen:
                self.sig2.emit()
                #self.__MessageHub()
        
    def __MessageHub(self):      
        #read comm
        self.popRecv()
        
        self.timerCount = self.timerCount+1        
        if self.timerCount >= 5:
            self.timerCount = 0
            if(self.repeatFrame!= None):
                self.__write(self.repeatFrame)
        elif len(self.SendQ):
            frame = self.SendQ.pop(0)
            try:   
                self.__write(frame)
            except:
                log = '__MessageHub err {0}'.format(sys.exc_info())
                print(log)
                logging.error(log)
    
    def RegisterReciveHandle(self, func):  
        self.rcvhandle =  func  
        
    def popRecv(self):               
        buffer = self.__read()
        len1 = len(buffer)
        if(len1>0):
            self.sig1.emit(buffer, len1, 0)
            
    def RecvProcess(self, buffer, len1, ret):               
        frames = self.maker.parseAck(buffer) 
        for frame in frames: 
            self.rcvhandle(frame)   

        
    