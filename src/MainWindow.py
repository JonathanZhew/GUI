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


class App(QMainWindow):
 
    def __init__(self):
        super().__init__()
        self.title = 'EE_GUI V2.00 PyQt5 zhenfeng.zhao@asml.com'
        self.initUI()
 
    def initUI(self):
        self.setWindowTitle(self.title)

        #initial backstage
        self.comm = CMessenger()
        self.comm.open()        
                
        #initial the front desk GUI
        self.mainMenu = myMenu(self) 
        self.toolBar = myToolBar(self, self.comm)         
        
        
        self.statusBar = myStatusBar(self.comm)
        self.setStatusBar(self.statusBar)
        
        #CentralWidget layout
        self.tabs = QTabWidget()
        self.tab1 = ControlPanel(self.comm)
        self.tab2 = QWidget()
        self.tabs.addTab(self.tab1,"    Panel    ")
        self.tabs.addTab(self.tab2,"    Chart    ")
        
        self.setCentralWidget(self.tabs)
       
        #self.show()
        self.showMaximized()    
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
    