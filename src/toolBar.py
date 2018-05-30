'''
Created on Apr 23, 2018

@author: zhenfengzhao
'''

from PyQt5.QtWidgets import QAction, QToolBar, QComboBox, QPushButton,\
    QMessageBox
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon, QPixmap
from Communication import CMessenger
from DlgConfigure import ConfigureData, DlgConfigure
#from ledwidget import LedWidget

class myToolBar(QToolBar):
    def __init__(self, mainWindow, Messenger):        
        super(myToolBar, self).__init__()
        self.__comm = Messenger
        self.mainWin = mainWindow
      
        #comuniction        
        icon = QIcon()
        icon.addPixmap(QPixmap('ico/link_normal.png'))
        icon.addPixmap(QPixmap('ico/link_disabled.png'), QIcon.Disabled)
        #icon.addPixmap(QPixmap('ico/link_clicking.png'), QIcon.Active)
        icon.addPixmap(QPixmap('ico/link_on.png'), QIcon.Normal, QIcon.On)
        self.btnLink = QAction(icon,"open",self)
        self.btnLink.setCheckable(True)
        self.btnLink.triggered.connect(self.toggleLink)
        self.btnLink.setStatusTip('connect to devices')
        self.refresLinkStatus()  
        
        icon = QIcon()
        icon.addPixmap(QPixmap('ico/cfgpara.png'))        
        self.btnCfg = QAction(icon,"configure",self)
        self.btnCfg.setStatusTip('configure HV parameters')
        self.btnCfg.triggered.connect(self.chickbtnCfg)
        
        
        icon = QIcon()
        icon.addPixmap(QPixmap('ico/manual.png'))     
        icon.addPixmap(QPixmap('ico/manual_on.png'), QIcon.Normal, QIcon.On)   
        self.btnManual = QAction(icon,"configure",self)
        self.btnManual.setCheckable(True)
        self.btnManual.setStatusTip('configure HV parameters')
        self.btnManual.triggered.connect(self.chickbtnManual)
        
        #layout
        Bar = mainWindow.addToolBar('tool bar')
        Bar.setFloatable(False)
        #conn.addWidget(comboBox)
        Bar.addAction(self.btnLink)
        Bar.addAction(self.btnCfg)
        Bar.addAction(self.btnManual)
        
    def refresLinkStatus(self):            
        if self.__comm.is_open():
            self.btnLink.setChecked(True)
            #self.mainWin.ControlPanel.AutoE.setEnabled(True)
        else:
            self.btnLink.setChecked(False) 
            #self.mainWin.ControlPanel.AutoE.setEnabled(False)
        
    def toggleLink(self, state):   
        #print(state)     
        if state:
            self.__comm.open();
        else:
            self.__comm.close();
         
        self.refresLinkStatus()   
   
    def chickbtnCfg(self):
        dlg = DlgConfigure(self.mainWin.cfgData)
        dlg.exec_()  
        self.mainWin.ControlPanel.setLabelInfo(self.mainWin.cfgData.GunNo, self.mainWin.cfgData.TableNo) 
        self.mainWin.ControlPanel.setMyTicks()
          
    def chickbtnManual(self):
        flg = self.btnManual.isChecked()
        cmd = self.mainWin.CmdList.getItems('Manual', 'set')
        val = 1 if flg else 0
        self.__comm.setValue(cmd, val, vtype='e')
        self.mainWin.ControlPanel.ManualModeEnable(flg)
            
        
    
    
