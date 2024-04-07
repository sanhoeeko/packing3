from functools import lru_cache
from math import pi, atan2, sqrt

import numpy as np
from scipy.interpolate import griddata
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import Delaunay
from scipy.stats import norm

from graph import Graph, getFineContactMatrix, getBriefContactMatrix
from scalar_order_parameter import calScalarOrderParameter, calGlobalScalarOrderParameter, calGlobalBestAngle

# constants
SQRT8 = sqrt(8)
dist_tol = 2e-3  # tolerance of trivial contact
Rsq = (2 - dist_tol) ** 2
force_range = np.arange(0, 5, 0.01)  # for histogram of force distribution


def cooLike(coo: coo_matrix, new_data: np.ndarray):
    return coo_matrix((new_data, (coo.row, coo.col)), shape=coo.shape, dtype=new_data.dtype)


def cooFilter(coo: coo_matrix, func):
    triplets = []
    for i, j, v in zip(coo.row, coo.col, coo.data):
        if func(v):
            triplets.append((i, j, v))
    Is, Js, Vs = list(zip(*triplets))
    return coo_matrix((Vs, (Is, Js)), shape=coo.shape)


def smooth_histogram(values, weights, bins, x_range, sigma=1):
    def gaussian(x, mu, sigma, scale):
        return scale * norm.pdf(x, mu, sigma)

    x = np.linspace(x_range[0], x_range[1], bins)
    result = np.zeros_like(x)

    for value, weight in zip(values, weights):
        result += gaussian(x, value, sigma, weight)

    return result, x


