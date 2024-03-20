import matplotlib.pyplot as plt
import numpy as np
from scipy.ndimage import laplace


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
    return normalize(u, v)


def circularMask(N, mask_rate):
    mask = np.zeros((N, N)).astype(bool)
    m = round(N / 2 * mask_rate)
    for i in range(N):
        for j in range(N):
            x, y = j - N // 2, i - N // 2   # ith line -> y = ...
            if x ** 2 + y ** 2 >= m ** 2:
                mask[i, j] = 1
    return mask


def ellipticField(N):
    x = np.linspace(-1, 1, N)
    y = np.linspace(-1, 1, N)
    X, Y = np.meshgrid(x, y)
    u, v = -gammaSq * Y, X
    return normalize(u, v)


def ellipticMask(N, mask_rate):
    mask = np.zeros((N, N)).astype(bool)
    m = round(N / 2 * mask_rate)
    for i in range(N):
        for j in range(N):
            x, y = j - N // 2, i - N // 2   # ith line -> y = ...
            if x ** 2 + gammaSq * y ** 2 >= m ** 2:
                mask[i, j] = 1
    return mask


class BoundaryCondFactory:      
    def __init__(self, fieldShape, maskShape):
        self.fact = lambda N, mask_rate: self.BoundaryCond(N, mask_rate, fieldShape, maskShape)
        
    def __call__(self, N, mask_rate):
        return self.fact(N, mask_rate)
        
    class BoundaryCond:
        def __init__(self, N, mask_rate, fieldShape, maskShape):
            self.fu, self.fv = fieldShape(N)
            self.mask = maskShape(N, mask_rate)
        
        def __call__(self, u: np.ndarray, v: np.ndarray):
            u[self.mask] = self.fu[self.mask]
            v[self.mask] = self.fv[self.mask]
            return u, v
        
        
def update(u, v):
    return boundaryCondCircle(*move(u, v))


def calEnergy(u, v, mask):
    # the energy is sub-linear convergent
    ux = np.diff(u, axis=1)[:-1, :]
    uy = np.diff(u, axis=0)[:, :-1]
    vx = np.diff(v, axis=1)[:-1, :]
    vy = np.diff(v, axis=0)[:, :-1]
    return np.sum(ux * ux + uy * uy + vx * vx + vy * vy)


def getState(N, T):
    phi = np.random.uniform(0, 2 * np.pi, (N, N))
    U, V = np.cos(phi), np.sin(phi)
    for t in range(T):
        U, V = update(U, V)
    return U, V


def div(u, v):
    ux = np.diff(u, axis=1)[:-1, :]
    vy = np.diff(v, axis=0)[:, :-1]
    return ux + vy

def curl(u, v):
    uy = np.diff(u, axis=0)[:, :-1]
    vx = np.diff(v, axis=1)[:-1, :]
    return uy - vx


def divCurlPlot(u, v):
    pass


N = 400
gammaSq = 2
boundaryCondCircle = BoundaryCondFactory(circularField, circularMask)(N, 0.9)
boundaryCondEllipse = BoundaryCondFactory(ellipticField, ellipticMask)(N, 0.9)

'''
if __name__ == '__main__':
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
'''

u, v = getState(N, 1000)
d = div(u, v)
c = curl(u, v)
