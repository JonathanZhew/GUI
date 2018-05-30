'''
Created on May 2, 2018

@author: zhenfengzhao
'''
from PyQt5.QtWidgets import QLineEdit, QGroupBox, QVBoxLayout, QDialog,\
    QPushButton, QHBoxLayout, QGridLayout, QLabel, QDoubleSpinBox, QMessageBox
from QScientificSpinBox import QScientificSpinBox
from PyQt5.QtCore import pyqtSlot, QTimer

class ConfigureData():
    def __init__(self, Messenger, Cmdlist):
        #super(ConfigureData, self).__init__()
        self.comm = Messenger
        self.GunNo = 'ABC123' 
        self.TableNo = 'Table008' 
        self.list = {}
        self.settings = []
        for name in Cmdlist.keys():
            group = Cmdlist.getItems(name, 'group')
            if (group == 'Target') or (group == 'Trip'):
                self.list[name] = Cmdlist.getRowbyName(name)  
    
        self.requestAll()       
                
    def requestAll(self):
        for row in self.list.values():
            row['value'] = None
            self.comm.requestValue(row['read'])  
            
    def isAvailable(self):
        if(len(self.settings) == self.list.values()):
            for row, val in zip(self.list.values(), self.settings):
                if(row['value'] != val):
                    return False
        else:
            for row in self.list.values():
                if(row['value'] == None):
                    self.requestAll()
                    return False
        return True
           
    def setValues(self, values):
        self.settings = values
        for i, row in enumerate(self.list.values()):
            self.comm.setValue(row['set'], values[i], row['type'], row['conversion'])  
            print('set', row['set'], values[i], row['type'])
                
class DlgConfigure(QDialog):
    def __init__(self, cfgData):
        super(DlgConfigure, self).__init__()
        self.setWindowTitle("Parameter Configure")
        self.setMinimumWidth(320)
        self.editBoxes = {}
        self.cfgDat = cfgData
        
        #btnOK = QPushButton('OK')        
        #btnCancel = QPushButton('Cancel')
        self.btnApply = QPushButton('Apply')
        #self.btnApply.setEnabled(False)
          
        BtnBox= QHBoxLayout()
        BtnBox.addStretch()
        #BtnBox.addWidget(btnOK)
        #BtnBox.addWidget(btnCancel)
        BtnBox.addWidget(self.btnApply)
        
        boxes = self.GroupBoxes(cfgData.list)
        
        Layout = QVBoxLayout()
        Layout.addLayout(boxes) 
        Layout.addLayout(BtnBox)
        #vbox.addStretch(1)
        self.setLayout(Layout)
        
        self.showValue(cfgData.list)
        
        self.btnApply.clicked.connect(self.chickbtnAplly)
        #btnOK.clicked.connect(self.chickbtnOK)
        #btnCancel.clicked.connect(self.chickbtnCancel)
        
        self.timer=QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.checkResult)      

    def GroupBoxes(self, cfgList):        
        gird = QGridLayout()
        self.editGunNo = QLineEdit(self.cfgDat.GunNo)
        gird.addWidget(QLabel('Gun No:'), 0, 0) 
        gird.addWidget(self.editGunNo, 0, 1) 
        self.editTable = QLineEdit(self.cfgDat.TableNo)
        gird.addWidget(QLabel('Table:'), 1, 0) 
        gird.addWidget(self.editTable, 1, 1)         
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

    def showValue(self, cfgList):   
        for name, row in cfgList.items():
            value = row['value']
            if(value == None):
                self.btnApply.setEnabled(False)
                self.editBoxes[name].setEnabled(False)
            else:    
                self.editBoxes[name].setValue(value)  
    
    @pyqtSlot()
    def chickbtnAplly(self):
        self.cfgDat.GunNo = self.editGunNo.text()
        self.cfgDat.TableNo = self.editTable.text()
        values = []
        for edit in self.editBoxes.values():
            value = edit.value()
            values.append(value)
        self.cfgDat.setValues(values)    
        self.cfgDat.requestAll()   
        self.timer.start(1500)
        self.btnApply.setEnabled(False)
        
    @pyqtSlot()  
    def chickbtnOK(self):
        self.chickbtnAplly()
        self.done(0)
    
    @pyqtSlot()  
    def chickbtnCancel(self):
        self.done(1)
    
    def checkResult(self):
        self.btnApply.setEnabled(True)
        if self.cfgDat.isAvailable():  
            text = "Successfully set up configuration\n"   
        else:
            text = "ERROR: Failed to set configuration\n"          
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle("MessageBox")
        msg.setStandardButtons(QMessageBox.Yes)
        msg.exec_() 

                