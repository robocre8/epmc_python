import serial
import struct

class EPMCSerialError(Exception):
        """Custom exception for for EPMC Comm failure"""
        pass


# Serial Protocol Command IDs -------------
START_BYTE = 0xAA
WRITE_VEL = 0x01
WRITE_PWM = 0x02
READ_POS = 0x03
READ_VEL = 0x04
READ_UVEL = 0x05
GET_MAX_VEL = 0x14
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
        """
        Reads 4 bytes from the serial port and converts to a float (little-endian).
        Returns (success, value-array)
        """
        payload = self.ser.read(4)
        if len(payload) != 4:
            print("[EPMC SERIAL ERROR]: Timeout while reading 1 values")
            raise EPMCSerialError("[EPMC SERIAL ERROR]: Timeout while reading 1 value")

        # Unpack 4 bytes as little-endian float
        (val,) = struct.unpack('<f', payload)
        return val
    
    def read_packet2(self):
        """
        Reads 8 bytes from the serial port and converts to a float (little-endian).
        Returns (success, value-array)
        """
        payload = self.ser.read(8)
        if len(payload) != 8:
            print("[EPMC SERIAL ERROR]: Timeout while reading 2 values")
            raise EPMCSerialError("[EPMC SERIAL ERROR]: Timeout while reading 2 values")

        # Unpack 4 bytes as little-endian float
        a, b = struct.unpack('<ff', payload)
        return a, b
    
    def read_packet4(self):
        """
        Reads 16 bytes from the serial port and converts to a float (little-endian).
        Returns (success, value-array)
        """
        payload = self.ser.read(16)
        if len(payload) != 16:
            print("[EPMC SERIAL ERROR]: Timeout while reading 4 values")
            raise EPMCSerialError("[EPMC SERIAL ERROR]: Timeout while reading 4 values")

        # Unpack 4 bytes as little-endian float
        a, b, c, d = struct.unpack('<ffff', payload)
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

    def read_data4(self, cmd):
        self.send_packet_without_payload(cmd)
        a, b, c, d = self.read_packet4()
        return a, b, c, d
    
    #---------------------------------------------------------------------
    def writeSpeed(self, v0, v1):
        self.write_data2(WRITE_VEL, v0, v1)
    
    def writePWM(self, pwm0, pwm1):
        self.write_data2(WRITE_PWM, pwm0, pwm1)
    
    def readPos(self):
        pos0, pos1 = self.read_data2(READ_POS)
        return round(pos0, 4), round(pos1, 4)
    
    def readVel(self):
        vel0, vel1 = self.read_data2(READ_VEL)
        return round(vel0, 4), round(vel1, 4)
    
    def readUVel(self):
        vel0, vel1 = self.read_data2(READ_UVEL)
        return round(vel0, 4), round(vel1, 4)
    
    def setCmdTimeout(self, timeout):
        res = self.write_data1(SET_CMD_TIMEOUT, 100, timeout)
        return int(res)
        
    def getCmdTimeout(self):
        timeout = self.read_data1(GET_CMD_TIMEOUT, 100)
        return int(timeout)
    
    def setPidMode(self, mode):
        res = self.write_data1(SET_PID_MODE, 100, mode)
        res = True if int(res) == 1 else False
        return res
    
    def getPidMode(self):
        mode = self.read_data1(GET_CMD_TIMEOUT, 100)
        return int(mode)
    
    def clearDataBuffer(self):
        res = self.write_data1(CLEAR_DATA_BUFFER, 100, 0.0)
        res = True if int(res) == 1 else False
        return res
    
    #---------------------------------------------------------------------

    def readMotorData(self):
        pos0, pos1, vel0, vel1 = self.read_data4(READ_MOTOR_DATA)
        return round(pos0, 4), round(pos1, 4), round(vel0, 4), round(vel1, 4)
    
    #---------------------------------------------------------------------
    
    def getMaxVel(self, motor_no):
        maxVel = self.read_data1(GET_MAX_VEL, motor_no)
        return round(maxVel, 3)