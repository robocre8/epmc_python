from epmc import EPMC
import time

port = '/dev/ttyACM0'
# port = '/dev/ttyUSB0'
motorControl = EPMC(port)

# [4 rev/sec, 2 rev/sec, 1 rev/sec, 0.5 rev/sec]
targetVel = [1.571, 3.142, 6.284, 12.568] 
vel = targetVel[1]
v = 0.0

readTime = None
readTimeInterval = 0.01 # 100Hz

cmdTime = None
cmdTimeInterval = 5.0

#wait for the EPMC to fully setup
for i in range(4):
  time.sleep(1.0)
  print(f'waiting for epmc controller: {i+1} sec')

motorControl.clearDataBuffer()
motorControl.writeSpeed(v, v)
print('configuration complete')

motorControl.setCmdTimeout(10000)
timeout = motorControl.getCmdTimeout()
print("command timeout in ms: ", timeout)

sendHigh = True

readTime = time.time()
cmdTime = time.time()

while True:
  if time.time() - cmdTime > cmdTimeInterval:
    if sendHigh:
      # print("command high")
      # motorControl.writeSpeed(vel, vel)
      v = vel
      vel = vel*-1
      sendHigh = False
    else:
      # print("command low")
      # motorControl.writeSpeed(0.0, 0.0)
      v = 0.0
      sendHigh = True
    
    
    cmdTime = time.time()



  if time.time() - readTime > readTimeInterval:
    try:
      motorControl.writeSpeed(v, v)
      pos0, pos1, v0, v1 = motorControl.readMotorData()

      print(f"motor0_readings: [{pos0}, {v0}]")
      print(f"motor1_readings: [{pos1}, {v1}]")
      print("")
    except:
      pass
    
    readTime = time.time()
