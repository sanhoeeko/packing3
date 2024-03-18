from functools import lru_cache
from math import acos, sin, pi, atan2, sqrt

import numpy as np
import scipy.sparse as ssp
from scipy.spatial import Delaunay

from graph import Graph

# constants
SQRT8 = sqrt(8)
dist_tol = 2e-3  # tolerance of trivial contact
Rsq = (2 - dist_tol) ** 2
force_range = np.arange(0, 5, 0.01)  # for histogram of force distribution


def _applyFuncToSparse(func, cmat: ssp.coo_matrix) -> ssp.coo_matrix:
    res = cmat.copy()
    res.data = func(res.data)
    return res


def applyFuncToSparse(func, cmat: ssp.coo_matrix) -> np.ndarray:
    # `.todense()` returns a np.matrix object, whose star operator is matrix multiplication,
    # but not element-wise multiplication!
    return _applyFuncToSparse(func, cmat).todense().A


def calPsi6(r, rjs: list, order):
    psi = 0
    if len(rjs) == 0: return 0
    for rj in rjs:
        vec = rj - r
        theta_ij = atan2(vec[1], vec[0])
        psi += np.exp(1j * order * theta_ij)
    return abs(psi) / len(rjs)


class Configuration:
    def __init__(self, xs: np.ndarray, ys: np.ndarray, thetas:np.ndarray, L):
        self.xs = xs
        self.ys = ys
        self.thetas = thetas
        self.L = L
        self.Lsq = (1 - self.L - dist_tol) ** 2
        self.n = len(self.xs)
        self.Rij = self.getRij()
        self.Ri = self.getRi()

    @lru_cache(maxsize=None)
    def getRij(self):
        """
        :return: symmetric sparse matrix of rij
        """
        # Do not use for-loop! It is thousands of times slower!
        dx = self.xs.reshape(1, -1) - self.xs.reshape(-1, 1)
        dy = self.ys.reshape(1, -1) - self.ys.reshape(-1, 1)
        r2 = dx ** 2 + dy ** 2
        r2[r2 > Rsq] = 0
        Rij = np.sqrt(r2)
        return ssp.coo_matrix(Rij)

    @lru_cache(maxsize=None)
    def getXijYij(self):
        """
        :return: asymmetric dense matrix of xij = xi - xj, yij = yi - yj
        """
        dx = self.xs.reshape(1, -1) - self.xs.reshape(-1, 1)
        dy = self.ys.reshape(1, -1) - self.ys.reshape(-1, 1)
        r_dense = self.Rij.todense()
        dx[r_dense == 0] = 0
        dy[r_dense == 0] = 0
        return dx, dy

    @lru_cache(maxsize=None)
    def getRi(self):
        """
        :return: sparse (n x 1) matrix of ri
        """
        ri2 = self.xs ** 2 + self.ys ** 2
        ri2[ri2 < self.Lsq] = 0
        Ri = np.sqrt(ri2)
        return ssp.coo_matrix(Ri)

    @lru_cache(maxsize=None)
    def getContactNumberPP(self):
        """
        :return: particle-particle contact number
        """
        return self.Rij.nnz / 2  # remember that Rij is symmetric!

    def eachPP(self):
        """
        :return: particle-particle iterator
        """
        for i, j, v in zip(self.Rij.row, self.Rij.col, self.Rij.data):
            yield v

    def eachPW(self):
        """
        :return: particle-wall iterator
        """
        for i, v in zip(self.Ri.row, self.Ri.data):
            yield v

    def eachPP_ij(self):
        """
        :return: particle-particle iterator
        """
        for i, j, v in zip(self.Rij.row, self.Rij.col, self.Rij.data):
            if i < j:
                yield i, j, v

    def eachPW_i(self):
        """
        :return: particle-wall iterator
        """
        for i, v in zip(self.Ri.row, self.Ri.data):
            yield i, v

    @lru_cache(maxsize=None)
    def calEnergy(self):
        pass

    @lru_cache(maxsize=None)
    def totalEnergy(self):
        tot_energy = np.sum(self.calEnergy())
        energy_error = self.energy_ref - tot_energy
        print(f"total energy: {tot_energy}, error: {energy_error}")
        return tot_energy

    @lru_cache(maxsize=None)
    def calForce(self):
        pass


class DiskData(Configuration):
    def __init__(self, json_data):
        super(DiskData, self).__init__(
            np.asarray(json_data['x'], dtype=float),
            np.asarray(json_data['y'], dtype=float),
            np.asarray(json_data['a'], dtype=float),
            json_data['scalar radius']
        )
        self.idx = json_data['id']
        self.energy_curve = np.asarray(json_data['energy curve'])
        self.energy_ref = json_data['energy']
        # self.contact_ref = json_data['contact number']


