import struct

byteorder = 'little'

class CStructAck():
    def __init__(self, frame):
        head = struct.unpack('IIIIIIII', frame[:32])        
        self.err = head[6]
        self.cmd = head[5]
        self.length = head[4]
        self.sequence = head[7]
        if(len(frame)>32):
            self.data = frame[32:]
        else:   
            self.data = b''
class CStructSend():
    def __init__(self, head_section):
        head = struct.unpack('IIIIIIII', head_section[:32])        
        self.cmd = head[1]
        self.length = head[4]
        self.sequence = head[7]
        self.data = frame[32:]

class HmiProtocol():
    def __init__(self):
        self.__Source     =0
        self.__Dest       =0
        self.__Sequence   =0
        self.LoopBuffer   = b''

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
                 
    def DemandFrame(self, cmdId, value, Type):
        if(Type == 't'):
            arrLen = len(value)+1            
            arrBody = str(value).encode()
            arrBody +=b'\0'
            #print(len(arrBody))
        if(Type == 'd'):
            arrLen = 8
            arrBody = bytearray(struct.pack("d", value))
        elif(Type == 'e') or (Type == 'i'):		
            arrLen = 4
            arrBody = int(value).to_bytes(4, byteorder)
        return self.__make_frame(cmdId, arrBody, arrLen)

    def RequestFrame(self, cmdId):
        return self.__make_frame(cmdId, b'', 0)
    

    def parseAck(self, buffer):
        frames = []
        self.LoopBuffer = self.LoopBuffer + buffer
        TotalLen = len(self.LoopBuffer)
        while(TotalLen >=32):
            try:
                index = self.LoopBuffer.index(b'\x08\4\2\1')
                if index >=0:
                    self.LoopBuffer = self.LoopBuffer[index:]
                    length= struct.unpack('I', self.LoopBuffer[16:20])[0]
                    #frame = CStructAck(buffer[index:])
                    if length > 1024:
                        TotalLen = TotalLen - 20
                        self.LoopBuffer = self.LoopBuffer[20:]
                    elif length <= TotalLen-32:     
                        frame = CStructAck(self.LoopBuffer[:length+32])                   
                        frames.append(frame)
                        self.LoopBuffer = self.LoopBuffer[length + 32:]
                        TotalLen = TotalLen - length - 32
                    else:
                        #find start mark, but not enough length wait next time
                        print(TotalLen, "wait next time")
                        TotalLen = 0
            except:   
                # Can not find start with 0x08040201 unload the buffer
                print(TotalLen, "Can not find")
                TotalLen = 0
                self.LoopBuffer = bytearray(b'')
        return frames
    
    def unpack(self, type, buf, conversion=1):
        if(type == 'd'):
            value = struct.unpack('d', buf[0:8])[0]
            #print(conversion,value)
            value = conversion*value
            #print(conversion,value)
        elif(type == 't'):
            value = buf.decode('ascii')
        elif(type == 'e') or (type == 'i'):                    
            value = struct.unpack('I',buf[0:4])[0]
        else:
            value = buf
        
        return value
            
if __name__ == '__main__':
    lst = HmiProtocol()
    frame = lst.setValue(4004, 'hello', 't')    
    print(lst)
    print(frame)
