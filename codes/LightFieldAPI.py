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


class Experiment:
    def __init__(self, experiment) -> None:
        # Create the LightField Application (true for visible)
        # The 2nd parameter forces LF to load with no experiment 
        self.auto = Automation(True, List[String]())
        self.application = self.auto.LightFieldApplication
        self.experiment = self.application.Experiment
        self.acquireCompleted = AutoResetEvent(False)
        self.experiment.Load(experiment)
        self.experiment.ExperimentCompleted += self.experiment_completed
    
    def load_experiment(self, experiment):
        self.experiment.Load(experiment)
        return self.device_found()

    def device_found(self):
        # Find connected device
        for device in self.experiment.ExperimentDevices:
            if device.Type == DeviceType.Camera:
                return True
        
        # If connected device is not a camera inform the user
        print("Camera not found. Please add a camera and try again.")
        return False  

    def experiment_completed(self, sender, event_args):    
        print("Aquisition Completed")    
        # Sets the state of the event to signaled,
        # allowing one or more waiting threads to proceed.
        self.acquireCompleted.Set()

    def save_file(self, filename):    
        # Set the base file name
        self.experiment.SetValue(ExperimentSettings.FileNameGenerationBaseFileName, Path.GetFileName(filename))
        
        # Option to Increment, set to false will not increment
        self.experiment.SetValue(ExperimentSettings.FileNameGenerationAttachIncrement, False)

        # Option to add date
        self.experiment.SetValue(ExperimentSettings.FileNameGenerationAttachDate, False)

        # Option to add time
        self.experiment.SetValue(ExperimentSettings.FileNameGenerationAttachTime, False)


    def get_frame(self, file_name):

        # Check for device and inform user if one is needed
        if self.device_found() == True:
            # Pass location of saved file
            self.save_file(file_name)

            # Acquire image in LightField
            self.experiment.Acquire()

            self.acquireCompleted.WaitOne()



