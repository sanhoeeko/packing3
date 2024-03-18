import numpy as np


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
