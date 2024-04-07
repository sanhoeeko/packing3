from math import sqrt

import matplotlib
import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import griddata

from visualization_numerical import DiskNumerical


def getColorForInterval(color_map_name: str, interval: tuple):
    cmap = matplotlib.colormaps[color_map_name]
    a = interval[0]
    b = interval[1]
    k = 1 / (b - a)

    def callCmap(x: float):
        y = k * (x - a)
        return cmap(sqrt(y))

    return callCmap


def plotListOfArray(lst: list[np.ndarray]):
    cmap = getColorForInterval('cool', (0, len(lst)))
    for i in range(len(lst)):
        plt.plot(lst[i], color=cmap(i), alpha=0.5)
    plt.show()


def _plotEnergySplit(curves: list[np.ndarray]):
    ys = []
    for cur in curves:
        if len(cur) < 2: continue
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


def getOverallScalarOrder(disks: list[DiskNumerical]):
    return np.array(list(map(lambda x: x.overallScalarOrder(), disks)))


def getOverallScalarOrderNormalized(disks: list[DiskNumerical]):
    gs = np.array(list(map(lambda x: x.ideal_overall_scalar_coef(), disks)))
    return getOverallScalarOrder(disks) / gs


def getOverallBestAngle(disks: list[DiskNumerical]):
    return np.array(list(map(lambda x: x.overallBestAngle(), disks)))


def getAngleDist(disks: list[DiskNumerical]):
    mat = np.zeros((180, len(disks)))
    for i in range(len(disks)):
        mat[:, i] = disks[i].angleDist()
    return mat


def bitmapTransformation(bitmap: np.ndarray, xs: np.ndarray, aspect_ratio_of_fig):
    assert xs.shape[0] == bitmap.shape[1]
    m = bitmap.shape[0]
    ys = np.array(range(m))
    pts = round(aspect_ratio_of_fig * m)
    X, Y = np.meshgrid(xs, ys)
    dst_x, dst_y = np.meshgrid(np.linspace(np.min(xs), np.max(xs), pts), np.arange(m - 1, 0 - 1, -1))
    return griddata((X.reshape(-1), Y.reshape(-1)), bitmap.reshape(-1), 
                    (dst_x.reshape(-1), dst_y.reshape(-1)),
                    method='cubic').reshape(dst_x.shape)


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
    # plt.show()


def plotScalarOrderAndMeanCluster(disks: list[DiskNumerical]):
    csc = getClusterSizeCurve(disks) / disks[0].n
    ss = getAveScalarOrderCurve(disks)
    xs = getIdealDensityCurve(disks)
    # plt.rcParams.update({"font.size": 22})
    plt.plot(xs, ss, xs, csc)
    plt.legend(['scalar order parameter', 'expected cluster size'])
    plt.xlabel('packing fraction')
    # plt.show()


def plotOverallScalarAndBestAngle(disks: list[DiskNumerical]):
    ovs = getOverallScalarOrder(disks)
    ov_angle = getOverallBestAngle(disks)
    xs = getIdealDensityCurve(disks)
    # plt.rcParams.update({"font.size": 22})
    plt.plot(xs, ovs, xs, ov_angle)
    plt.legend(['scalar order parameter of system', 'angle of system'])
    plt.xlabel('packing fraction')
    # plt.show()


def imshowAngleDist(disks: list[DiskNumerical]):
    aspect = 4
    mat = getAngleDist(disks)
    xs = getIdealDensityCurve(disks)
    interp = bitmapTransformation(mat, xs, aspect)
    plt.imshow(interp, cmap='Reds', interpolation='none', 
               extent=[np.min(xs), np.max(xs), 0, interp.shape[0]])
    plt.gca().set_aspect((np.max(xs) - np.min(xs)) / interp.shape[1])
    plt.xlabel('packing fraction')
    plt.ylabel('angle (degree)')
    # plt.show()
    