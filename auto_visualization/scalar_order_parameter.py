import math

import numpy as np


def Q(n: np.ndarray):
    """
    :param n: [nx, ny].T
    -1/2 is to make this tensor traceless
    """
    return np.outer(n, n) - 0.5 * np.eye(2)


def eig2(mat):
    """
    :return: the eigen system of a zero trace, symmetric matrix [a, b; b, -a]
    """
    a, b = mat[0]
    ev = math.sqrt(a ** 2 + b ** 2)
    vec = np.array([ev + a, b])
    return ev, vec / np.linalg.norm(vec)


def s(Q: np.ndarray):
    """
    ev, vec = eig2(Q)
    return 2 * ev  # the largest positive eigenvalue. The coefficient 2 is for 2d, and 3/2 for 3d.
    """
    a, b = Q[0]
    return 2 * math.sqrt(a ** 2 + b ** 2)


def eigen_angle(Q: np.ndarray):
    ev, vec = eig2(Q)
    return math.atan2(vec[1], vec[0])


def calScalarOrderParameter(ns: np.ndarray, adjacent: np.ndarray) -> np.ndarray:
    """
    Calculate local scalar order parameter for each particle, averaging over its neighbors
    :param ns: (2, N) matrix
    :param adjacent: (N, N) symmetric matrix. NOT upper triangular!
    :return: scalar order parameter distribution for N particles.
    """
    N = ns.shape[1]
    Qs = np.array([Q(ns[:, i]) for i in range(N)])
    res = np.zeros((N,))
    for i in range(N):
        neighbors = np.where(adjacent[i, :])[0]
        subQs = [Qs[j, :, :] for j in neighbors]
        if len(subQs) <= 1:
            res[i] = 0.01
        else:
            Q_ave = sum(subQs) / len(subQs)
            res[i] = s(Q_ave)
    return res


def calGlobalScalarOrderParameter(ns: np.ndarray):
    """
    Calculate scalar order parameter as the system is uniform
    :param ns: directors: (2, N) matrix
    """
    N = ns.shape[1]
    Qs = np.array([Q(ns[:, i]) for i in range(N)])
    Q_ave = sum(Qs) / len(Qs)
    return s(Q_ave)


def calGlobalBestAngle(ns: np.ndarray):
    """
    Calculate the angle related to the order parameter as the system is uniform
    :param ns: directors: (2, N) matrix
    """
    N = ns.shape[1]
    Qs = np.array([Q(ns[:, i]) for i in range(N)])
    Q_ave = sum(Qs) / len(Qs)
    return eigen_angle(Q_ave)
