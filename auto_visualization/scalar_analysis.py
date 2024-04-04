import numpy as np
from matplotlib import pyplot as plt

from visualization_numerical import DiskNumerical


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
    plt.show()


def _plotEnergySplit(curves: list[np.ndarray]):
    ys = []
    for cur in curves:
        if len(cur) == 0: continue
        y = cur / cur[0] - 1
        ys.append(y)
    plotListOfArray(ys)


def getPhi4Phi6(disks: list[DiskNumerical]):
    p6s = list(map(lambda x: x.averageBondOrientationalOrder(6), disks))
    p4s = list(map(lambda x: x.averageSquareOrder(4), disks))
    return np.array(p4s), np.array(p6s)


def getEnergyCurve(disks: list[DiskNumerical]):
    return np.array(list(map(lambda x: x.energy_ref, disks)))


def getIdealDensityCurve(disks: list[DiskNumerical]):
    return np.array(list(map(lambda x: x.ideal_packing_density(), disks)))


def getClusterSizeCurve(disks: list[DiskNumerical]):
    return np.array(list(map(lambda x: x.expectedClusterSize(), disks)))


def getAveScalarOrderCurve(disks: list[DiskNumerical]):
    return np.array(list(map(lambda x: x.aveScalarOrder(), disks)))


"""
Interfaces: input list[Disk]
"""


def plotEnergySplit(disks: list[DiskNumerical]):
    _plotEnergySplit(list(map(lambda x: x.energy_curve, disks)))


def plotPhi4Phi6(disks: list[DiskNumerical]):
    p4s, p6s = getPhi4Phi6(disks)
    xs = getIdealDensityCurve(disks)
    # plt.rcParams.update({"font.size": 22})
    plt.plot(xs, p4s, xs, p6s)
    plt.legend(['Phi 4', 'Phi 6'])
    plt.xlabel('packing fraction')
    plt.show()
    
    
def plotScalarOrderAndMeanCluster(disks: list[DiskNumerical]):
    csc = getClusterSizeCurve(disks) / disks[0].n
    ss = getAveScalarOrderCurve(disks)
    xs = getIdealDensityCurve(disks)
    # plt.rcParams.update({"font.size": 22})
    plt.plot(xs, ss, xs, csc)
    plt.legend(['scalar order parameter', 'expected cluster size'])
    plt.xlabel('packing fraction')
    plt.show()
