import numpy as np
import math


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
        if onodes.shape[0] != flows.shape[0]:
            return

        onodes2d = onodes[:, 0:2].copy()
        flows2d = flows[:, 0:2].copy()

        sum = np.absolute(onodes2d).sum(axis=0)
        if sum[0] == 0 and sum[1] == 0:
            return

        step = self.size - 0.0001
        npf = math.ceil(onodes2d.shape[0] / self.frames)

        self.clear()

        for i in range(onodes2d.shape[0]):
            fid = math.floor(i / npf)
            x, y = onodes2d[i]
            xid = math.floor(x * step)
            yid = math.floor(y * step)
            self.counts[fid][xid][yid] = self.counts[fid][xid][yid] + flows2d[i]

        for f in range(self.counts.shape[0]):
            for i in range(self.counts.shape[1]):
                for j in range(self.counts.shape[2]):
                    x, y = self.counts[f][i][j]
                    mag = math.sqrt(x * x + y * y)
                    ang = np.arctan2(y, x) * 180 / np.pi
                    self.counts[f][i][j] = [mag, ang]

        for f in range(self.counts.shape[0]):
            tmax = self.counts[f].max(axis=(0, 1))[0]
            tmin = self.counts[f].min(axis=(0, 1))[0]
            trng = tmax - tmin

            for i in range(self.counts.shape[1]):
                for j in range(self.counts.shape[2]):
                    x, y = self.counts[f][i][j]
                    self.counts[f][i][j][0] = (x - tmin) / trng
                    if y < 0:
                        self.counts[f][i][j][1] = y + 360
                    self.counts[f][i][j][1] = self.counts[f][i][j][1] / 360.0

        return

    def getmotion(self):
        return self.counts
