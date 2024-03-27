import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import laplace
import matplotlib.colors as mcolors


def normalize(u, v):
    nor = np.sqrt(u * u + v * v)
    return u / nor, v / nor


def move(u: np.ndarray, v: np.ndarray):
    D = 0.2
    ddu = laplace(u)
    ddv = laplace(v)
    proj = ddu * u + ddv * v
    grad_u = ddu - proj * u
    grad_v = ddv - proj * v
    u += D * grad_u
    v += D * grad_v
    return normalize(u, v)


def circularField(N):
    x = np.linspace(-1, 1, N)
    y = np.linspace(-1, 1, N)
    X, Y = np.meshgrid(x, y)
    u, v = -Y, X
    c, s = normalize(u, v)
    return 2 * c * c - 1, 2 * s * c


def circularMask(N, mask_rate):
    mask = np.zeros((N, N)).astype(bool)
    m = round(N / 2 * mask_rate)
    for i in range(N):
        for j in range(N):
            x, y = j - N // 2, i - N // 2   # ith line -> y = ...
            if x ** 2 + y ** 2 >= m ** 2:
                mask[i, j] = 1
    return mask


def ellipticField(N, gamma):
    x = np.linspace(-1, 1, N)
    y = np.linspace(-1, 1, N)
    X, Y = np.meshgrid(x, y)
    u, v = -gamma ** 2 * Y, X
    c, s = normalize(u, v)
    return 2 * c * c - 1, 2 * s * c


def ellipticMask(N, gamma, mask_rate):
    mask = np.zeros((N, N)).astype(bool)
    m = round(N / 2 * mask_rate)
    for i in range(N):
        for j in range(N):
            x, y = j - N // 2, i - N // 2   # ith line -> y = ...
            if x ** 2 + gamma ** 2 * y ** 2 >= m ** 2:
                mask[i, j] = 1
    return mask


class BoundaryCondFactory:      
    def __init__(self, fieldShape, maskShape, gamma=1):
        self.fact = lambda N, mask_rate: self.BoundaryCond(N, mask_rate, fieldShape, maskShape, gamma)
        
    def __call__(self, N, mask_rate):
        return self.fact(N, mask_rate)
        
    class BoundaryCond:
        def __init__(self, N, mask_rate, fieldShape, maskShape, gamma=1):
            self.fu, self.fv = fieldShape(N, gamma)
            self.mask = maskShape(N, gamma, mask_rate)
        
        def __call__(self, u: np.ndarray, v: np.ndarray):
            u[self.mask] = self.fu[self.mask]
            v[self.mask] = self.fv[self.mask]
            return u, v
        
        
def loadData(u, v, udata, vdata):
    u[udata != 0] = udata[udata != 0]
    v[vdata != 0] = vdata[vdata != 0]
    return u, v
        
        
def updateD(u, v, udata, vdata, boundary):
    return loadData(*boundary(*move(u, v)), udata, vdata)


def update(u, v, boundary):
    return move(*boundary(u, v))


def calEnergy(u, v, mask):
    # the energy is sub-linear convergent
    ux = np.diff(u, axis=1)[:-1, :]
    uy = np.diff(u, axis=0)[:, :-1]
    vx = np.diff(v, axis=1)[:-1, :]
    vy = np.diff(v, axis=0)[:, :-1]
    return np.sum(ux * ux + uy * uy + vx * vx + vy * vy)


def getState(N, T, udata, vdata):
    N = udata.shape[0]
    boundary = BoundaryCondFactory(circularField, circularMask)(N, 0.9)
    phi = np.random.uniform(0, 2 * np.pi, (N, N))
    U, V = np.cos(phi), np.sin(phi)
    for t in range(T):
        U, V = update(U, V, udata, vdata, boundary)
    return U, V


def div(u, v):
    ux = np.diff(u, axis=1)[:-1, :]
    vy = np.diff(v, axis=0)[:, :-1]
    return ux + vy

def curl(u, v):
    uy = np.diff(u, axis=0)[:, :-1]
    vx = np.diff(v, axis=1)[:-1, :]
    return uy - vx


def RBplot(mat: np.ndarray, cmap='RdBu', ax=None, **kwargs):
    mat_no_nan = mat[~np.isnan(mat)]
    norm = mcolors.TwoSlopeNorm(vmin=mat_no_nan.min(), vmax=mat_no_nan.max(), vcenter=0)
    if ax is None:
        plt.imshow(mat, cmap, norm=norm, **kwargs)
    else:
        im = ax.imshow(mat, cmap, norm=norm, **kwargs)
        return im


def divCurlPlot(u, v):
    fig, ax = plt.subplots(figsize=(5, 5))
    im1 = RBplot(div(u, v), cmap='seismic', ax=ax, alpha=1.0)
    im2 = RBplot(curl(u, v), cmap='PuOr', ax=ax, alpha=0.5)
    cbar1 = fig.colorbar(im1, ax=ax, shrink=0.7)
    cbar2 = fig.colorbar(im2, ax=ax, shrink=0.7)


if __name__ == '__main__':
    
    N = 200
    gammaSq = 2
    boundaryCondCircle = BoundaryCondFactory(circularField, circularMask)(N, 0.9)
    boundaryCondEllipse = BoundaryCondFactory(ellipticField, ellipticMask)(N, 0.9)
    
    phi = np.random.uniform(0, 2 * np.pi, (N, N))
    U, V = np.cos(phi), np.sin(phi)
    x, y = np.linspace(-1, 1, N), np.linspace(-1, 1, N)
    X, Y = np.meshgrid(x, y)
    energies = []
    plt.ion()
    for t in range(10000):
        plt.cla()
        U, V = update(U, V)
        Phi = np.arctan2(V, U) % np.pi
        energies.append(calEnergy(U, V, boundaryCondCircle.mask))
        plt.imshow(Phi, cmap='hsv')
        plt.pause(0.001)