def rotMat(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.array(((c, -s), (s, c)))


def calPsi6(r, rjs: list, order):
    psi = 0
    if len(rjs) == 0: return 0
    for rj in rjs:
        vec = rj - r
        theta_ij = atan2(vec[1], vec[0])
        psi += np.exp(1j * order * theta_ij)
    return abs(psi) / len(rjs)


class ConfigurationC:
    def __init__(self, xs: np.ndarray, ys: np.ndarray, L: float):
        self.xs = xs
        self.ys = ys
        self.L = L  # the scalar radius, defined as "boundary b" in ellipse case
        self.n = len(self.xs)


class Configuration(ConfigurationC):
    def __init__(self, json_data, metadata):
        super(Configuration, self).__init__(
            np.asarray(json_data['x'], dtype=float),
            np.asarray(json_data['y'], dtype=float),
            json_data['scalar radius']
        )
        self.thetas = np.asarray(json_data['a'], dtype=float) % np.pi
        self.LaM = metadata['boundary size a']
        self.LbM = metadata['boundary size b']
        self.m = metadata['assembly number']
        self.Rm = metadata['sphere distance']
        self.Gamma = self.LaM / self.LbM
        self.La = self.Gamma * self.L
        self.Lb = self.L  # the scalar radius

    @lru_cache(maxsize=None)
    def contactMatrix(self):
        """
        Warning: may cause problems for very high density states
        """
        return getFineContactMatrix(self.xs, self.ys, self.thetas, self.m, self.Rm, 1.2)

    @lru_cache(maxsize=None)
    def sphereContactMatrix(self):
        return getBriefContactMatrix(self.xs, self.ys, 1.5)

    @lru_cache(maxsize=None)
    def toSphereHalfWay(self) -> (np.ndarray, np.ndarray):  # shape:(N, m)
        a = 1 + (self.m - 1) / 2 * self.Rm
        analog_sphere_num = round(a)
        n_start = (analog_sphere_num - 1) / 2
        ass = np.array([(2 * (-n_start + i), 0) for i in range(analog_sphere_num)]).T  # shape:(2, m)
        Us = np.array([rotMat(self.thetas[i]) for i in range(self.n)])  # shape:(N, 2, 2)
        Uass = np.einsum('ijk,kl->ijl', Us, ass)  # shape:(N, 2, m)
        Uass_X, Uass_Y = Uass.transpose(1, 0, 2)  # shape:(N, m)
        return self.xs + Uass_X.T, self.ys + Uass_Y.T  # shape:(m, N)

    @lru_cache(maxsize=None)
    def toSpheres(self) -> ConfigurationC:
        """
        convert sphere assembly to spheres
        """
        ux, uy = self.toSphereHalfWay()  # shape:(m, N)
        return ConfigurationC(ux.reshape(-1), uy.reshape(-1), self.L)

    @lru_cache(maxsize=None)
    def angleField(self):
        """
        generate a field for interpolation
        """
        X, Y = self.toSphereHalfWay()
        X, Y = X.T, Y.T  # shape:(N, m)
        m = X.shape[1]
        A = np.tile(self.thetas.reshape(-1, 1), (1, m))
        return X.reshape(-1), Y.reshape(-1), A.reshape((-1))


class DiskData(Configuration):
    def __init__(self, json_data, metadata):
        super(DiskData, self).__init__(json_data, metadata)
        self.idx = json_data['id']
        self.energy_curve = np.asarray(json_data['energy curve'])
        self.energy_ref = json_data['energy']


class DiskNumerical(DiskData):
    def __init__(self, json_data, metadata):
        super(DiskNumerical, self).__init__(json_data, metadata)

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
    def getVoronoiContactMatrix(self):
        """
        Note: The result is a symmetric coo_matrix, not upper triangular.
        """
        return self.calVoronoiGraph().toCoo()

    @lru_cache(maxsize=None)
    def calVoronoiNeighborsDistribution(self):
        return self.calVoronoiGraph().get_z_distribution()

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
    def calSquarePhase(self, order=4):
        adjacent = self.sphereContactMatrix().todense()
        adjacent += adjacent.T

        def find_nearest_n(n: int) -> np.ndarray:
            js = np.where(adjacent[i])[1]
            xjs = np.array([self.xs[j] for j in js])
            yjs = np.array([self.ys[j] for j in js])
            if len(js) <= n:
                return None
            xi, yi = self.xs[i], self.ys[i]
            distances = np.sqrt((xjs - xi) ** 2 + (yjs - yi) ** 2)
            nearest_indices = np.argsort(distances)[:4]
            x_nearest = xjs[nearest_indices]
            y_nearest = yjs[nearest_indices]
            return np.vstack((x_nearest, y_nearest)).T

        square = np.zeros((self.n,))
        for i in range(self.n):
            rs = find_nearest_n(order)
            if rs is None:
                square[i] = 0.01
            else:
                square[i] = calPsi6(np.array([self.xs[i], self.ys[i]]), list(rs), 4)
        return square

    @lru_cache(maxsize=None)
    def averageBondOrientationalOrder(self, order=6):
        return np.sum(self.calHexatic(order)) / self.n

    @lru_cache(maxsize=None)
    def averageSquareOrder(self, order=4):
        return np.sum(self.calSquarePhase(order)) / self.n

    @lru_cache(maxsize=None)
    def number_density(self):
        return self.n / (pi * self.La * self.Lb)

    @lru_cache(maxsize=None)
    def ideal_packing_density(self):
        return self.number_density() * (pi + 2 * self.Rm * (self.m - 1))
    
    @lru_cache(maxsize=None)
    def ideal_overall_scalar_coef(self):
        g = self.Gamma
        return (g**2 - 1) / g * np.arctanh(1 / g)

    @lru_cache(maxsize=None)
    def angleInterpolation(self, fold: int, sz: int):
        thetas = self.thetas % (2 * np.pi / fold)
        aa = thetas * fold  # scale to [0, 2pi]
        u, v = np.cos(aa), np.sin(aa)
        xs = np.linspace(-self.La, self.La, int(sz * self.Gamma))
        ys = np.linspace(-self.Lb, self.Lb, sz)
        X, Y = np.meshgrid(xs, ys)
        U = griddata((self.xs, self.ys), u, (X, Y), method='linear')
        V = griddata((self.xs, self.ys), v, (X, Y), method='linear')  # U, V are in 2pi space
        Phi = np.arctan2(V, U)
        return Phi / fold

    @lru_cache(maxsize=None)
    def nematicInterpolation(self, sz=1000):
        return self.angleInterpolation(2, sz)

    @lru_cache(maxsize=None)
    def D4Interpolation(self, sz=1000):
        return self.angleInterpolation(4, sz)

    @lru_cache(maxsize=None)
    def getAngleDiffMatrix(self) -> coo_matrix:
        # adjacency = self.contactMatrix()
        adjacency = self.getVoronoiContactMatrix()
        angles = np.zeros_like(adjacency.data).astype(float)
        k = 0
        A = self.thetas % np.pi
        for i, j, v in zip(adjacency.row, adjacency.col, adjacency.data):
            angles[k] = min(abs(A[i] + A[j]) % np.pi, abs(A[i] - A[j]) % np.pi)
            k += 1
        return cooLike(adjacency, angles)

    @lru_cache(maxsize=None)
    def getAngleDiffDist(self):
        angle_diff = self.getAngleDiffMatrix()
        angles = angle_diff.data
        hist, bins = np.histogram(angles, bins=24, range=(0, np.pi / 2))
        return hist / len(angles)

    @lru_cache(maxsize=None)
    def getAngleCluster(self) -> list[list]:
        adjacency_matrix = cooFilter(self.getAngleDiffMatrix(), lambda x: x < np.pi / 12).astype(bool)
        n_components, labels = connected_components(csgraph=adjacency_matrix, directed=False)  # labels: iterator
        clusters = [[] for _ in range(n_components)]
        for node_id, cluster_id in enumerate(labels):
            clusters[cluster_id].append(node_id)
        return clusters

    @lru_cache(maxsize=None)
    def angleClusterSizeDist(self) -> np.ndarray:
        clusters = self.getAngleCluster()
        lst = np.array(list(map(len, clusters)))  # sizes of each cluster
        res = np.zeros((self.n,))
        for i in lst:
            res[i + 1] += 1
        return res

    @lru_cache(maxsize=None)
    def expectedClusterSize(self):
        """
        Meaning: randomly pick up a particle, the expectation of the size of the cluster it is in.
        """
        size_dist = self.angleClusterSizeDist()
        weight = np.array(range(1, self.n + 1)) ** 2
        return np.dot(size_dist, weight) / self.n

    @lru_cache(maxsize=None)
    def scalarOrderParameter(self):
        # mat = self.contactMatrix()
        # mat = mat + mat.T + np.eye(mat.shape[0])  # including self
        mat = self.getVoronoiContactMatrix().toarray() + np.eye(self.n)
        ns = np.vstack((np.cos(self.thetas), np.sin(self.thetas)))
        ords = calScalarOrderParameter(ns, mat.astype(bool))
        return ords

    @lru_cache(maxsize=None)
    def aveScalarOrder(self):
        return np.mean(self.scalarOrderParameter())

    @lru_cache(maxsize=None)
    def overallScalarOrder(self):
        ns = np.vstack((np.cos(self.thetas), np.sin(self.thetas)))
        return calGlobalScalarOrderParameter(ns)

    @lru_cache(maxsize=None)
    def overallBestAngle(self):
        ns = np.vstack((np.cos(self.thetas), np.sin(self.thetas)))
        return calGlobalBestAngle(ns)

    @lru_cache(maxsize=None)
    def angleDist(self) -> np.ndarray:
        A = self.thetas % np.pi
        hist, _ = np.histogram(A, bins=180)
        return hist
