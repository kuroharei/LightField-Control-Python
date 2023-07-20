# Import the .NET class library
import clr

# Import python sys module
import sys

# Import os module
import os

# Import System.IO for saving and opening files
from System.IO import *

# Import c compatible List and String
from System import String
from System.Collections.Generic import List

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

# Create the LightField Application (true for visible)
# The 2nd parameter forces LF to load with no experiment 
auto = Automation(True, List[String]())

application = auto.LightFieldApplication
experiment = application.Experiment
file_manager = application.FileManager
data_manager = application.DataManager

experiment.Load("FSRS-Blaze")

# Check for device and inform user if one is needed
if device_found()==True:

    file_name = "SRS_data.spe"

    dataset = experiment.Capture(1000)

    file_manager.SaveFile(dataset, file_name)

    data1 = [dataset.GetFrame(0, i) for i in range(0, 1000, 2)]
    data2 = [dataset.GetFrame(0, i) for i in range(1, 1000, 2)]