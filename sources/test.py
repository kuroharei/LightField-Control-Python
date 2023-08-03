import numpy as np
import matplotlib.pyplot as plt

frames = 1000
pixels = 1340

for i in range(430, 681, 10):
    with open("D:/2023/zhangli/TEST/FSRS" + str(i) + "nm_ret.csv") as f:
        wavelenth = []
        intensity = []
        for line in f:
            try:
                x, y = map(float, line.split(','))
                wavelenth.append(x)
                intensity.append(y)
            except:
                continue

        plt.plot(wavelenth, intensity, 'r')
        plt.show()