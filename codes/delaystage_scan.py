from feinixsAPI import *

from LightFieldAPI import *

import numpy as np

def scan(start, end, step, com, axis, experimentName):
    delaystage = DelayStage(com, 19200, "SMC", 0xCC, True)
    delaystage.home(axis)
    experiment = Experiment(experimentName)
    for pos in np.arange(start, end, step):
        delaystage.moveto(axis, pos)
        experiment.get_frame(str(pos)+"mm")

if __name__ == "__main__":
    # 可以按照下面注释掉的例子写指令，写好之后运行代码就可以了（Ctrl+F5或者右上角的运行键）
    # scan(0, 50, 0.1, "COM5","Y", "CJM")