from feinixsAPI import *

from LightFieldAPI import *

import numpy as np

def scan(start, end, step, com, axis, experimentName):
    experiment = Experiment(experimentName)
    delaystage = DelayStage(com, 19200, "SMC", 0xCC, True)
    delaystage.set_homingvel(axis, 5.0)
    delaystage.home(axis)
    delaystage.set_vel(axis, 1.0)
    for pos in np.arange(start, end, step):
        delaystage.moveto(axis, pos)
        experiment.get_frame(str(format(pos, ".4f")).replace(".", "_")+"mm")
    del delaystage
    del experiment


if __name__ == "__main__":
    # 可以按照下面注释掉的例子写指令，写好之后运行代码就可以了（Ctrl+F5或者右上角的运行键）
    # scan(0, 50, 0.1, "COM5","Y", "CJM")
    # scan(14, 32, 0.75, "COM12", "X", "cross")
    scan(100, 161, 0.2, "COM4", "X", "HRBBSFGVS-ProEM")


#        experiment.get_frame(str(format(pos, ".4f")).replace(".", "_")+"mm")