from math import sqrt

import matplotlib
import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import griddata

from visualization_numerical import DiskNumerical


font_size = 24


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


def _plotEnergySplit(curves: list[np.ndarray], stride=1):
    ys = []
    i = 0
    for cur in curves:
        i += 1
        if i % stride == 0:
            if len(cur) < 2: continue
            y = cur / cur[0] - 1
            ys.append(y)
    plotListOfArray(ys)


def getPhi4Phi6(disks: list[DiskNumerical]):
    p6s = list(map(lambda x: x.averageBondOrientationalOrder(6), disks))
    p4s = list(map(lambda x: x.averageSquareOrder(4), disks))
    return np.array(p4s), np.array(p6s)


def getPhi4(disks: list[DiskNumerical]):
    p4s = list(map(lambda x: x.averageSquareOrder(4), disks))
    return np.array(p4s)


def getPhi6(disks: list[DiskNumerical]):
    p6s = list(map(lambda x: x.averageBondOrientationalOrder(6), disks))
    return np.array(p6s)


def getCorrPhi4S(disks: list[DiskNumerical]):
    y = list(map(lambda x: x.CorrelationPhi4S(), disks))
    return np.array(y)


def getCorrPhi6S(disks: list[DiskNumerical]):
    y = list(map(lambda x: x.CorrelationPhi6S(), disks))
    return np.array(y)


def getEnergyCurve(disks: list[DiskNumerical]):
    return np.array(list(map(lambda x: x.energy_ref, disks)))


def getIdealDensityCurve(disks: list[DiskNumerical]):
    return np.array(list(map(lambda x: x.ideal_packing_density(), disks)))


def getDensityCurve(disks: list[DiskNumerical]):
    return np.array(list(map(lambda x: x.number_density(), disks)))


def densityUpTo(disks: list[DiskNumerical], max_ideal_density):
    xs = getDensityCurve(disks)
    if np.all(xs <= max_ideal_density):
        return xs, disks
    else:
        cut_index = np.where(xs > max_ideal_density)[0][0]
        return xs[:cut_index], disks[:cut_index]
    
    
def fractionUpTo(disks: list[DiskNumerical], max_ideal_density):
    xs = getIdealDensityCurve(disks)
    if np.all(xs <= max_ideal_density):
        return xs, disks
    else:
        cut_index = np.where(xs > max_ideal_density)[0][0]
        return xs[:cut_index], disks[:cut_index]


def getClusterSizeCurve(disks: list[DiskNumerical]):
    return np.array(list(map(lambda x: x.expectedClusterSize(), disks)))


def getAveScalarOrderCurve(disks: list[DiskNumerical]):
    return np.array(list(map(lambda x: x.aveScalarOrder(), disks)))


def getOverallScalarOrder(disks: list[DiskNumerical]):
    return np.array(list(map(lambda x: x.overallScalarOrder(), disks)))


def getScalarOrderByX(disks: list[DiskNumerical]):
    return np.array(list(map(lambda x: x.scalarOrderByX(), disks)))


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


def plotEnergySplit(disks: list[DiskNumerical], stride=1):
    _plotEnergySplit(list(map(lambda x: x.energy_curve, disks)), stride)


def plotPhi4(disk_groups: list[list[DiskNumerical]]):
    for disks in disk_groups:
        xs, disks = densityUpTo(disks, 2.5)
        p4s = getPhi4(disks)
        plt.rcParams.update({"font.size": font_size})
        plt.plot(xs, p4s)
    # legend: Gamma
    Gammas = list(map(lambda x: x[0].Gamma, disk_groups))
    plt.legend([f'Γ={round(g, 1)}' for g in Gammas])
    plt.xlabel('ρ')
    plt.title(f'Φ(4) for γ={round(disk_groups[0][0].gamma, 3)}')
    # plt.show()


def plotPhi6(disk_groups: list[list[DiskNumerical]]):
    for disks in disk_groups:
        xs, disks = densityUpTo(disks, 2.5)
        p6s = getPhi6(disks)
        plt.rcParams.update({"font.size": font_size})
        plt.plot(xs, p6s)
    # legend: Gamma
    Gammas = list(map(lambda x: x[0].Gamma, disk_groups))
    plt.legend([f'Γ={round(g, 1)}' for g in Gammas])
    plt.xlabel('ρ')
    plt.title(f'Φ(6) for γ={round(disk_groups[0][0].gamma, 3)}')
    # plt.show()


def plotPhi4Phi6(disks: list[DiskNumerical]):
    p4s, p6s = getPhi4Phi6(disks)
    xs = getIdealDensityCurve(disks)
    # plt.rcParams.update({"font.size": 22})
    plt.plot(xs, p4s, xs, p6s)
    plt.legend(['Phi 4', 'Phi 6'])
    plt.xlabel('ρ')
    # plt.show()


def plotScalarOrderAndMeanCluster(disks: list[DiskNumerical]):
    csc = getClusterSizeCurve(disks) / disks[0].n
    ss = getAveScalarOrderCurve(disks)
    xs = getIdealDensityCurve(disks)
    # plt.rcParams.update({"font.size": 22})
    plt.plot(xs, ss, xs, csc)
    plt.legend(['scalar order parameter', 'expected cluster size'])
    plt.xlabel('ρ')
    # plt.show()


