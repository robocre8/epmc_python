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
    def __init__(self, port, baud=57600, timeOut=0.1):
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

        try:
            payload = self.ser.read(4)
            if len(payload) != 4:
                print("[EPMC SERIAL COMM]: Timeout while reading packet1")
                return False, [0.0]

            # Unpack 4 bytes as little-endian float
            (val,) = struct.unpack('<f', payload)
            return True, [val]

        except serial.SerialException as e:
            print(f"[EPMC SERIAL COMM]: Serial error — {e}")
            return False, [0.0]
        
    def read_packet2(self):
        """
        Reads 8 bytes from the serial port and converts to a float (little-endian).
        Returns (success, value-array)
        """
        try:
            payload = self.ser.read(8)
            if len(payload) != 8:
                print("[EPMC SERIAL COMM]: Timeout while reading packet2")
                return False, [0.0, 0.0]

            # Unpack 4 bytes as little-endian float
            a, b = struct.unpack('<ff', payload)
            return True, [a, b]

        except serial.SerialException as e:
            print(f"[EPMC SERIAL COMM]: Serial error — {e}")
            return False, [0.0, 0.0]
    
    def read_packet4(self):
        """
        Reads 8 bytes from the serial port and converts to a float (little-endian).
        Returns (success, value-array)
        """
        try:
            payload = self.ser.read(16)
            if len(payload) != 16:
                print("[EPMC SERIAL COMM]: Timeout while reading packet2")
                return False, [0.0, 0.0, 0.0, 0.0]

            # Unpack 4 bytes as little-endian float
            a, b, c, d = struct.unpack('<ffff', payload)
            return True, [a, b, c, d]

        except serial.SerialException as e:
            print(f"[EPMC SERIAL COMM]: Serial error — {e}")
            return False, [0.0, 0.0, 0.0, 0.0]
        
    
    #---------------------------------------------------------------------

    def write_data1(self, cmd, pos, val):
        payload = struct.pack('<Bf', pos, val)
        self.send_packet_with_payload(cmd, payload)
        success, val = self.read_packet1()
        return success, val

    def read_data1(self, cmd, pos):
        payload = struct.pack('<Bf', pos, 0.0)  # big-endian
        self.send_packet_with_payload(cmd, payload)
        success, val = self.read_packet1()
        return success, val
    
    def write_data2(self, cmd, a, b):
        payload = struct.pack('<ff', a,b) 
        self.send_packet_with_payload(cmd, payload)

    def read_data2(self, cmd):
        self.send_packet_without_payload(cmd)
        success, val = self.read_packet2()
        return success, val

    def write_data4(self, cmd, a, b, c, d):
        payload = struct.pack('<ffff', a,b,c,d) 
        self.send_packet_with_payload(cmd, payload)

    def read_data4(self, cmd):
        self.send_packet_without_payload(cmd)
        success, val = self.read_packet4()
        return success, val
        
    #---------------------------------------------------------------------

    def writeSpeed(self, v0, v1):
        self.write_data2(WRITE_VEL, v0, v1)
    
    def writePWM(self, v0, v1):
        self.write_data2(WRITE_PWM, v0, v1)
    
    def readPos(self):
        success, pos_arr = self.read_data2(READ_POS)
        return success, pos_arr
    
    def readVel(self):
        success, vel_arr = self.read_data2(READ_VEL)
        return success, vel_arr
    
    def readUVel(self):
        success, vel_arr = self.read_data2(READ_UVEL)
        return success, vel_arr
    
    def setCmdTimeout(self, timeout):
        success, res = self.write_data1(SET_CMD_TIMEOUT, 0, timeout)
        if success:
            return success, int(res[0])
        else:
            return success, 0
        
    def getCmdTimeout(self):
        success, res = self.read_data1(GET_CMD_TIMEOUT, 0)
        if success:
            return success, int(res[0])
        else:
            return success, 0
    
    def setPidMode(self, motor_no, mode):
        success, res = self.write_data1(SET_PID_MODE, motor_no, mode)
        if success:
            return success, int(res[0])
        else:
            return success, 0
    
    def getPidMode(self, motor_no):
        success, res = self.read_data1(GET_CMD_TIMEOUT, motor_no)
        if success:
            return success, int(res[0])
        else:
            return success, 0
    
    def clearDataBuffer(self):
        success, res = self.write_data1(CLEAR_DATA_BUFFER, 0, 0.0)
        if success:
            return success, int(res[0])
        else:
            return success, 0
    
    #---------------------------------------------------------------------

    def readMotorData(self):
        success, vel_arr = self.read_data4(READ_MOTOR_DATA)
        return success, vel_arr