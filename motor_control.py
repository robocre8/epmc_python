from epmc import EPMC
import time

epmc = EPMC()

# variable for communication
pos0=0.0; pos1=0.0; pos2=0.0; pos3=0.0
vel0=0.0; vel1=0.0; vel2=0.0; vel3=0.0

# [4 rev/sec, 2 rev/sec, 1 rev/sec, 0.5 rev/sec]
targetVel = [1.571, 3.142, 6.284, 12.568] 
vel = targetVel[1]
v = 0.0

readTime = None
readTimeInterval = 0.01 # 100Hz

cmdTime = None
cmdTimeInterval = 5.0

port = '/dev/ttyACM0'
# port = '/dev/ttyUSB0'

epmc.connect(port)

#wait for the EPMC to fully setup
for i in range(4):
  time.sleep(1.0)
  print(f'waiting for epmc controller: {i+1} sec')

success = epmc.clearDataBuffer()
epmc.writeSpeed(v, v)
print('configuration complete')

timeout_ms = 10000
epmc.setCmdTimeout(timeout_ms)
success, val0 = epmc.getCmdTimeout()
if success: # only update if read was successfull
  timeout_ms = val0
  print("command timeout in ms: ", timeout_ms)
else:
  print("ERROR: could not read motor command timeout")

sendHigh = True

readTime = time.time()
cmdTime = time.time()

while True:
  if time.time() - cmdTime > cmdTimeInterval:
    if sendHigh:
      # print("command high")
      v = vel
      epmc.writeSpeed(v, v)
      vel = vel*-1
      sendHigh = False
    else:
      # print("command low")
      v = 0.0
      epmc.writeSpeed(v, v)
      sendHigh = True
    
    
    cmdTime = time.time()



  if time.time() - readTime > readTimeInterval:
    try:
      # epmc.writeSpeed(v, v)
      success, val0, val1, val2, val3 = epmc.readMotorData()
      if success: # only update if read was successfull
        pos0 = val0
        pos1 = val1
        vel0 = val2
        vel1 = val3

      print(f"motor0_readings: [{pos0}, {vel0}]")
      print(f"motor1_readings: [{pos1}, {vel1}]")
      print("")
    except:
      pass
    
    readTime = time.time()
