from feinixsAPI import *

from LightFieldAPI import *

import numpy as np

def scan(start, end, step, com, axis, experimentName):
    experiment = Experiment(experimentName)
    delaystage = DelayStage(com, 19200, "SMC", 0xCC, True)
    delaystage.home(axis)
    for pos in np.arange(start, end, step):
        delaystage.moveto(axis, pos)
        experiment.get_frame(str(pos)+"mm")

if __name__ == "__main__":
    # 可以按照下面注释掉的例子写指令，写好之后运行代码就可以了（Ctrl+F5或者右上角的运行键）
    # scan(0, 50, 0.1, "COM5","Y", "CJM")
    scan(14, 32, 0.75, "COM12", "X", "cross")
    # experiment = Experiment("cross")
    # for i in np.arange(14, 15, 0.15):
    #     experiment.get_frame("test"+str(i))