'''
Created on Apr 23, 2018

@author: zhenfengzhao
'''

from PyQt5.QtWidgets import QAction, QToolBar, QComboBox, QPushButton
from PyQt5 import QtGui
from PyQt5.QtGui import QIcon, QPixmap
from Communication import CMessenger
#from ledwidget import LedWidget

class myToolBar(QToolBar):
    def __init__(self, mainWindow, Messenger):        
        super(myToolBar, self).__init__(mainWindow)
        self.__comm = Messenger
        '''
        #QIcon('exit24.png')
        exitAct = QAction('Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.triggered.connect(self.close)
        
        self.toolbar = mainWindow.addToolBar('Exit')
        self.toolbar.addAction(exitAct)
        '''
        
        #comuniction        
        icon = QIcon()
        icon.addPixmap(QPixmap('ico/link_normal.png'))
        icon.addPixmap(QPixmap('ico/link_disabled.png'), QIcon.Disabled)
        #icon.addPixmap(QPixmap('ico/link_clicking.png'), QIcon.Active)
        icon.addPixmap(QPixmap('ico/link_on.png'), QIcon.Normal, QIcon.On)
        #btn.setIcon(icon)

        self.btnLink = QAction(icon,"open",self)
        self.btnLink.setCheckable(True)
        self.btnLink.triggered.connect(self.toggleLink)
        self.btnLink.setStatusTip('connect to devices')
        self.refresLinkStatus()   
        #layout
        Bar = mainWindow.addToolBar('tool bar')
        Bar.setFloatable(False)
        #conn.addWidget(comboBox)
        Bar.addAction(self.btnLink)
        
    def refresLinkStatus(self):            
        if self.__comm.is_open():
            self.btnLink.setChecked(True)
        else:
            self.btnLink.setChecked(False) 
        
    def toggleLink(self, state):   
        print(state)     
        if state:
            self.__comm.open();
        else:
            self.__comm.close();
         
        self.refresLinkStatus()   
   
            


