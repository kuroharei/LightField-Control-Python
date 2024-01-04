from feinixsAPI import *

from LightFieldAPI import *

import numpy as np

# Import the .NET class library
import clr, ctypes

# Import python sys module
import sys

# Import os module
import os

import matplotlib.pyplot as plt

import csv

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


def device_found():
    # Find connected device
    for device in experiment.ExperimentDevices:
        if device.Type == DeviceType.Camera:
            return True
     
    # If connected device is not a camera inform the user
    print("Camera not found. Please add a camera and try again.")
    return False  

# Creates a numpy array from our acquired buffer 
def convert_buffer(net_array, image_format):
    src_hndl = GCHandle.Alloc(net_array, GCHandleType.Pinned)
    try:
        src_ptr = src_hndl.AddrOfPinnedObject().ToInt64()

        # Possible data types returned from acquisition
        if (image_format==ImageDataFormat.MonochromeUnsigned16):
            buf_type = ctypes.c_ushort*len(net_array)
        elif (image_format==ImageDataFormat.MonochromeUnsigned32):
            buf_type = ctypes.c_uint*len(net_array)
        elif (image_format==ImageDataFormat.MonochromeFloating32):
            buf_type = ctypes.c_float*len(net_array)
                    
        cbuf = buf_type.from_address(src_ptr)
        resultArray = np.frombuffer(cbuf, dtype=cbuf._type_)

    # Free the handle 
    finally:        
        if src_hndl.IsAllocated: src_hndl.Free()
        
    # Make a copy of the buffer
    return np.copy(resultArray)

def experiment_completed(sender, event_args):    
    print("Experiment Completed")    
    # Sets the state of the event to signaled,
    # allowing one or more waiting threads to proceed.
    acquireCompleted.Set()

def save_file(filename):    
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

# Create the LightField Application (true for visible)
# The 2nd parameter forces LF to load with no experiment 
auto = Automation(True, List[String]())

application = auto.LightFieldApplication
experiment = application.Experiment
file_manager = application.FileManager
data_manager = application.DataManager

def get_FSRS(frames, center_wavelength, _file_name):
    
    experiment.Load("FSRS--Gain-Blaze")

    # Notifies a waiting thread that an event has occurred
    # acquireCompleted = AutoResetEvent(False)

    # Check for device and inform user if one is needed
    if device_found() == True:

        # Hook the experiment completed handler
        # experiment.ExperimentCompleted += experiment_completed    

        pixels = 1340

        experiment.SetValue(ExperimentSettings.AcquisitionFramesToStore, str(frames))
        experiment.SetValue(SpectrometerSettings.GratingCenterWavelength, str(center_wavelength))

        # try:

        #     # Pass location of saved file
        #     save_file(_file_name)

        #     # Acquire image in LightField
        #     experiment.Acquire()

        #     # Wait for acquisition to complete
        #     acquireCompleted.WaitOne()
        
        # finally:
        #     # Cleanup handler
        #     experiment.ExperimentCompleted -= experiment_completed
    
        # Pass location of saved file
        save_file(_file_name)

        # Acquire image in LightField
        experiment.Acquire()

        time.sleep(70 + frames * 0.001)

        # Get image directory
        directory = experiment.GetValue(ExperimentSettings.FileNameGenerationDirectory)

        file_path = '/'.join(directory.split('\\'))
        with open(file_path + '/' + _file_name + '.csv') as f:
            wavelength = []
            intensities = []
            intensity = []
            pixel = 0
            for line in f:
                x, y = map(float, line.split(','))
                if pixel < 1340:
                    wavelength.append(x)
                intensity.append(y)
                pixel += 1
                if pixel % pixels == 0:
                    intensities.append(np.array(intensity))
                    intensity =[]

            ret1 = sum([intensities[i] / intensities[i + 1] - 1 for i in range(0, frames, 2)]) / (frames / 2)
            ret2 = sum([intensities[i + 1] / intensities[i] - 1 for i in range(0, frames, 2)]) / (frames / 2)
            ret = ret1 if sum(ret1) > sum(ret2) else ret2

            with open(file_path + '/' + _file_name + '_ret.csv', 'w', newline='') as ret_file:
                writer = csv.writer(ret_file)
                writer.writerows(list(np.array([wavelength, ret]).T))

            with open(file_path + '/' + _file_name + '_ret1.csv', 'w', newline='') as ret_file:
                writer = csv.writer(ret_file)
                writer.writerows(list(np.array([wavelength, ret1]).T))

            with open(file_path + '/' + _file_name + '_ret2.csv', 'w', newline='') as ret_file:
                writer = csv.writer(ret_file)
                writer.writerows(list(np.array([wavelength, ret2]).T))

def scan(start, end, step, com, axis, experimentName):
    delaystage = DelayStage(com, 19200, "SMC", 0xCC, True)
    delaystage.set_homingvel(axis, 5.0)
    delaystage.home(axis)
    delaystage.set_vel(axis, 1.0)
    for pos in np.arange(start, end, step):
        delaystage.moveto(axis, pos)
        get_FSRS(frames=100000, center_wavelength=503, _file_name=("MG-240uJ-100000f-Loss-SS-" + str(format(pos, ".4f")).replace(".", "_") + "mm"))
    del delaystage
    del experiment



# if __name__ == "__main__":

    # get_FSRS(frames=2000, center_wavelength=630, _file_name=("FSRS-CYC-580mW-2000f-"+"SS"))

    # for i in range(550, 661, 15):
        # get_FSRS(frames=2000, center_wavelength=i, _file_name=("FSRS-Cyclohexene-150mW-2000f-SS-"+ str(i) + "nm"))
    #     print(str(i) + "nm, Experiment Completed")

if __name__ == "__main__":
    # 可以按照下面注释掉的例子写指令，写好之后运行代码就可以了（Ctrl+F5或者右上角的运行键）
    # scan(0, 50, 0.1, "COM5","Y", "CJM")
    # scan(14, 32, 0.75, "COM12", "X", "cross")
    scan(81, 102, 2.0, "COM4", "X", "FSRS--Gain-Blaze")
