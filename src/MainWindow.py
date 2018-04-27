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
from RoundProgressBar import QRoundProgressBar 

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
        
        self.bar = QRoundProgressBar()
        self.bar.setFixedSize(300, 300)

        self.bar.setDataPenWidth(3)
        self.bar.setOutlinePenWidth(3)
        self.bar.setDonutThicknessRatio(0.85)
        self.bar.setDecimals(1)
        self.bar.setFormat('%v | %p %')
        # self.bar.resetFormat()
        self.bar.setNullPosition(90)
        #self.bar.setBarStyle(QRoundProgressBar.StyleDonut)
        self.bar.setDataColors([(0., QtGui.QColor.fromRgb(255,0,0)), (0.5, QtGui.QColor.fromRgb(255,255,0)), (1., QtGui.QColor.fromRgb(0,255,0))])

        self.bar.setRange(0, 300)
        self.bar.setValue(260)
        
        self.setCentralWidget(self.bar)
       
        #self.show()
        self.showMaximized()    
 
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
    