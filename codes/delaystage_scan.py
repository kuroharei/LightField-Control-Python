from feinixsAPI import *

from LightFieldAPI import *

import numpy as np

def scan(start, end, step, com, axis, experimentName):
    delaystage = DelayStage(com, 19200, "SMC", 0xCC, True)
    delaystage.home(axis)
    experiment = Experiment(experimentName)
    for pos in np.arange(start, end, step):
        delaystage.moveto(axis, pos)
        experiment.get_frame(str(pos)+"nm")

if __name__ == "__main__":
    scan()