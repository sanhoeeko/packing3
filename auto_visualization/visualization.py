# This is an interface module

import matplotlib.pyplot as plt
import numpy as np

from visualization_numerical import ConfigurationC
from visualization_paint import DiskPainter, ScaleHelper

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
    ys = []
    for cur in curves:
        if len(cur) == 0: continue
        y = cur / cur[0] - 1
        ys.append(y)
    plotListOfArray(ys)


class Disk(DiskPainter):
    def __init__(self, json_data: dict, metadata: dict, dst_folder: str, sz=500):
        super(Disk, self).__init__(json_data, metadata, dst_folder, sz)

    @classmethod
    def fromConfigurationC(cls, cc: ConfigurationC, ref: 'DiskPainter'):
        obj = cls(None, None, ref.dst_folder, ref.sz)
        obj.xs, obj.ys, obj.L, obj.n = cc.xs, cc.ys, cc.L, cc.n
        obj.idx = ref.idx
        obj.sz, obj.height = ref.sz, ref.sz
        obj.La, obj.Lb = ref.La, ref.Lb
        obj.LaM, obj.LbM = ref.LaM, ref.LbM
        obj.helper = ScaleHelper(obj.height / obj.LbM, obj.LaM, obj.LbM)
        obj.relative_helper = ScaleHelper(obj.height / obj.Lb, obj.La, obj.Lb)
        return obj

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

    def plotScalarOrder(self, dots):
        self.plotContinuum(dots)(self.scalarOrderParameter(), 'Blues', 'e')

    def plotPsi6(self, dots):
        self.plotContinuum(dots)(self.calHexatic(6), 'Greens', '6p')

    def plotPsi6AsSpheres(self, dots):
        spheres = Disk.fromConfigurationC(self.toSpheres(), self)
        spheres.plotContinuum(dots)(spheres.calHexatic(6), 'Greens', '6ps')

    def plotPsi5(self, dots):
        self.plotContinuum(dots)(self.calSquarePhase(5), 'PuRd', '5p')

    def plotPsi4(self, dots):
        self.plotContinuum(dots)(self.calSquarePhase(4), 'Oranges', '4p')
    
    def plotPsi4AsSpheres(self, dots):
        spheres = Disk.fromConfigurationC(self.toSpheres(), self)
        spheres.plotContinuum(dots)(spheres.calSquarePhase(4), 'Oranges', '4ps')

    def plotVoronoiNeighbors(self, dots):
        self.plotDiscrete(dots)(self.calVoronoiNeighbors(), 'v')

    def plotVoronoiAsSpheres(self, dots):
        spheres = Disk.fromConfigurationC(self.toSpheres(), self)
        spheres.plotDiscrete(dots)(spheres.calVoronoiNeighbors(), 'vs')

    def plotOrientationAngles(self, dots):
        self.plotContinuumDotsNoColorBar__(self.thetas % np.pi, 'hsv', 'a')

    def plotConfigurationOnly(self, dots):
        if self.ass_n > 1:
            self.plotDiscrete(dots)([3] * self.n, 'c')
        else:
            spheres = Disk.fromConfigurationC(self.toSpheres(), self)
            spheres.plotDiscrete(dots)([3] * self.n, 'c')

    def plotD4Field(self):
        self.plotCross('d')
