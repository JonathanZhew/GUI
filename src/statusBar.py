'''
Created on Apr 25, 2018

@author: zhenfengzhao
'''

from PyQt5.QtWidgets import QStatusBar
from Communication import CMessenger

class myStatusBar(QStatusBar):
    def __init__(self, Messenger):        
        super(myStatusBar, self).__init__()
        self.__comm = Messenger
        self.showMessage("status bar")
"""
    def __init__(self, Messenger, parent = None):        
        super(myStatusBar, self).__init__(parent)
        self.__comm = Messenger
        self.showMessage("status bar")
"""
