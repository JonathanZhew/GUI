
import struct
import datetime
    
byteorder = 'little'

class HmiProtocol():
    def __init__(self):
        self.__Source     =0
        self.__Dest       =0
        self.__Sequence   =0

    def __make_frame(self, cmdId, arrBody, arrLen):
        frame = b'\x08\4\2\1'
        frame += cmdId.to_bytes(4, byteorder)
        frame += self.__Source.to_bytes(4, byteorder)
        frame += self.__Dest.to_bytes(4, byteorder)
        length = arrLen
        frame += length.to_bytes(4, byteorder)
        frame +=  b'\0\0\0\0'
        frame +=  b'\0\0\0\0'
        self.__Sequence = self.__Sequence+1
        frame += self.__Sequence.to_bytes(4, byteorder)
        frame += arrBody
        #log = datetime.datetime.now().strftime('[%H:%M:%S] ')
        #log += "send:"
        #log += ''.join('{:02x}'.format(x) for x in frame)
        #print(log)
        return frame
                 
    def setValue(self, cmdId, value, Type):
        if(Type == 't'):
            arrLen = len(value)+1            
            arrBody = str(value).encode()
            arrBody +=b'\0'
            #print(len(arrBody))
        if(Type == 'd'):
            arrLen = 8
            arrBody = bytearray(struct.pack("d", value))
        elif(Type == 'e'):		
            arrLen = 4
            arrBody = value.to_bytes(4, byteorder)
        return self.__make_frame(cmdId, arrBody, arrLen)

    def requestValue(self, cmdId):
        return self.__make_frame(cmdId, b'', 0)

    def parseMag(self, mag):
        return 1688
    
if __name__ == '__main__':
    lst = HmiProtocol()
    frame = lst.setValue(4004, 'hello', 't')    
    print(lst)
    print(frame)
