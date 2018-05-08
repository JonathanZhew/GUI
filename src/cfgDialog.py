'''
Created on May 2, 2018

@author: zhenfengzhao
'''
from PyQt5.QtWidgets import QLineEdit, QGroupBox, QVBoxLayout, QDialog,\
    QPushButton, QHBoxLayout, QGridLayout, QLabel, QDoubleSpinBox
from QScientificSpinBox import QScientificSpinBox

class ConfigureData():
    def __init__(self, Messenger, Cmdlist):
        super(ConfigureData, self).__init__()
        self.comm = Messenger
        self.cfgList = self.ReortCmdList(Cmdlist)
        self.requestCfgData();
        
    def ReortCmdList(self, Cmdlist):
        newlist = {}
        for name in Cmdlist.keys():
            group = Cmdlist.getItems(name, 'group')
            if (group == 'Target') or (group == 'Trip'):
                newlist[name] = Cmdlist.getRowbyName(name)  
        return newlist
                
    def requestCfgData(self):
        for row in self.cfgList.values():
            row['value'] = None
            self.comm.requestValue(row['read'])  
                
class DlgConfigure(QDialog):
    def __init__(self, cfgList):
        super(DlgConfigure, self).__init__()
        self.setWindowTitle("Parameter Configure")
        self.editBoxes = {}
        
        btnOK = QPushButton('OK')
        btnCancel = QPushButton('Cancel')
        btnApply = QPushButton('Apply')
        btnApply.setEnabled(False)
        
        BtnBox= QHBoxLayout()
        BtnBox.addStretch()
        BtnBox.addWidget(btnOK)
        BtnBox.addWidget(btnCancel)
        BtnBox.addWidget(btnApply)
        
        boxes = self.GroupBoxes(cfgList)
        
        Layout = QVBoxLayout()
        Layout.addLayout(boxes) 
        Layout.addLayout(BtnBox)
        #vbox.addStretch(1)
        self.setLayout(Layout)
        
        self.fleshValue(cfgList)
                
    def GroupBoxes(self, cfgList):        
        gird = QGridLayout()
        edit = QLineEdit('ABC123')
        gird.addWidget(QLabel('Gun No:'), 0, 0) 
        gird.addWidget(edit, 0, 1) 
        edit = QLineEdit('Bench123')
        gird.addWidget(QLabel('Table:'), 1, 0) 
        gird.addWidget(edit, 1, 1)         
        groupInfo = QGroupBox("self Info")
        groupInfo.setLayout(gird)
        
        gird1 = QGridLayout()
        gird2 = QGridLayout()
        index1 = 0
        index2 = 0
        for name, row in cfgList.items():
            lable  = QLabel(name+' ('+row['uint']+')'+':')   
                         
            if(row['group'] == 'Target'):            
                edit = QDoubleSpinBox()
                #edit.setSpecialValueText('err')
                edit.setRange(row['min'],row['max'] )
                gird1.addWidget(lable, index1, 0) 
                gird1.addWidget(edit, index1, 1)  
                index1 = index1+1          
                  
            if(row['group'] == 'Trip'):            
                edit = QScientificSpinBox()
                #edit.setSpecialValueText('0')
                edit.setRange(row['min'],row['max'] )
                gird2.addWidget(lable, index2, 0) 
                gird2.addWidget(edit, index2, 1)  
                index2 = index2+1
                
            self.editBoxes[name]= edit  
                             
        groupTarget = QGroupBox("Target value")
        groupTarget.setLayout(gird1)    
        groupTrip = QGroupBox("Trip threshold")
        groupTrip.setLayout(gird2)
        
        Layout = QVBoxLayout()
        Layout.addWidget(groupInfo) 
        Layout.addWidget(groupTarget) 
        Layout.addWidget(groupTrip) 
        return Layout

    def fleshValue(self, cfgList):   
        for name, row in cfgList.items():
            value = row['value']
            if(value == None):
                self.editBoxes[name].setEnabled(False)
            else:    
                self.editBoxes[name].setValue(value)        
                