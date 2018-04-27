from cffi import FFI
import time,sys
#import numpy as np
#from .comm_drv import CommDriver

ffi = FFI()
ffi.cdef(
    r'''
    bool open_rcb(void);
    void close_rcb(void);
    bool rcb_write(unsigned int dwOffset, unsigned int data);
    int rcb_send(unsigned char *msg, int msgLen);
    bool rcb_read(unsigned int dwOffset, unsigned int *data);
    int PCIe_Read(unsigned char *buf, unsigned int start, unsigned int max_size);
    unsigned int num_log_entries(void);
    unsigned int get_log_op(int idx);
    unsigned int get_log_offset(int idx);
    unsigned int get_log_val(int idx);
	''')


class PcieDriver():
    def __init__(self, send_buf_size):  
        self.__isoped = False
        self.frame = b''
        self.frames = []
        self.__lib = ffi.dlopen("libpcie_api.dll")
        #self.__send_array = np.empty((1, send_buf_size), dtype = np.uint8)
        self.__send_array = np.zeros(send_buf_size, dtype = np.uint8)
        self.__recv_array = np.zeros(send_buf_size, dtype = np.uint8)
    
    def setopt(self, *args, **kwargs):
        pass

    def open(self):
        print("PcieDriver open in")
        if not self.__isoped:
            print("PcieDrive: attempt to open_rcb")
            success = self.__lib.open_rcb()
            print("PcieDriver open: open_rcb returns ", success)
            if success == 1:
                print("open_rcb successful")
                self.__isoped = True;
            else:
                print("open_rcb failed!")
        else:
            print("PcieDriver already opened")
        time.sleep(1)
        dummy = self.__lib.rcb_write(0x18, 0)
        dummy = self.__lib.rcb_write(0x18, 0xffaa5500)
        dummy = self.__lib.rcb_write(0x18, 0)
        time.sleep(1)
        return self.__isoped
    
    def print_log(self):
        num_log_entries = self.__lib.num_log_entries()
        print("====== Here is the reg op log, number of entries =", num_log_entries)
        for cc in range(num_log_entries):
            print("OP:", self.__lib.get_log_op(cc), hex(self.__lib.get_log_offset(cc)), hex(self.__lib.get_log_val(cc)))

    def is_open(self):
        return self.__isoped
    
    def close(self):
        if self.__isoped:
            self.__lib.close_rcb()
        self.__isoped = False

    def __pad_msg(self, msg, length):
        remainder = length % 4
        if remainder > 0:
            padding_len = 4 - remainder
            padding = b'\0' * padding_len
            return msg + padding, length + padding_len 
        else:
            return msg, length
            
    def copy_to_send_buf(self, src, num_bytes):
        for cc in range(num_bytes):
            self.__send_array[cc] = src[cc]

    def send(self, msg, length):
        pa = ffi.from_buffer(memoryview(msg))
        success = self.__lib.rcb_send(pa, length) 
        if success:
            return 1
        else:
            return 0
        
    def rcb_send(self, length):
        #pa = ffi.from_buffer(msg)
        pa = ffi.from_buffer(memoryview(self.__send_array))
        result = False
        try:
            send_result = self.__lib.rcb_send(pa, length)
            if send_result == 0:
                result = True
            else:
                result = False
        except:
            result = False
        return result
    
    def copy_from_recv_buf(self, recv_msg, num_bytes):
        for cc in range(num_bytes):
            recv_msg[cc] = self.__recv_array[cc]

    def recv(self, recv_size):
        buffer = bytes(recv_size)
        pa = ffi.from_buffer(memoryview(buffer))
        r_size = self.__lib.PCIe_Read(pa, 0, recv_size)
        return r_size, buffer
        #result = np.zeros(r_size, dtype = np.uint8)
        #for cc in range(r_size):
        #    result[cc] = self.__recv_array[cc]
        #return memoryview(result.data)

    def read(self):
        good_frame = b''
        frame_len, self.frame = self.recv(self, 1500)
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
        
    def write(self, offset, buf):
        pa = ffi.from_buffer(buf)
        result = False
        try:
            if self.__lib.RCB_Write(offset, buf) > 0:
                result = True
        except:
            result = False
        return result
        
    def clear_read_buffer(self):
        pass

if __name__ == '__main__':
    app = PcieDriver(1024)
    app.open()
    print(app.is_open())
    app.close()
    sys.exit()
