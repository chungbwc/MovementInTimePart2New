import numpy as np
import math
import cv2


class Grid:

    def __init__(self, fm, sz):
        self.size = sz
        self.frames = fm
        self.counts = np.zeros((self.frames, self.size, self.size, 2))
        return

    def clear(self):
        self.counts = np.zeros((self.frames, self.size, self.size, 2))
        return

    def update(self, onodes, flows):
        temp = np.zeros((1, self.size, self.size, 2))
        if onodes.shape[0] != flows.shape[0]:
            return

        onodes2d = onodes[:, 0:2].copy()
        flows2d = flows[:, 0:2].copy()

        sum = np.absolute(onodes2d).sum(axis=0)
        if sum[0] == 0 and sum[1] == 0:
            return

        minv = onodes2d.min(axis=0)
        maxv = onodes2d.max(axis=0)
        size = maxv - minv

        if size[0] > size[1]:
            d = (size[0] - size[1]) / (2.0 * size[0])
            for i in range(onodes2d.shape[0]):
                onodes2d[i][0] = (onodes2d[i][0] - minv[0]) / size[0]
                onodes2d[i][1] = d + (onodes2d[i][1] - minv[1]) / size[0]
        else:
            d = (size[1] - size[0]) / (2.0 * size[1])
            for i in range(onodes2d.shape[0]):
                onodes2d[i][0] = d + (onodes2d[i][0] - minv[0]) / size[1]
                onodes2d[i][1] = (onodes2d[i][1] - minv[1]) / size[1]

        step = self.size - 0.0001

        fid = 0
        for i in range(onodes2d.shape[0]):
            x, y = onodes2d[i]
            y = 1.0 - y
            xid = math.floor(x * step)
            yid = math.floor(y * step)
            temp[fid][xid][yid] = temp[fid][xid][yid] + flows2d[i]

        mag, ang = cv2.cartToPolar(temp[..., 0], temp[..., 1], angleInDegrees=True)
        mag[np.isinf(mag)] = 0

        temp[..., 0] = mag
        temp[..., 1] = ang / 360

        #        for i in range(temp.shape[1]):
        #            for j in range(temp.shape[2]):
        #                x, y = temp[fid][i][j]
        #                mag = math.sqrt(x * x + y * y)
        #                ang = np.arctan2(y, x) * 180 / np.pi
        #                temp[fid][i][j] = [mag, ang]

        if np.count_nonzero(temp[..., 0]) > 0:
            norm = cv2.normalize(temp[..., 0], None, 0, 1, cv2.NORM_MINMAX)
            norm[norm < 0] = 0
            temp[..., 0] = norm

        #        tmax = temp[fid].max(axis=(0, 1))[0]
        #        tmin = temp[fid].min(axis=(0, 1))[0]
        #        trng = tmax - tmin

        #        for i in range(temp.shape[1]):
        #            for j in range(temp.shape[2]):
        #                x, y = temp[fid][i][j]
        #                temp[fid][i][j][0] = (x - tmin) / trng
        #                if y < 0:
        #                    temp[fid][i][j][1] = y + 360
        #                temp[fid][i][j][1] = temp[fid][i][j][1] / 360.0

        self.counts = np.append(self.counts, temp, axis=0)
        self.counts = np.delete(self.counts, 0, axis=0)

        return

    def getMotion(self):
        return self.counts
