import serial
import struct


# Serial Protocol Command IDs -------------
START_BYTE = 0xAA
WRITE_VEL = 0x01
WRITE_PWM = 0x02
READ_POS = 0x03
READ_VEL = 0x04
READ_UVEL = 0x05
SET_PID_MODE = 0x15
GET_PID_MODE = 0x16
SET_CMD_TIMEOUT = 0x17
GET_CMD_TIMEOUT = 0x18
SET_I2C_ADDR = 0x19
GET_I2C_ADDR = 0x1A
RESET_PARAMS = 0x1B
READ_MOTOR_DATA = 0x2A
CLEAR_DATA_BUFFER = 0x2C
#---------------------------------------------



class EPMC:
    def __init__(self, port, baud=115200, timeOut=0.1):
        self.ser = serial.Serial(port, baud, timeout=timeOut)
    
    #------------------------------------------------------------------------
    def send_packet_without_payload(self, cmd):
        length = 0
        packet = bytearray([START_BYTE, cmd, length])
        checksum = sum(packet) & 0xFF
        packet.append(checksum)
        self.ser.write(packet)

    def send_packet_with_payload(self, cmd, payload_bytes):
        length = len(payload_bytes)
        packet = bytearray([START_BYTE, cmd, length]) + payload_bytes
        checksum = sum(packet) & 0xFF
        packet.append(checksum)
        self.ser.write(packet)

    def read_packet1(self):
        payload = self.ser.read(4)
        a = struct.unpack('<f', payload)[0]  # little-endian float
        return a
    
    def read_packet2(self):
        payload = self.ser.read(8)
        a, b = struct.unpack('<ff', payload)  # little-endian float
        return a, b

    def read_packet4(self):
        payload = self.ser.read(16)
        a, b, c, d = struct.unpack('<ffff', payload)  # little-endian float
        return a, b, c, d
    
    #---------------------------------------------------------------------

    def write_data1(self, cmd, pos, val):
        payload = struct.pack('<Bf', pos, val)
        self.send_packet_with_payload(cmd, payload)
        val = self.read_packet1()
        return val

    def read_data1(self, cmd, pos):
        payload = struct.pack('<Bf', pos, 0.0)  # big-endian
        self.send_packet_with_payload(cmd, payload)
        val = self.read_packet1()
        return val
    
    def write_data2(self, cmd, a, b):
        payload = struct.pack('<ff', a,b) 
        self.send_packet_with_payload(cmd, payload)

    def read_data2(self, cmd):
        self.send_packet_without_payload(cmd)
        a, b = self.read_packet2()
        return a, b

    def write_data4(self, cmd, a, b, c, d):
        payload = struct.pack('<ffff', a,b,c,d) 
        self.send_packet_with_payload(cmd, payload)

    def read_data4(self, cmd):
        self.send_packet_without_payload(cmd)
        a, b, c, d = self.read_packet4()
        return a, b, c, d
        
    #---------------------------------------------------------------------

    def writeSpeed(self, v0, v1):
        self.write_data2(WRITE_VEL, v0, v1)
    
    def writePWM(self, v0, v1):
        self.write_data2(WRITE_PWM, v0, v1)
    
    def readPos(self):
        pos0, pos1 = self.read_data2(READ_POS)
        return round(pos0,4), round(pos1,4)
    
    def readVel(self):
        v0, v1 = self.read_data2(READ_VEL)
        return round(v0,6), round(v1,6)
    
    def readUVel(self):
        v0, v1 = self.read_data2(READ_UVEL)
        return round(v0,6), round(v1,6)
    
    def setCmdTimeout(self, timeout):
        res = self.write_data1(SET_CMD_TIMEOUT, 0, timeout)
        return int(res)
    
    def getCmdTimeout(self):
        timeout = self.read_data1(GET_CMD_TIMEOUT, 0)
        return int(timeout)
    
    def setPidMode(self, motor_no, mode):
        res = self.write_data1(SET_PID_MODE, motor_no, mode)
        return int(res)
    
    def getPidMode(self, motor_no):
        mode = self.read_data1(GET_CMD_TIMEOUT, motor_no)
        return int(mode)
    
    def clearDataBuffer(self):
        res = self.write_data1(CLEAR_DATA_BUFFER, 0, 0.0)
        return int(res)
    
    #---------------------------------------------------------------------

    def readMotorData(self):
        pos0, pos1, v0, v1 = self.read_data4(READ_MOTOR_DATA)
        return round(pos0,4), round(pos1,4), round(v0,6), round(v1,6)