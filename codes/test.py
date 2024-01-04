from LightFieldAPI import *
from ThorlabsAPI import *
import numpy as np

if __name__ == "__main__":
    
    experiment = Experiment("HRBBSFGVS-ProEM")
    VIS_rotator = Rotator("Cage", '55358884')
    SFG_rotator = Rotator("Cage", '55355234')

    SFG_rotator.moveTo(168)
    for angle in range(21, 41, 1):
        VIS_rotator.moveTo(angle)
        experiment.get_frame("VIS" + str(angle) + "degree")
    
    del experiment
    del VIS_rotator
    del SFG_rotator

