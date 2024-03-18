# This is an interface module

import matplotlib.pyplot as plt
import numpy as np

from visualization_paint import DiskPainter

figure_size = 1000


def getColorForInterval(color_map_name: str, interval: tuple):
    cmap = plt.cm.get_cmap(color_map_name)
    a = interval[0]
    b = interval[1]
    k = 1 / (b - a)

    def callCmap(x: float):
        y = k * (x - a)
        return cmap(y)

    return callCmap


def plotListOfArray(lst: list[np.ndarray]):
    cmap = getColorForInterval('cool', (0, len(lst[0])))
    for i in range(len(lst)):
        plt.plot(lst[i], color=cmap(i), alpha=0.5)


def plotEnergySplit(curves: list[np.ndarray]):
    logs = []
    for cur in curves:
        lny = np.log(cur)
        if len(lny) == 0 or np.isnan(lny[0]):
            continue
        lny -= lny[0]
        logs.append(lny)
    plotListOfArray(logs)


class Disk(DiskPainter):
    def __init__(self, json_data: dict, metadata: dict, dst_folder: str):
        super(Disk, self).__init__(json_data, metadata, dst_folder)

    def plotDiscrete(self, dots: bool):
        if dots:
            return self.plotDiscreteDots__
        else:
            return self.plotDiscrete__

    def plotContinuum(self, dots: bool):
        if dots:
            return self.plotContinuumDots__
        else:
            return self.plotContinuum__

    def plotEnergyDistribution(self, dots):
        self.plotContinuum(dots)(self.calEnergy(), 'Blues', 'e')

    def plotPsi6(self, dots):
        self.plotContinuum(dots)(self.calHexatic(6), 'Greens', '6p')

    def plotPsi5(self, dots):
        self.plotContinuum(dots)(self.calHexatic(5), 'PuRd', '5p')

    def plotPsi4(self, dots):
        self.plotContinuum(dots)(self.calHexatic(4), 'Oranges', '4p')

    def plotVoronoiNeighbors(self, dots):
        self.plotDiscrete(dots)(self.calVoronoiNeighbors(), 'v')
        
    def plotOrientationAngles(self, dots):
        self.plotContinuum(dots)(self.thetas % np.pi, 'hsv' ,'a')
        
    def plotConfigurationOnly(self):
        self.plotDiscrete(False)([0] * self.n, 'c')

'''
    def plotForceNetwork(self):
        self.plotNetwork_(self.calEnergy(), self.calForceNetwork(), 'Blues', 'Blues', 'f')
'''