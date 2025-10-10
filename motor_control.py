from epmc import EPMC
import time


motorControl = EPMC('/dev/ttyUSB0')

#wait for the EPMC to fully setup
for i in range(4):
  time.sleep(1.0)
  print(f'configuring controller: {i} sec')

motorControl.clearDataBuffer()
motorControl.writeSpeed(0.0, 0.0)
print('configuration complete')

motorControl.setCmdTimeout(5000)
timeout = motorControl.getCmdTimeout()
print("command timeout in ms: ", timeout)

lowTargetVel = -3.142 # in rad/sec
highTargetVel = 3.142 # in rad/sec

prevTime = None
sampleTime = 0.015

ctrlPrevTime = None
ctrlSampleTime = 5.0
sendHigh = True


motorControl.writeSpeed(lowTargetVel, lowTargetVel) # targetA, targetB
sendHigh = True

prevTime = time.time()
ctrlPrevTime = time.time()
while True:
  if time.time() - ctrlPrevTime > ctrlSampleTime:
    if sendHigh:
      motorControl.writeSpeed(highTargetVel, highTargetVel) # targetA, targetB
      sendHigh = False
    else:
      motorControl.writeSpeed(lowTargetVel, lowTargetVel) # targetA, targetB
      sendHigh = True
    
    ctrlPrevTime = time.time()



  if time.time() - prevTime > sampleTime:
    try:
      angPosA, angPosB = motorControl.readPos() # returns angPosA, angPosB
      angVelA, angVelB = motorControl.readVel() # returns angVelA, angVelB
      print(f"motorA_readings: [{angPosA}, {angVelA}]")
      print(f"motorB_readings: [{angPosB}, {angVelB}]")
      print("")
    except:
      pass
    
    prevTime = time.time()
  time.sleep(0.01)
