import numpy as np
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

    def update(self, fl):
        temp = np.zeros((1, self.size, self.size, 2))
        dx = fl.shape[1] // self.size
        dy = fl.shape[0] // self.size

        fm = 0
        for y in range(fl.shape[0]):
            gy = (fl.shape[0] - 1 - y) // dy
            for x in range(fl.shape[1]):
                gx = x // dx
                temp[fm][gx][gy] = temp[fm][gx][gy] + fl[y][x]

        if np.count_nonzero(temp[..., 0]) > 0:
            norm = cv2.normalize(temp[..., 0], None, 0, 1, cv2.NORM_MINMAX)
            norm[norm < 0] = 0
            temp[..., 0] = norm
        temp[..., 1] = temp[..., 1] % 360
        temp[..., 1] = temp[..., 1] / 360

        self.counts = np.append(self.counts, temp, axis=0)
        self.counts = np.delete(self.counts, 0, axis=0)
        return

    def getMotion(self):
        return self.counts