class DiskNumerical(DiskData):
    def __init__(self, json_data):
        super(DiskNumerical, self).__init__(json_data)

    @lru_cache(maxsize=None)
    def calAreaDefect(self):
        def Area(r):
            theta = acos(r) * 2
            return theta / 2 - sin(theta) / 2

        area_defect = 0
        for rij in self.eachPP():
            area_defect += Area(rij / 2)
        for ri in self.eachPW():
            area_defect += Area(self.L - ri)
        return area_defect

    @lru_cache(maxsize=None)
    def calContactNumber(self):
        raise NotImplementedError

    @lru_cache(maxsize=None)
    def calVoronoiGraph(self):
        # input of Delaunay is (n_point, n_dim)
        points = np.array([self.xs, self.ys]).T
        delaunay = Delaunay(points)
        # delaunay.simplices is delaunay.vertices in old versions
        voro_graph = Graph(points)
        voro_graph.from_delaunay(delaunay.simplices)
        return voro_graph

    @lru_cache(maxsize=None)
    def calVoronoiNeighbors(self):
        return self.calVoronoiGraph().get_z_numbers()

    @lru_cache(maxsize=None)
    def calVoronoiNeighborsDistribution(self):
        return self.calVoronoiGraph().get_z_distribution()

    @lru_cache(maxsize=None)
    def calContactMatrix(self):
        raise NotImplementedError

    @lru_cache(maxsize=None)
    def calHexatic(self, order=6):
        v_graph = self.calVoronoiGraph()
        hexatic = np.zeros((self.n,))
        pos = np.hstack((self.xs.reshape(-1, 1), self.ys.reshape(-1, 1)))
        for i in range(self.n):
            r = pos[i]
            rjs = [pos[j] for j in v_graph.adjacency[i]]
            hexatic[i] = calPsi6(r, rjs, order)
        return hexatic

    @lru_cache(maxsize=None)
    def averageContactNumber(self):
        return self.calContactNumber() / self.n

    @lru_cache(maxsize=None)
    def averageBondOrientationalOrder(self, order=6):
        return np.sum(self.calHexatic(order)) / self.n

    @lru_cache(maxsize=None)
    def packing_fraction(self):
        S = self.n * pi - self.calAreaDefect()
        S0 = pi * self.L ** 2
        return S / S0

    @lru_cache(maxsize=None)
    def number_density(self):
        return self.n / (pi * self.L ** 2)
    
    # new features
    
    @lru_cache(maxsize=None)
    def calOrientationOrder(self):
        # not 'bond orientational order'
        def order(x, y, a):
            r = np.sqrt(x * x + y * y)
            ordr = (x * np.sin(a) - y * np.cos(a)) / r
            return r, ordr * ordr
        
        def average(x, y):
            bins = np.linspace(0, 1, num=6)
            indices = np.digitize(x, bins)
            averaged_y = [y[indices == i].mean() for i in range(1, len(bins))]
            return np.asarray(averaged_y)
        
        r, ordr2 = order(self.xs, self.ys, self.thetas)
        normalized_r = r / self.L  # now r in [0,1]
        y_ave = average(normalized_r, ordr2)
        return y_ave
    
    @lru_cache(maxsize=None)
    def meanOrientation(self):
        u = (np.mean(np.cos(self.thetas)),
             np.mean(np.sin(self.thetas)))
        u = np.array(u)
        return atan2(u[1], u[0]) % pi
    
    @lru_cache(maxsize=None)
    def nematicOrder(self):
        ave_theta = self.meanOrientation()
        phi = self.thetas % pi - ave_theta
        S = np.mean(3 * np.cos(phi) ** 2 - 1) * 0.5
        return S
    
    
    '''
    @lru_cache(maxsize=None)
    def calForceNetwork(self) -> np.ndarray:
        """
        :return: symmetric dense matrix
        """
        raise NotImplementedError

    @lru_cache(maxsize=None)
    def calForceDistribution(self):
        raise NotImplementedError()

    @lru_cache(maxsize=None)
    def calHessian(self):
        raise NotImplementedError()
        
    @lru_cache(maxsize=None)
    def calHessianEigenValues(self):
        """
        :return: array of sorted eigen values of the Hessian matrix
        """
        hessian = self.calHessian()
        s, j = np.linalg.eig(hessian)
        return np.sort(np.real(s))
    '''