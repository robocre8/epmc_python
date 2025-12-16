
## Easy PID Motor Controller (EPMC) Python Library
This library helps communicate with the **`Easy PID Motor Controller Module`** in your PC or microcomputer-based python projects, with the [epmc_setup_application](https://github.com/samuko-things-company/epmc_setup_application).

> you can use it in your microcomputer robotics project (e.g Raspberry Pi, PC, etc.)

A simple way to get started is simply to try out and follow the example code


## Dependencies
- you'll need to pip install the pyserial library
  ```shell
    pip3 install pyserial   //linux or mac
    pip install pyserial   //windows
  ```

## Dependencies
- you'll need to pip install the pyserial library
  > pip3 install pyserial


## How to Use the Library
- Ensure you have the **`EPMC MODULE`** interfaced with your preferred motors, setup the encoder and PID parameters with the **`epmc_setup_application`**.

- Download (by clicking on the green Code button above) or clone the repo into your PC using **`git clone`**
> [!NOTE]  
> you can use this command if you want to clone the repo:
> 
> ```git clone https://github.com/samuko-things-company/epmc_python.git```

- check the serial port the driver is connected to:
  ```shell
  ls /dev/ttyA*
  ```
  > you should see /dev/ttyACM0 or /dev/ttyACM1 and so on

- A simple way to get started is simply to try out and follow the example `motor_control.py` code.

- You can copy the **`epmc.py`** file into your python robotics project, import the library as shown in the example `motor_control.py` code, add it to your code, and start using it.


## Basic Library functions and usage

- connect to smc_driver shield module
  > epmc = EPMC()
  >
  > epmc.connect("port_name or port_path")
  >
  > epmc.clearDataBuffer() # returns bool -> success

- send target angular velocity command
  > epmc.writeSpeed(motor0_TargetVel, motor1_TargetVel)

- send PWM command
  > epmc.writePWM(motor0_PWM, motor1_PWM)

- set motor command timeout
  > epmc.setCmdTimeout(timeout_ms)

- get motor command timeout
  > epmc.getCmdTimeout() # returns tuple -> (success, motor_command_timeout_ms): bool, float

- read motors angular position
  > epmc.readPos() # returns tuple -> (success, angPos0, angPos1): bool, float, float

- read motors angular velocity
  > epmc.readVel() # returns tuple -> (success, angVel0, angVel1): bool, float, float

- read motorA maximum commandable angular velocity
  > epmc.getMaxVel(motor_no) # returns tuple -> (success, max_vel): bool, float, float
  > maxVel0 or maxVel1 based on the specified motor number