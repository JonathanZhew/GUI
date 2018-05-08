'''
Created on Apr 30, 2018

@author: zhenfengzhao
'''
import csv
from PyQt5.Qt import QPoint

class CDataBase(dict):
    def __init__(self, csvfile):
        self.db = {}
        with open(csvfile, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if(row['name']!=''):
                    self.db[row['name']]=row
    
    def getItems(self, name, Item):
        row = self.db[name]
        return row[Item]

    def setItems(self, name, Item, value):
        row = self.db[name]
        row[Item] = value
    
    def getRowbyName(self, name):
        return self.db[name]

    def keys(self):
        return self.db.keys()
    
class RtReadDataBase(CDataBase):
    def __init__(self, csvfile):
        super(RtReadDataBase, self).__init__(csvfile)
        for name in self.db.keys():
            self.db[name]['max'] = float(self.db[name]['max'])
            self.db[name]['min'] = float(self.db[name]['min'])
            self.db[name]['wr'] = True if (self.db[name]['wr'] == 'TRUE')  else False
            self.db[name]['value'] = None
            
            args = self.db[name]['valid'].split('~')
            x = float(args[0])
            y = float(args[1]) 
            self.db[name]['valid'] = QPoint(x,y)


class CommandDataBase(CDataBase):
    def __init__(self, csvfile):
        super(CommandDataBase, self).__init__(csvfile)
        self.__cmdIDs = {} 
        for name in self.db.keys():
            cmdRead = int(self.db[name]['set'])
            cmdWrite = int(self.db[name]['read'])
            self.db[name]['set'] = cmdRead
            self.db[name]['read'] = cmdWrite
            self.db[name]['value'] = None
            
            strRange = self.db[name]['range'] 
            if('~' in strRange):
                args = strRange.split('~')
                minv = float(args[0])
                maxv = float(args[1])
                self.db[name]['min'] = minv
                self.db[name]['max'] = maxv
            else:
                self.db[name]['min'] = 0.0
                self.db[name]['max'] = 100.0
                
            # fast cmd index    
            self.__cmdIDs[cmdRead] = self.db[name]
            self.__cmdIDs[cmdWrite] = self.db[name]
            
    def getRowbyCmd(self, cmd):
        return self.__cmdIDs[cmd] 
    
    def clearValuebyGroup(self, group):
        for name in self.db.keys():
            if group == self.db[name]['group']:
                self.db[name]['value'] = None
