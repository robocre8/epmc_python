import serial
import struct

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
    def __init__(self):
        pass

    def connect(self, port, baud=56700, timeOut=0.1):
        self.ser = serial.Serial(port, baud, timeout=timeOut)
    
    def disconnect(self):
        if self.ser.is_open:
            self.ser.close()

    #------------------------------------------------------------------------
    def send_packet_without_payload(self, cmd, length=0):
        length = 0
        packet = bytearray([START_BYTE, cmd, length])
        checksum = sum(packet) & 0xFF
        packet.append(checksum)
        self.ser.write(packet)
        self.ser.flush()

    def send_packet_with_payload(self, cmd, payload_bytes):
        length = len(payload_bytes)
        packet = bytearray([START_BYTE, cmd, length]) + payload_bytes
        checksum = sum(packet) & 0xFF
        packet.append(checksum)
        self.ser.write(packet)
        self.ser.flush()

    def read_packet1(self):
        """
        Reads 4 bytes from the serial port and converts to a float (little-endian).
        Returns (success, value-array)
        """
        try:
            payload = self.ser.read(4)
            if len(payload) != 4:
                # print("[EPMC SERIAL ERROR]: Timeout while reading 1 values")
                return False, 0.0

            # Unpack 4 bytes as little-endian float
            (val,) = struct.unpack('<f', payload)
            return True, val
        except:
            # print("[PYSERIAL ERROR]: Read Timeout")
            return False, 0.0
    
    def read_packet2(self):
        """
        Reads 8 bytes from the serial port and converts to a float (little-endian).
        Returns (success, value-array)
        """
        try:
            payload = self.ser.read(8)
            if len(payload) != 8:
                # print("[EPMC SERIAL ERROR]: Timeout while reading 2 values")
                return False, 0.0, 0.0

            # Unpack 4 bytes as little-endian float
            a, b = struct.unpack('<ff', payload)
            return True, a, b
        except:
            # print("[PYSERIAL ERROR]: Read Timeout")
            return False, 0.0, 0.0
    
    def read_packet4(self):
        """
        Reads 16 bytes from the serial port and converts to a float (little-endian).
        Returns (success, value-array)
        """
        try:
            payload = self.ser.read(16)
            if len(payload) != 16:
                # print("[EPMC SERIAL ERROR]: Timeout while reading 4 values")
                return False, 0.0, 0.0, 0.0, 0.0

            # Unpack 4 bytes as little-endian float
            a, b, c, d = struct.unpack('<ffff', payload)
            return True, a, b, c, d
        except:
            # print("[PYSERIAL ERROR]: Read Timeout")
            return False, 0.0, 0.0, 0.0, 0.0
    
    #---------------------------------------------------------------------

    def write_data1(self, cmd, val, pos=100):
        payload = struct.pack('<Bf', pos, val)
        self.send_packet_with_payload(cmd, payload)

    def read_data1(self, cmd, pos=100):
        payload = struct.pack('<Bf', pos, 0.0)  # big-endian
        self.send_packet_with_payload(cmd, payload)
        success, val = self.read_packet1()
        return success, val
    
    def write_data2(self, cmd, a, b):
        payload = struct.pack('<ff', a, b) 
        self.send_packet_with_payload(cmd, payload)

    def read_data2(self, cmd):
        self.send_packet_without_payload(cmd, length=8)
        success, a, b = self.read_packet2()
        return success, a, b

    def read_data4(self, cmd):
        self.send_packet_without_payload(cmd, length=16)
        suceess, a, b, c, d = self.read_packet4()
        return suceess, a, b, c, d
    
    #---------------------------------------------------------------------
    def writeSpeed(self, v0, v1):
        self.write_data2(WRITE_VEL, v0, v1)
    
    def writePWM(self, pwm0, pwm1):
        self.write_data2(WRITE_PWM, pwm0, pwm1)
    
    def readPos(self):
        success, pos0, pos1 = self.read_data2(READ_POS)
        return success, round(pos0, 4), round(pos1, 4)
    
    def readVel(self):
        success, vel0, vel1 = self.read_data2(READ_VEL)
        return success, round(vel0, 4), round(vel1, 4)
    
    def readUVel(self):
        success, vel0, vel1 = self.read_data2(READ_UVEL)
        return success, round(vel0, 4), round(vel1, 4)
    
    def setCmdTimeout(self, timeout):
        self.write_data1(SET_CMD_TIMEOUT, timeout)
        
    def getCmdTimeout(self):
        success, timeout = self.read_data1(GET_CMD_TIMEOUT)
        return success, int(timeout)
    
    def setPidMode(self, mode):
        self.write_data1(SET_PID_MODE, mode)
    
    def getPidMode(self):
        success, mode = self.read_data1(GET_CMD_TIMEOUT)
        return success, int(mode)
    
    def clearDataBuffer(self):
        success, res = self.read_data1(CLEAR_DATA_BUFFER)
        return success
    
    #---------------------------------------------------------------------

    def readMotorData(self):
        success, pos0, pos1, vel0, vel1 = self.read_data4(READ_MOTOR_DATA)
        return success, round(pos0, 4), round(pos1, 4), round(vel0, 4), round(vel1, 4)
    
    #---------------------------------------------------------------------

    def getMaxVel(self, motor_no):
        success, maxVel = self.read_data1(GET_MAX_VEL, motor_no)
        return success, round(maxVel, 3)