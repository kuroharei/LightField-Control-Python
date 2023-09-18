# Import the .NET class library
import clr, ctypes

# Import python sys module
import sys

# Import os module
import os

# numpy import
import numpy as np

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

def get_FSRS(frames, center_wavelenth, _file_name):
    
    experiment.Load("FSRS-Blaze")

    # Notifies a waiting thread that an event has occurred
    # acquireCompleted = AutoResetEvent(False)

    # Check for device and inform user if one is needed
    if device_found() == True:

        # Hook the experiment completed handler
        # experiment.ExperimentCompleted += experiment_completed    

        pixels = 1340

        experiment.SetValue(ExperimentSettings.AcquisitionFramesToStore, str(frames))
        experiment.SetValue(SpectrometerSettings.GratingCenterWavelength, str(center_wavelenth))

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

        time.sleep(15 + frames * 0.001)

        # Get image directory
        directory = experiment.GetValue(ExperimentSettings.FileNameGenerationDirectory)

        file_path = '/'.join(directory.split('\\'))
        with open(file_path + '/' + _file_name + '.csv') as f:
            wavelenth = []
            intensities = []
            intensity = []
            pixel = 0
            for line in f:
                x, y = map(float, line.split(','))
                if pixel < 1340:
                    wavelenth.append(x)
                intensity.append(y)
                pixel += 1
                if pixel % pixels == 0:
                    intensities.append(np.array(intensity))
                    intensity =[]

            ret1 = sum([intensities[i] / intensities[i + 1] - 1 for i in range(0, frames, 2)])
            ret2 = sum([intensities[i + 1] / intensities[i] - 1 for i in range(0, frames, 2)])
            ret = ret1 if sum(ret1) > sum(ret2) else ret2

            with open(file_path + '/' + _file_name + '_ret.csv', 'w') as ret_file:
                writer = csv.writer(ret_file)
                writer.writerows(list(np.array([wavelenth, ret]).T))

            with open(file_path + '/' + _file_name + '_ret1.csv', 'w') as ret_file:
                writer = csv.writer(ret_file)
                writer.writerows(list(np.array([wavelenth, ret1]).T))

            with open(file_path + '/' + _file_name + '_ret2.csv', 'w') as ret_file:
                writer = csv.writer(ret_file)
                writer.writerows(list(np.array([wavelenth, ret2]).T))
            

if __name__ == "__main__":

    # get_FSRS(frames=1000, center_wavelenth=630, _file_name=("FSRS-"+"SP"))

    for i in range(430, 671, 10):
        get_FSRS(frames=2000, center_wavelenth=i, _file_name=("FSRS-" +"230901-"+"2000Frames-"+ str(i) + "nm"))
        print(str(i) + "nm, Experiment Completed")