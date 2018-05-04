# import USB-CAN module
import ControlCAN
from ctypes import *
from time import sleep
import struct

# parameters define
DeviceIndex = 0
CANIndex = 0
DevType = ControlCAN.VCI_USBCAN2
class Usb2CanDev():
    def __init__(self):
        print("Initial Usb2CanDev")
        super(Usb2CanDev, self).__init__()
        self.__isopen = False
        self.frame = b''
        self.frames = []
 
    def __del__(self):
        # Close device
        nRet = ControlCAN.VCI_CloseDevice(DevType,DeviceIndex)
        print("__del__:VCI_CloseDevice nRet = %d"%nRet)

    def open(self):
        print("Usb2CanDev:open()")
        nRet = ControlCAN.VCI_OpenDevice(DevType,DeviceIndex,0)
        if(nRet == ControlCAN.STATUS_ERR):
            self.__isopen = False
            return self.__isopen
        else:
            self.__isopen = True
            CAN_InitEx = ControlCAN.VCI_INIT_CONFIG_EX()
            CAN_InitEx.CAN_ABOM = 0
            CAN_InitEx.CAN_Mode = 0
            # Baud Rate
            CAN_InitEx.CAN_BRP = 6
            CAN_InitEx.CAN_BS1 = 3
            CAN_InitEx.CAN_BS2 = 2
            CAN_InitEx.CAN_SJW = 1

            CAN_InitEx.CAN_NART = 0
            CAN_InitEx.CAN_RFLM = 0
            CAN_InitEx.CAN_TXFP = 1
            CAN_InitEx.CAN_RELAY = 0

            nRet = ControlCAN.VCI_InitCANEx(DevType,DeviceIndex,CANIndex,byref(CAN_InitEx))
            if(nRet == ControlCAN.STATUS_ERR):
                print("Init device failed!")
                exit()
            else:
                print("Init device success!")
            # Set filter
            CAN_FilterConfig = ControlCAN.VCI_FILTER_CONFIG()
            CAN_FilterConfig.FilterIndex = 0
            CAN_FilterConfig.Enable = 1        
            CAN_FilterConfig.ExtFrame = 0
            CAN_FilterConfig.FilterMode = 0
            CAN_FilterConfig.ID_IDE = 0x07B0
            CAN_FilterConfig.ID_RTR = 0
            CAN_FilterConfig.ID_Std_Ext = 0
            CAN_FilterConfig.MASK_IDE = 0x07B0
            CAN_FilterConfig.MASK_RTR = 0
            CAN_FilterConfig.MASK_Std_Ext = 0
            nRet = ControlCAN.VCI_SetFilter(DevType,DeviceIndex,CANIndex,byref(CAN_FilterConfig))
            if(nRet == ControlCAN.STATUS_ERR):
                print("Set filter failed!")
                exit()
            else:
                print("Set filter success!")
                
            # Register callback function
            #pGetDataCallback = ControlCAN.PVCI_RECEIVE_CALLBACK(self.GetDataCallback)
            #ControlCAN.VCI_RegisterReceiveCallback(DeviceIndex,pGetDataCallback)
            # Start CAN
            nRet = ControlCAN.VCI_StartCAN(DevType,DeviceIndex,CANIndex);
            if(nRet == ControlCAN.STATUS_ERR):
                print("Start CAN failed!")
                exit()
            else:
                print("Start CAN success!")
    
            return self.__isopen
        
    def close(self):
        # Close device
        nRet = ControlCAN.VCI_CloseDevice(DevType,DeviceIndex)
        print("close():VCI_CloseDevice nRet = %d"%nRet)
        self.__isopen = False

    def is_open(self):
         return self.__isopen

    def GetDataCallback(self, DeviceIndex,CANIndex, cb_Len =1):
        print(DeviceIndex,CANIndex, cb_Len)
        DataNum = ControlCAN.VCI_GetReceiveNum(DevType, DeviceIndex,CANIndex)
        CAN_ReceiveData = (ControlCAN.VCI_CAN_OBJ*DataNum)()
        if(DataNum > 0):
            ReadDataNum = ControlCAN.VCI_Receive(DevType, DeviceIndex, CANIndex, byref(CAN_ReceiveData), DataNum,0)
            for i in range(0,DataNum):
                for j in range(0,CAN_ReceiveData[i].DataLen):
                    #print("%02X "%CAN_ReceiveData[i].Data[j],end='')
                    kk = CAN_ReceiveData[i].Data[j]
                    self.frame += (kk&0xff).to_bytes(1, byteorder='big')

            #can_bus_frame_detector
            frame_len = len(self.frame)
            if(frame_len >=4):
                if(not((self.frame[0]==0x08)and(self.frame[1]==0x04) and(self.frame[2]==0x02)and(self.frame[3]==0x01))):
                    self.frame = b''
                elif(frame_len >=32):
                    body_length_info = self.frame[16:20]
                    body_len = struct.unpack('I', body_length_info)[0]
                    if(body_len > 1024):
                        self.frame = b''
                    elif(frame_len>=body_len+32):
                        print(self.frame)
                        return self.frame              
                
    def read(self):
        good_frame = b''
        DataNum = ControlCAN.VCI_GetReceiveNum(DevType, DeviceIndex,CANIndex)
        CAN_ReceiveData = (ControlCAN.VCI_CAN_OBJ*DataNum)()
        if(DataNum > 0):
            ReadDataNum = ControlCAN.VCI_Receive(DevType, DeviceIndex, CANIndex, byref(CAN_ReceiveData), DataNum,0)
            for i in range(0,DataNum):
                for j in range(0,CAN_ReceiveData[i].DataLen):
                    #print("%02X "%CAN_ReceiveData[i].Data[j],end='')
                    kk = CAN_ReceiveData[i].Data[j]
                    self.frame += (kk&0xff).to_bytes(1, byteorder='big')

            #can_bus_frame_detector
            frame_len = len(self.frame)
            if(frame_len >=4):
                if(not((self.frame[0]==0x08)and(self.frame[1]==0x04) and(self.frame[2]==0x02)and(self.frame[3]==0x01))):
                    self.frame = b''
                elif(frame_len >=32):
                    body_length_info = self.frame[16:20]
                    body_len = struct.unpack('I', body_length_info)[0]
                    if(body_len > 1024):
                        self.frame = b''
                    elif(frame_len>=body_len+32):
                        good_frame = self.frame
                        self.frame = b''
        return good_frame
                    
                        
    def write(self, msg):        
        CAN_SendData = (ControlCAN.VCI_CAN_OBJ)()
        CAN_SendData.ExternFlag = 0
        CAN_SendData.RemoteFlag = 0
        CAN_SendData.ID = 0x07F2
        CAN_SendData.SendType = 0
        datas = [msg[i:i+8] for i in range(0, len(msg), 8)]
        for data in datas:
            CAN_SendData.DataLen = len(data)
            for i in range(0,CAN_SendData.DataLen):
                CAN_SendData.Data[i] = data[i]
            nRet = ControlCAN.VCI_Transmit(DevType,DeviceIndex,CANIndex,byref(CAN_SendData),1)
            #print('usb_can_dev write()',nRet)
            if(nRet == ControlCAN.STATUS_ERR):
                ControlCAN.VCI_ResetCAN(DevType,DeviceIndex,CANIndex)
                print('usb_can_dev write() err')
				
				
