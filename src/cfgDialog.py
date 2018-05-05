'''
Created on May 2, 2018

@author: zhenfengzhao
'''
from PyQt5.QtWidgets import QLineEdit, QGroupBox, QVBoxLayout, QDialog,\
    QPushButton, QHBoxLayout, QGridLayout, QLabel, QDoubleSpinBox
from QScientificSpinBox import QScientificSpinBox

class DlgConfigure(QDialog):
    def __init__(self, Messenger, Cmdlist):
        super(DlgConfigure, self).__init__()
        self.comm = Messenger
        self.setWindowTitle("Parameter Configure")
        self.Cmdlist = Cmdlist
        
        self.TargetList=[]
        self.TripList=[]        
        self.SortCmdList(Cmdlist)
                
        edit = QLineEdit()
        box= QVBoxLayout()
        box.addWidget(edit)
        GroupTarget= QGroupBox("Target")
        GroupTarget.setLayout(box)
        
        edit = QLineEdit()
        box= QVBoxLayout()
        box.addWidget(edit)
        GroupTrip= QGroupBox("Trip threshold")
        GroupTrip.setLayout(box)
        
        btnOK = QPushButton('OK')
        btnCancel = QPushButton('Cancel')
        btnApply = QPushButton('Apply')
        btnApply.setEnabled(False)
        
        BtnBox= QHBoxLayout()
        BtnBox.addStretch()
        BtnBox.addWidget(btnOK)
        BtnBox.addWidget(btnCancel)
        BtnBox.addWidget(btnApply)
        
        boxes = self.GroupBoxes(Cmdlist)
        
        Layout = QVBoxLayout()
        Layout.addLayout(boxes) 
        Layout.addLayout(BtnBox)
        #vbox.addStretch(1)
        self.setLayout(Layout)
        
    def SortCmdList(self, Cmdlist):         
        for name in Cmdlist.keys():
            group = Cmdlist.getItems(name, 'group')
            if(group == 'Target'):
                self.TargetList.append(Cmdlist.getRowbyName(name))
            if(group == 'Trip'):
                self.TripList.append(Cmdlist.getRowbyName(name))
                
    def GroupBoxes(self):        
        gird = QGridLayout()
        edit = QLineEdit('ABC123')
        gird.addWidget(QLabel('Gun No:'), 0, 0) 
        gird.addWidget(edit, 0, 1) 
        edit = QLineEdit('Bench123')
        gird.addWidget(QLabel('Table:'), 1, 0) 
        gird.addWidget(edit, 1, 1)         
        groupInfo = QGroupBox("self Info")
        groupInfo.setLayout(gird)
        
        gird = QGridLayout()
        for i, row in enumerate(self.TargetList):
            lable  = QLabel(row['name']+' ('+row['uint']+')'+':')                
            edit = QDoubleSpinBox()
            edit.setRange(row['min'],row['max'] )
            gird.addWidget(lable, i, 0) 
            gird.addWidget(edit, i, 1)                 
        groupTarget = QGroupBox("Target value")
        groupTarget.setLayout(gird)    
        
        gird = QGridLayout()
        for i, row in enumerate(self.TripList):
            lable  = QLabel(row['name']+' ('+row['uint']+')'+':')                
            edit = QScientificSpinBox()
            edit.setRange(row['min'],row['max'] )
            gird.addWidget(lable, i, 0) 
            gird.addWidget(edit, i, 1)                 
        groupTrip = QGroupBox("Trip threshold")
        groupTrip.setLayout(gird)
        
        Layout = QVBoxLayout()
        Layout.addWidget(groupInfo) 
        Layout.addWidget(groupTarget) 
        Layout.addWidget(groupTrip) 
        return Layout

    def ReadAllValues(self):
        #clear
        for row in self.TargetList:
            row['value'] = None
            self.comm.requestValue(row['read'])  
            
        for row in self.TripList:
            row['value'] = None
            self.comm.requestValue(row['read']) 
            
        return True    
        
        
        
        