from math import sqrt

import matplotlib.pyplot as plt
import numpy as np


class BoundaryE:
    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.aspect_ratio = a / b
        self.c2 = self.a ** 2 - self.b ** 2

    def make_first_estimate(self, x0, y0):
        a, b = self.a, self.b
        k = (a * b) / sqrt(self.b ** 2 * x0 ** 2 + self.a ** 2 * y0 ** 2)
        return k * x0, k * y0

    def inner(self, x0, y0) -> tuple[int, int]:
        if x0 == 0 and y0 == 0:
            return 0, self.b
        a, b = self.a, self.b

        def iteration(x1, y1):
            sq_delta = sqrt(
                b ** 6 * x1 ** 2 - b ** 4 * x1 ** 2 * y0 ** 2 + 2 * a ** 2 * b ** 2 * x0 * x1 * y0 * y1 + a ** 4 * (
                        a ** 2 - x0 ** 2) * y1 ** 2)
            k = 1 / (b ** 6 * x1 ** 2 + a ** 6 * y1 ** 2)
            x20 = k * (-a ** 4 * b ** 2 * x1 * y0 * y1 + a ** 6 * x0 * y1 ** 2)
            y20 = k * (b ** 6 * x1 ** 2 * y0 - a ** 2 * b ** 4 * x0 * y1 * x1)
            abs_det = abs(k * a * b * sq_delta)
            return x20 + b**2*x1*abs_det, y20 + a**2*y1*abs_det

        x1, y1 = self.make_first_estimate(x0, y0)
        x2, y2 = iteration(x1, y1)
        for i in range(3):
            x2, y2 = iteration(x1, y1)
            if max(abs(x2 - x1), abs(y2 - y1)) < 1e-2:
                return x2, y2
        # return first estimation as default value
        return x2, y2

    def outer(self, x0, y0) -> tuple[int, int]:
        a, b = self.a, self.b

        def iteration(x1, y1):
            sq_delta = sqrt(
                b ** 6 * x1 ** 2 - b ** 4 * x1 ** 2 * y1 ** 2 + 2 * a ** 2 * b ** 2 * x1 * x1 * y1 * y1 + a ** 4 * (
                        a ** 2 - x1 ** 2) * y1 ** 2)
            k = 1 / (b ** 6 * x1 ** 2 + a ** 6 * y1 ** 2)
            kx = k * a * x1
            ky = k * b * y1
            x20 = kx * (a ** 5 * y1 ** 2 - a ** 3 * b ** 2 * y1 ** 2)
            y20 = ky * (b ** 5 * x1 ** 2 - a ** 2 * b ** 3 * x1 ** 2)
            abs_det = abs(sq_delta)
            return x20 + b ** 3 * kx * abs_det, y20 + a ** 3 * ky * abs_det

        x1, y1 = self.make_first_estimate(x0, y0)
        for i in range(3):
            x2, y2 = iteration(x1, y1)
            if max(abs(x2 - x1), abs(y2 - y1)) < 1e-2:
                return x2, y2
        # return first estimation as default value
        return x2, y2

    def h(self, x0, y0):
        x0, y0 = abs(x0), abs(y0)
        a, b = self.a, self.b
        if x0 ** 2 / a ** 2 + y0 ** 2 / b ** 2 < 1:
            x1, y1 = self.inner(x0, y0)
            hh = sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)
            return hh
        else:
            x1, y1 = self.outer(x0, y0)
            hh = sqrt((x0 - x1) ** 2 + (y0 - y1) ** 2)
            return -hh


a, b = 4, 1
region = (2 * a, 2 * a)
be = BoundaryE(a, b)
xs, ys = np.arange(0, region[0], 0.01), np.arange(0, region[1], 0.01)
X, Y = np.meshgrid(xs, ys)
H = np.vectorize(be.h)(X, Y)
handle = plt.contour(X, Y, H, levels=16)
plt.clabel(handle, fontsize=10, inline=True, colors='k')
plt.xlim(0, region[0])
plt.ylim(0, region[1])
plt.gca().set_aspect(1)
plt.show()
