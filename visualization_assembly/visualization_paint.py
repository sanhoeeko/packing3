from functools import lru_cache

from cmapy import cmap
from scipy.sparse import coo_matrix

from colorbar import draw_colorbar
from cv_assist import *
from visualization_numerical import DiskNumerical
import numpy as np

class SphereAssembly:
    def __init__(self, centers:list):
        self.centers = np.asarray(centers).T
        
def getSphereChain(n, sphere_dist):
    x0 = -(n - 1)/2 * sphere_dist
    return SphereAssembly([(i * sphere_dist + x0, 0) for i in range(n)])


def toTuple(x):
    lst = [int(i) for i in x]
    return tuple(lst)


def prepare_data_continuum(data: np.ndarray):
    # normalize the data
    max_value = np.max(data)
    if max_value < 0.001:
        max_value = 0.001
    min_value = np.min(data)
    data = (data - min_value) / (max_value - min_value)

    # Convert the z values to uint8 type
    u8data = (data * 255).astype(np.uint8)
    return min_value, max_value, u8data


class DiskPainter(DiskNumerical):
    def __init__(self, json_data, metadata, dst_folder: str):
        super(DiskPainter, self).__init__(json_data)
        self.L_max = metadata['initial boundary radius']
        self.dst_folder = dst_folder
        self.ass_n = metadata['assembly number']
        self.sph_dist = metadata['sphere distance']
        self.ass = getSphereChain(self.ass_n, self.sph_dist)

    @lru_cache(maxsize=None)
    def scaling_factor(self, size):
        return size / self.L_max / 2

    # cannot be cached, because input parameters include unhashable type: np.ndarray.
    def scale(self, x, size):
        return list(map(int, (x + self.L_max) * self.scaling_factor(size)))

    # cannot be cached, because input parameters include unhashable type: np.ndarray.
    def full_scale(self, x, size):
        y = (self.L_max / self.L) * x
        return list(map(int, (y + self.L_max) * self.scaling_factor(size)))

    def full_scale_f(self, x, size):
        """
        :return: return float data, instead of int.
        """
        y = (self.L_max / self.L) * x
        return (y + self.L_max) * self.scaling_factor(size)

    def plotDiscrete__(self, data, prefix: str, sz=1000):
        """
        Visualize discrete data.
        """
        sf = self.scaling_factor(sz)
        X = self.scale(self.xs, sz)
        Y = self.scale(self.ys, sz)
        A = self.thetas
        centers = self.ass.centers * sf
        r = int(sf)

        img = FastImage(sz, sz)
        img.circle((sz // 2, sz // 2), round(self.L * sf), getColor(-1), 2)

        for i in range(self.n):
            img.sphere_chain((X[i], Y[i], A[i]), centers, r, getColor(data[i]), 1)

        cv.imwrite(self.dst_folder + prefix + str(self.idx) + '.jpg', img.toImg())

    def plotContinuum__(self, data, color_map_name: str, prefix: str, sz=1000, fast_mode=True):
        """
        Visualize continuum data.
        """

        min_value, max_value, data = prepare_data_continuum(data)
        color_map = cmap(color_map_name)
        colors = cv.applyColorMap(data, color_map).reshape(-1, 3)

        sf = self.scaling_factor(sz)
        X = self.scale(self.xs, sz)
        Y = self.scale(self.ys, sz)
        A = self.thetas
        eshape = tuple(np.round(sf * self.pshape).astype(int))

        img = FastImage(sz, sz) if fast_mode else ProjectiveImage(sz, sz)
        img.circle((sz // 2, sz // 2), round(self.L * sf), getColor(-1), 2)

        if self.ptype == 'DoubleSphere':
            for i in range(self.n):
                img.double_sphere((X[i], Y[i], A[i]), eshape, toTuple(colors[i]), 1)
        elif self.ptype == 'ECP-Ellipse':
            for i in range(self.n):
                img.ellipse((X[i], Y[i], A[i]), eshape, toTuple(colors[i]), -1)
                img.ellipse((X[i], Y[i], A[i]), eshape, getColor(-1), 1)

        # reserve space for color bar
        img = img.toImg()
        bar = np.full((sz, int(sz * 0.2), 3), 255, dtype=np.uint8)
        img = np.hstack((img, bar))

        # draw color bar
        img = draw_colorbar(img, color_map, min_value, max_value)
        cv.imwrite(self.dst_folder + prefix + str(self.idx) + '.jpg', img)

    def plotDiscreteDots__(self, data, prefix: str, sz=1000):
        """
        Visualize discrete data using non-scaling dots diagram.
        """
        X = self.full_scale(self.xs, sz)
        Y = self.full_scale(self.ys, sz)
        A = self.thetas
        img = FastImage(sz, sz)
        img.circle((sz // 2, sz // 2), sz // 2, getColor(-1), 2)
        eshape = tuple(np.round(self.scaling_factor(sz) * self.pshape).astype(int))
        c = round(sqrt(eshape[0] ** 2 - eshape[1] ** 2))

        for i in range(self.n):
            img.sphericalCylinder(np.array((X[i], Y[i])), A[i], c, getColor(data[i]), eshape[1])
        cv.imwrite(self.dst_folder + prefix + str(self.idx) + '.jpg', img.toImg())

    def plotContinuumDots__(self, data, color_map_name: str, prefix: str, sz=1000, save=True):
        """
        Visualize continuum data using non-scaling dots diagram.
        """
        min_value, max_value, data = prepare_data_continuum(data)
        color_map = cmap(color_map_name)
        colors = cv.applyColorMap(data, color_map).reshape(-1, 3)

        X = self.full_scale(self.xs, sz)
        Y = self.full_scale(self.ys, sz)
        A = self.thetas
        img = FastImage(sz, sz)
        img.circle((sz // 2, sz // 2), sz // 2, getColor(-1), 2)
        eshape = tuple(np.round(self.scaling_factor(sz) * self.pshape).astype(int))
        c = round(sqrt(eshape[0] ** 2 - eshape[1] ** 2))

        for i in range(self.n):
            img.sphericalCylinder(np.array((X[i], Y[i])), A[i], c, toTuple(colors[i]), eshape[1])

        # reserve space for color bar
        img = img.toImg()
        bar = np.full((sz, int(sz * 0.2), 3), 255, dtype=np.uint8)
        img = np.hstack((img, bar))

        # draw color bar
        img = draw_colorbar(img, color_map, min_value, max_value)
        if save:
            cv.imwrite(self.dst_folder + prefix + str(self.idx) + '.jpg', img)
        else:
            # for further painting, like drawing networks
            return img

    def plotNetwork__(self, img, data, color_map_name: str, prefix: str, sz=1000):
        """
        Note that the network plot is dependent of a dot plot. So, an image input is required.
        """
        min_value, max_value, data = prepare_data_continuum(data)
        color_map = cmap(color_map_name)
        img = FastImage.fromImg(img)

        # construct sparse matrix for easier iterations
        # np.triu: return upper triangular matrix
        data_coo = coo_matrix(np.triu(data))

        if data_coo.nnz != 0:
            colors = cv.applyColorMap(data_coo.data, color_map).reshape(-1, 3)
            X = self.full_scale_f(self.xs, sz)
            Y = self.full_scale_f(self.ys, sz)
            r0 = round(self.scaling_factor(sz) * 0.6)

            cnt = 0
            for i, j in zip(data_coo.row, data_coo.col):
                pos1 = np.array((X[i], Y[i]))
                pos2 = np.array((X[j], Y[j]))
                img.rod(r0, pos1, pos2, toTuple(colors[cnt]), 4)
                cnt += 1

            # reserve space for color bar 2
            img = img.toImg()
            bar = np.full((sz, int(sz * 0.2), 3), 255, dtype=np.uint8)
            img = np.hstack((img, bar))
            # draw color bar
            img = draw_colorbar(img, color_map, min_value, max_value)
            cv.imwrite(self.dst_folder + prefix + str(self.idx) + '.jpg', img)

    def plotNetwork_(self, data_arr, data_mat, color_map_name_arr: str, color_map_name_mat: str,
                     prefix: str, sz=1000):
        img = self.plotContinuumDots__(data_arr, color_map_name_arr, None, sz, False)
        self.plotNetwork__(img, data_mat, color_map_name_mat, prefix, sz)
