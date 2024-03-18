from math import pi, sin, cos, sqrt

import cv2 as cv
import numpy as np
from PIL import ImageColor

color_list = ['floralWhite', 'lemonchiffon', 'wheat', 'lightsalmon', 'coral', 'crimson',
              'paleturquoise', 'blue', 'teal', 'seagreen', 'green']
my_black = (10, 10, 10)
color_num = len(color_list)

def rotMat(theta):
    c, s = np.cos(theta), np.sin(theta)
    return np.array(((c, -s), (s, c)))


def getColor(x: int):
    if x < 0:
        return my_black
    elif x >= color_num:
        x = color_num - 1
    rgb = ImageColor.getrgb(color_list[x])
    r, g, b = rgb
    return b, g, r


def BGRA2bgr(image):
    B, G, R, A = cv.split(image)
    a = A.astype(float) / 255
    recip = 1 - a
    ones = np.ones_like(B).astype(float) * 255
    b = a * B.astype(float) + recip * ones
    g = a * G.astype(float) + recip * ones
    r = a * R.astype(float) + recip * ones
    image_after = np.stack((b.astype(np.uint8),
                            g.astype(np.uint8),
                            r.astype(np.uint8)), 2)
    return image_after


def rad_to_angle_int(rad: float):
    return round(180 * rad / pi)


class ProjectiveImage:
    """
    includes a color blending
    """

    def __init__(self, size_x, size_y):
        self.mat = np.zeros((size_x, size_y, 4), dtype=int)
        self.shape = (size_x, size_y, 3)
        self.one_shape = (size_x, size_y, 1)

    def add(self, img):
        ones = np.zeros(self.one_shape, dtype=np.uint8)
        sum_img = np.sum(img, axis=2)
        ones[sum_img != 0] = 1
        projective = np.concatenate((img, ones), axis=2)
        self.mat += projective

    def toImg(self):
        bgr = self.mat[:, :, 0:3].astype(float)
        projective_coordinate = self.mat[:, :, 3].astype(float)
        proj = np.stack([projective_coordinate] * 3, axis=2)
        bgr /= proj
        bgr[proj == 0] = 255
        return bgr.astype(np.uint8)

    def circle(self, center, r, color: tuple, line_width):
        mask = np.zeros(self.shape, dtype=np.uint8)
        cv.circle(mask, center, r, color, line_width)
        self.add(mask)


class FastImage:
    def __init__(self, size_x, size_y):
        self.mat = np.full((size_x, size_y, 3), 255, dtype=np.uint8)

    @classmethod
    def fromImg(cls, img: np.ndarray):
        obj = cls(img.shape[0], img.shape[1])
        obj.mat = img
        return obj

    def circle(self, center, r, color: tuple, line_width):
        cv.circle(self.mat, center, r, color, line_width)

    def ellipse(self, triplet, a_and_b, color: tuple, line_width):
        cv.ellipse(self.mat, (triplet[0], triplet[1]), a_and_b, angle=rad_to_angle_int(triplet[2]),
                   startAngle=0, endAngle=360,
                   color=color, thickness=line_width)
        
    def sphere_chain(self, triplet:tuple, centers:np.ndarray, radius, color: tuple, line_width):
        x, y, angle = triplet
        rotation_matrix = rotMat(angle)
        rotated_centers = rotation_matrix @ centers + np.array([[x], [y]])
        
        for x, y in rotated_centers.T:
            cv.circle(self.mat, (int(x), int(y)), radius=radius + line_width, color=(0, 0, 0), thickness=line_width)
        for x, y in rotated_centers.T:
            cv.circle(self.mat, (int(x), int(y)), radius=radius, color=color, thickness=-1)

    def rod(self, r0, pos1: np.ndarray, pos2: np.ndarray, color: tuple, line_width):
        direction = pos2 - pos1
        direction /= np.linalg.norm(direction)
        p1 = pos1 + r0 * direction
        p2 = pos2 - r0 * direction
        p1 = p1.astype(int)
        p2 = p2.astype(int)
        cv.line(self.mat, p1, p2, color, line_width)
        
    def sphericalCylinder(self, center: np.ndarray, alpha, half_length, color:tuple, line_width):
        direction = np.array([cos(alpha), sin(alpha)])
        pos1 = center + half_length * direction
        pos2 = center - half_length * direction
        self.rod(0, pos1, pos2, color, line_width)

    def toImg(self):
        return self.mat
