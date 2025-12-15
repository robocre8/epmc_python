from epmc import EPMC
import time

port = '/dev/ttyACM0'
# port = '/dev/ttyUSB0'
epmc = EPMC(port)

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

success = epmc.clearDataBuffer()
epmc.writeSpeed(v, v)
print('configuration complete')

epmc.setCmdTimeout(10000)
success, timeout = epmc.getCmdTimeout()
print("command timeout in ms: ", timeout)

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
      success, pos0, pos1, v0, v1 = epmc.readMotorData()

      print(f"motor0_readings: [{pos0}, {v0}]")
      print(f"motor1_readings: [{pos1}, {v1}]")
      print("")
    except:
      pass
    
    readTime = time.time()
