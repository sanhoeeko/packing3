from math import sin, cos

import numpy as np
from scipy.sparse import coo_matrix
from shapely.geometry import Polygon


class Graph:
    def __init__(self, points: np.ndarray):
        """
        :param points: coordinates of points, to identify what point an index refers to.
        """
        self.points = points
        self.adjacency = [[] for i in range(len(points))]
        self.zs = None

    def from_delaunay(self, triplets):
        for triangle in triplets:
            a, b, c = triangle
            self.adjacency[a].append(b)
            self.adjacency[b].append(c)
            self.adjacency[c].append(a)

    def get_z_numbers(self):
        if self.zs is None:
            self.zs = [len(adj) for adj in self.adjacency]
        return self.zs

    def get_z_distribution(self):
        zs = self.get_z_numbers()
        z_max = max(zs)
        res = np.zeros((z_max - 2,), dtype=int)
        for i in range(len(zs)):
            res[zs[i] - 3] += 1  # a particle has at least three neighbors
        return res

    def toCoo(self) -> coo_matrix:
        lens = list(map(len, self.adjacency))
        rows = np.hstack([[i] * length for i, length in enumerate(lens)])
        cols = np.hstack(self.adjacency)
        data = np.ones((len(cols),))
        return coo_matrix((data, (rows, cols)), shape=(len(self.points), len(self.points)))


def rect(a, b, x, y, theta) -> Polygon:
    """
    :param a: semi-major axis
    :param b: semi-minor axis
    """
    r0 = np.array([x, y])
    u = np.array([a * cos(theta), a * sin(theta)])
    v = np.array([-b * sin(theta), b * cos(theta)])
    return Polygon([r0 + u + v, r0 + u - v, r0 - u - v, r0 - u + v])


def outerRectType(n, R, r):
    """
    :param n: the number of particles in a chain
    :param R: distance between two particles
    :param r: tolerant distance of contact
    """
    b = r
    a = (n - 1) / 2 * R + r

    def outerRect(x, y, theta):
        return rect(a, b, x, y, theta)

    return outerRect


def getBriefContactMatrix(xs, ys, a) -> coo_matrix:
    """
    storage mode: upper triangular
    """
    xs = xs.reshape(-1, 1)
    ys = ys.reshape(-1, 1)
    Rsq = 4 * a * a
    X = xs - xs.T
    Y = ys - ys.T
    r2 = X * X + Y * Y
    mat = np.triu(r2 < Rsq).astype(bool)
    mat ^= np.eye(len(xs)).astype(bool)  # remove diagonal
    return coo_matrix(mat)


def getFineContactMatrix(xs, ys, thetas, n, R, r) -> coo_matrix:
    """
    storage mode: upper triangular + diagonal
    """
    N = len(xs)
    rectType = outerRectType(n, R, r)
    rects = np.empty((N,), dtype=Polygon)
    for i in range(N):
        rects[i] = rectType(xs[i], ys[i], thetas[i])
    mat = getBriefContactMatrix(xs, ys, (n - 1) / 2 * R + r)
    new_mat = mat.toarray().astype(bool)
    for i, j in zip(mat.row, mat.col):
        collision = rects[i].intersects(rects[j])
        if not collision:
            new_mat[i, j] = 0
    return coo_matrix(new_mat)