def plotScalarOrder(disk_groups: list[list[DiskNumerical]]):
    for disks in disk_groups:
        xs, disks = densityUpTo(disks, 2.5)
        ss = getAveScalarOrderCurve(disks)
        plt.rcParams.update({"font.size": font_size})
        plt.plot(xs, ss)
    # legend: Gamma
    Gammas = list(map(lambda x: x[0].Gamma, disk_groups))
    plt.legend([f'Γ={round(g, 1)}' for g in Gammas])
    plt.xlabel('ρ')
    plt.title(f'Scalar order parameter S for γ={round(disk_groups[0][0].gamma, 3)}')
    # plt.show()
    
    
def plotLogEnergys(disk_groups: list[list[DiskNumerical]]):
    for disks in disk_groups:
        xs, disks = densityUpTo(disks, 2.5)
        ys = np.log(getEnergyCurve(disks))
        plt.rcParams.update({"font.size": font_size})
        plt.plot(xs, ys)
    # legend: Gamma
    Gammas = list(map(lambda x: x[0].Gamma, disk_groups))
    plt.legend([f'Γ={round(g, 1)}' for g in Gammas])
    plt.xlabel('ρ')
    plt.title(f'Log energy for γ={round(disk_groups[0][0].gamma, 3)}')
    # plt.show()
    

def plotEnergys(disk_groups: list[list[DiskNumerical]]):
    for disks in disk_groups:
        xs, disks = densityUpTo(disks, 2.5)
        ys = getEnergyCurve(disks)
        plt.rcParams.update({"font.size": font_size})
        plt.plot(xs, ys)
    # legend: Gamma
    Gammas = list(map(lambda x: x[0].Gamma, disk_groups))
    plt.legend([f'Γ={round(g, 1)}' for g in Gammas])
    plt.xlabel('ρ')
    plt.title(f'Log energy for γ={round(disk_groups[0][0].gamma, 3)}')
    # plt.show()


def plotMeanCluster(disk_groups: list[list[DiskNumerical]]):
    for disks in disk_groups:
        xs, disks = densityUpTo(disks, 2.5)
        csc = getClusterSizeCurve(disks) / disks[0].n
        plt.rcParams.update({"font.size": font_size})
        plt.plot(xs, csc)
    # legend: Gamma
    Gammas = list(map(lambda x: x[0].Gamma, disk_groups))
    plt.legend([f'Γ={round(g, 1)}' for g in Gammas])
    plt.xlabel('ρ')
    plt.title(f'Normalized cluster size C for γ={round(disk_groups[0][0].gamma, 3)}')
    # plt.show()


def plotOverallScalarAndBestAngle(disks: list[DiskNumerical]):
    ovs = getOverallScalarOrder(disks)
    ov_angle = getOverallBestAngle(disks)
    xs = getIdealDensityCurve(disks)
    # plt.rcParams.update({"font.size": 22})
    plt.plot(xs, ovs, xs, ov_angle)
    plt.legend(['scalar order parameter of system', 'angle of system'])
    plt.xlabel('ρ')
    # plt.show()


def imshowAngleDist(disks: list[DiskNumerical]):
    aspect = 4
    mat = getAngleDist(disks)
    xs = getIdealDensityCurve(disks)
    interp = bitmapTransformation(mat, xs, aspect)
    plt.imshow(interp, cmap='Reds', interpolation='none',
               extent=[np.min(xs), np.max(xs), 0, interp.shape[0]])
    plt.gca().set_aspect((np.max(xs) - np.min(xs)) / interp.shape[1])
    plt.xlabel('ρ')
    plt.ylabel('angle (degree)')
    # plt.show()


def plotCorrPhi4S(disk_groups: list[list[DiskNumerical]]):
    for disks in disk_groups:
        xs, disks = densityUpTo(disks, 2.5)
        y = getCorrPhi4S(disks)
        plt.rcParams.update({"font.size": font_size})
        plt.plot(xs, y)
    # legend: Gamma
    Gammas = list(map(lambda x: x[0].Gamma, disk_groups))
    plt.legend([f'Γ={round(g, 1)}' for g in Gammas])
    plt.xlabel('ρ')
    plt.title(f'Correlation between Φ(4) and S for γ={round(disk_groups[0][0].gamma, 3)}')
    # plt.show()


def plotCorrPhi6S(disk_groups: list[list[DiskNumerical]]):
    for disks in disk_groups:
        xs, disks = densityUpTo(disks, 2.5)
        y = getCorrPhi6S(disks)
        plt.rcParams.update({"font.size": font_size})
        plt.plot(xs, y)
    # legend: Gamma
    Gammas = list(map(lambda x: x[0].Gamma, disk_groups))
    plt.legend([f'Γ={round(g, 1)}' for g in Gammas])
    plt.xlabel('ρ')
    plt.title(f'Correlation between Φ(6) and S for γ={round(disk_groups[0][0].gamma, 3)}')
    # plt.show()
