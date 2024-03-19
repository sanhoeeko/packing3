from cmapy import cmap
from scipy.sparse import coo_matrix

from colorbar import draw_colorbar
from cv_assist import *
from visualization_numerical import DiskNumerical


class SphereAssembly:
    def __init__(self, centers: list):
        self.centers = np.asarray(centers).T


class ScaleHelper:
    def __init__(self, rate, LaM, LbM):
        self.rate = rate
        self.LaM, self.LbM = LaM, LbM
        self.shape = (round(LaM * rate), round(LbM * rate))
        self.shapeT2 = (round(LbM * rate * 2), round(LaM * rate * 2))

    # cannot cache: unhashable type: np.ndarray
    def scaleVector(self, x):
        return np.round(self.rate * x).astype(int)

    def scaleVector_keepFloat(self, x):
        return self.rate * x

    def scalePosition(self, x, y):
        return np.round(self.rate * (x + self.LaM)).astype(int), np.round(self.rate * (y + self.LbM)).astype(int)


def getSphereChain(n, sphere_dist):
    x0 = -(n - 1) / 2 * sphere_dist
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
    def __init__(self, json_data, metadata, dst_folder: str, sz=500):
        super(DiskPainter, self).__init__(json_data)
        self.LaM = metadata['boundary size a']
        self.LbM = metadata['boundary size b']
        self.Gamma = self.LaM / self.LbM
        self.La = self.Gamma * self.L
        self.Lb = self.L  # the scalar radius
        self.dst_folder = dst_folder
        self.ass_n = metadata['assembly number']
        self.sph_dist = metadata['sphere distance']
        self.ass = getSphereChain(self.ass_n, self.sph_dist)
        self.pshape = np.array(((self.ass_n - 1) / 2 * self.sph_dist + 1, 1))
        self.particle_c = sqrt((self.ass_n - 1) * self.sph_dist * (1 + (self.ass_n - 1) * self.sph_dist / 4))
        self.height = sz
        self.helper = ScaleHelper(self.height / self.LbM, self.LaM, self.LbM)
        self.relative_helper = ScaleHelper(self.height / self.Lb, self.La, self.Lb)

    def drawBoundary(self, img):
        img.ellipse((self.helper.shape[0], self.helper.shape[1], 0),
                    (self.helper.scaleVector(self.La), self.helper.scaleVector(self.Lb)),
                    getColor(-1), 2)

    def drawBoundaryRelative(self, img):
        img.ellipse((self.relative_helper.shape[0], self.relative_helper.shape[1], 0),
                    (self.relative_helper.scaleVector(self.La), self.relative_helper.scaleVector(self.Lb)),
                    getColor(-1), 2)

    def plotDiscrete__(self, data, prefix: str):
        """
        Visualize discrete data.
        """
        X, Y = self.helper.scalePosition(self.xs, self.ys)
        A = self.thetas
        centers = self.helper.scaleVector_keepFloat(self.ass.centers)
        r = self.helper.scaleVector(1)

        img = FastImage(*self.helper.shapeT2)
        self.drawBoundary(img)

        for i in range(self.n):
            img.sphere_chain((X[i], Y[i], A[i]), centers, r, getColor(data[i]), 1)

        cv.imwrite(self.dst_folder + prefix + str(self.idx) + '.jpg', img.toImg())

    def plotContinuum__(self, data, color_map_name: str, prefix: str, fast_mode=True):
        """
        Visualize continuum data.
        """

        min_value, max_value, data = prepare_data_continuum(data)
        color_map = cmap(color_map_name)
        colors = cv.applyColorMap(data, color_map).reshape(-1, 3)

        X, Y = self.helper.scalePosition(self.xs, self.ys)
        A = self.thetas
        centers = self.helper.scaleVector_keepFloat(self.ass)
        r = self.helper.scaleVector(1)

        img = FastImage(*self.helper.shapeT2) if fast_mode else ProjectiveImage(*self.helper.shapeT2)
        self.drawBoundary(img)

        for i in range(self.n):
            img.sphere_chain((X[i], Y[i], A[i]), centers, r, toTuple(colors[i]), 1)

        # reserve space for color bar
        szb = self.helper.shapeT2[0]
        bar = np.full((szb, int(szb * 0.2), 3), 255, dtype=np.uint8)
        img = np.hstack((img, bar))

        # draw color bar
        img = draw_colorbar(img, color_map, min_value, max_value)
        cv.imwrite(self.dst_folder + prefix + str(self.idx) + '.jpg', img)

    def plotDiscreteDots__(self, data, prefix: str):
        """
        Visualize discrete data using non-scaling dots diagram.
        """
        X, Y = self.relative_helper.scalePosition(self.xs, self.ys)
        A = self.thetas
        img = FastImage(*self.relative_helper.shapeT2)
        self.drawBoundaryRelative(img)

        for i in range(self.n):
            img.sphericalCylinder(np.array((X[i], Y[i])), A[i], self.helper.scaleVector(self.particle_c),
                                  getColor(data[i]), self.scaleVector(1))
        cv.imwrite(self.dst_folder + prefix + str(self.idx) + '.jpg', img.toImg())

    def plotContinuumDots__(self, data, color_map_name: str, prefix: str, save=True):
        """
        Visualize continuum data using non-scaling dots diagram.
        """
        min_value, max_value, data = prepare_data_continuum(data)
        color_map = cmap(color_map_name)
        colors = cv.applyColorMap(data, color_map).reshape(-1, 3)

        X, Y = self.relative_helper.scalePosition(self.xs, self.ys)
        A = self.thetas
        img = FastImage(*self.relative_helper.shapeT2)
        self.drawBoundaryRelative(img)

        for i in range(self.n):
            img.sphericalCylinder(np.array((X[i], Y[i])), A[i], self.helper.scaleVector(self.particle_c),
                                  toTuple(colors[i]), self.helper.scaleVector(1))

        # reserve space for color bar
        img = img.toImg()
        szb = self.relative_helper.shapeT2[0]
        bar = np.full((szb, int(szb * 0.2), 3), 255, dtype=np.uint8)
        img = np.hstack((img, bar))

        # draw color bar
        img = draw_colorbar(img, color_map, min_value, max_value)
        if save:
            cv.imwrite(self.dst_folder + prefix + str(self.idx) + '.jpg', img)
        else:
            # for further painting, like drawing networks
            return img
