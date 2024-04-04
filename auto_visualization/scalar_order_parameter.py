import numpy as np


def Q(n: np.ndarray):
    """
    :param n: [nx, ny].T
    -1/2 is to make this tensor traceless
    """
    return np.outer(n, n) - 0.5 * np.eye(2)


def s(Q: np.ndarray):
    ev, vecs = np.linalg.eigh(Q)
    return 2 * ev[-1]  # the largest positive eigenvalue. The coefficient 2 is for 2d, and 3/2 for 3d.


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


def calFullScalarOrderParameter(ns: np.array):
    """
    Calculate average scalar order parameter for the system
    :param ns: (2, N) matrix
    """
    N = ns.shape[1]
    Qs = np.array([Q(ns[:, i]) for i in range(N)])
    Q_ave = sum(Qs) / len(Qs)
    return s(Q_ave)
