'''
Created on Apr 23, 2018

@author: zhenfengzhao
'''
from PyQt5.QtWidgets import QAction, QMenu 

class myMenu(QMenu):
    def __init__(self, mainWindow):        
        super(myMenu, self).__init__(mainWindow)
 
        self.menubar = mainWindow.menuBar() 
        fileMenu = self.menubar.addMenu('File')
        cfgMenu = self.menubar.addMenu('Configuration')
        #viewMenu = self.menubar.addMenu('View')
        #searchMenu = self.menubar.addMenu('Search')
        toolsMenu = self.menubar.addMenu('Tools')
        helpMenu = self.menubar.addMenu('Help')
 
        exitButton = QAction('Exit', self)
        exitButton.setShortcut('Ctrl+Q')
        exitButton.setStatusTip('Exit application')
        exitButton.triggered.connect(mainWindow.close)
        fileMenu.addAction(exitButton)

