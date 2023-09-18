# Import the .NET class library
import clr

# Import python sys module
import sys

# Import os module
import os

import time

# Import System.IO for saving and opening files
from System.IO import *

from System.Threading import AutoResetEvent

# Import c compatible List and String
from System import String, Array
from System.Collections.Generic import List
from System.Runtime.InteropServices import Marshal
from System.Runtime.InteropServices import GCHandle, GCHandleType

# Add needed dll references
sys.path.append(os.environ['LIGHTFIELD_ROOT'])
sys.path.append(os.environ['LIGHTFIELD_ROOT']+"\\AddInViews")
clr.AddReference('PrincetonInstruments.LightFieldViewV5')
clr.AddReference('PrincetonInstruments.LightField.AutomationV5')
clr.AddReference('PrincetonInstruments.LightFieldAddInSupportServices')

# PI imports
from PrincetonInstruments.LightField.Automation import Automation
from PrincetonInstruments.LightField.AddIns import *
from PrincetonInstruments.LightField.AddIns import *


# Write in file paths of dlls needed. 
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.DeviceManagerCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\Thorlabs.MotionControl.GenericMotorCLI.dll")
clr.AddReference("C:\\Program Files\\Thorlabs\\Kinesis\\ThorLabs.MotionControl.IntegratedStepperMotorsCLI.dll")

# Import functions from dlls. 
from Thorlabs.MotionControl.DeviceManagerCLI import *
from Thorlabs.MotionControl.GenericMotorCLI import *
from Thorlabs.MotionControl.IntegratedStepperMotorsCLI import *
from System import Decimal 


def device_found(experiment):
    # Find connected device
    for device in experiment.ExperimentDevices:
        if device.Type == DeviceType.Camera:
            return True
     
    # If connected device is not a camera inform the user
    print("Camera not found. Please add a camera and try again.")
    return False  

def experiment_completed(sender, event_args):    
    print("Experiment Completed")    
    # Sets the state of the event to signaled,
    # allowing one or more waiting threads to proceed.
    acquireCompleted.Set()

def save_file(filename, experiment):    
    # Set the base file name
    experiment.SetValue(
        ExperimentSettings.FileNameGenerationBaseFileName,
        Path.GetFileName(filename))
    
    # Option to Increment, set to false will not increment
    experiment.SetValue(
        ExperimentSettings.FileNameGenerationAttachIncrement,
        False)

    # Option to add date
    experiment.SetValue(
        ExperimentSettings.FileNameGenerationAttachDate,
        False)

    # Option to add time
    experiment.SetValue(
        ExperimentSettings.FileNameGenerationAttachTime,
        False)
    
def init_mount(serial_number):

    try:
        # Create new device
        serial_no = str(serial_number)

        DeviceManagerCLI.BuildDeviceList()

        device = CageRotator.CreateCageRotator(serial_no)
        print(DeviceManagerCLI.GetDeviceList())
        # Connect, begin polling, and enable
        device.Connect(serial_no)
        time.sleep(0.25)
        device.StartPolling(250)
        time.sleep(0.25)  # wait statements are important to allow settings to be sent to the device

        device.EnableDevice()
        time.sleep(0.25)  # Wait for device to enable

        # Get Device information
        device_info = device.GetDeviceInfo()
        print(device_info.Description)

        # Wait for Settings to Initialise
        if not device.IsSettingsInitialized():
            device.WaitForSettingsInitialized(10000)  # 10 second timeout
            assert device.IsSettingsInitialized() is True

        # Before homing or moving device, ensure the motor's configuration is loaded
        m_config = device.LoadMotorConfiguration(serial_no,
                                                DeviceConfiguration.DeviceSettingsUseOptionType.UseFileSettings)

        m_config.DeviceSettingsName = "K10CR1/M"

        m_config.UpdateCurrentConfiguration()

        device.SetSettings(device.MotorDeviceSettings, True, False)

        print("Homing Actuator")
        device.Home(60000)  # 10s timeout, blocking call

    except Exception as e:
        print(e)

    # SimulationManager.Instance.UninitializeSimulations()
    return device

def init_lightfield():
    # Create the LightField Application (true for visible)
    # The 2nd parameter forces LF to load with no experiment 
    auto = Automation(True, List[String]())


    return auto

def rotate(device, angle):
    device.MoveTo(Decimal(angle), 20000)  # 10s timeout again
    time.sleep(1)
    print(f'Device now at position {device.Position}')
    time.sleep(1)

def get_frame(auto, expe, _file_name):
    application = auto.LightFieldApplication
    experiment = application.Experiment

    experiment.Load(expe)

    # Check for device and inform user if one is needed
    if device_found(experiment) == True:
        # Pass location of saved file
        save_file(_file_name, experiment)

        # Acquire image in LightField
        experiment.Acquire()

        time.sleep(10)

def rotate_get_frame(auto, device, angle, expe, _file_name):
    application = auto.LightFieldApplication
    experiment = application.Experiment

    experiment.Load(expe)
    
    device.MoveTo(Decimal(angle), 20000)  # 10s timeout again
    time.sleep(1)
    print(f'Device now at position {device.Position}')
    time.sleep(1)

    # Check for device and inform user if one is needed
    if device_found(experiment) == True:
        # Pass location of saved file
        save_file(_file_name, experiment)

        # Acquire image in LightField
        experiment.Acquire()

        time.sleep(20)



if __name__ == "__main__":

    VIS_S_angle = 212
    VIS_P_angle = 167

    SFG_S_angle = 168
    SFG_P_angle = 123

    VIS_device = init_mount('55358884')
    SFG_device = init_mount('55355234')
    auto = init_lightfield()

    rotate(SFG_device, SFG_S_angle)
    rotate(VIS_device, VIS_S_angle)
    get_frame(auto, "HRBBSFGVS-ProEM", ("9 ITO50nm-SSP-30s"))
    
    rotate(SFG_device, SFG_P_angle)
    rotate(VIS_device, VIS_P_angle)
    get_frame(auto, "HRBBSFGVS-ProEM", ("10 ITO50nm-PPP-30s"))

    rotate(SFG_device, SFG_P_angle)
    rotate(VIS_device, VIS_S_angle)
    get_frame(auto, "HRBBSFGVS-ProEM", ("11 ITO50nm-PSP-30s"))

    rotate(SFG_device, SFG_S_angle)
    rotate(VIS_device, VIS_P_angle)
    get_frame(auto, "HRBBSFGVS-ProEM", ("12 ITO50nm-SPP-30s"))

    # rotate(SFG_device, SFG_S_angle + 22.5)
    # for angle in range(-20, 50, 3):
    #     rotate(VIS_device, VIS_S_angle + angle)
    #     get_frame(auto, "HRBBSFGVS-ProEM", ("ITO-SFG45-VIS" + str(angle) + "-IRp-30s"))
    #     time.sleep(30)

VIS_device.Disconnect()
SFG_device.Disconnect()




