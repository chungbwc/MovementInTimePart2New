import cv2
import numpy as np
import math


class OpFlow:

    def __init__(self, w, h, s):
        self.prev = 0
        self.curr = 1
        self.w = w
        self.h = h
        self.scale = s
        self.frames = []
        self.first = True
        self.size = (18, 18)
        self.threshold = 5
        self.offset = ((self.w - self.size[0]) // 2, (self.h - self.size[1]) // 2)
        for i in range(2):
            self.frames.append(np.zeros((self.h, self.w), dtype=np.uint8))

        self.flows = np.zeros((self.h, self.w, 2), dtype=np.float32)
        self.flow = cv2.FarnebackOpticalFlow_create(3, 0.5, False, 5, 3, 7, 1.2, cv2.OPTFLOW_FARNEBACK_GAUSSIAN)
        return

    def update(self, f):
        small = cv2.resize(f, (self.w, self.h))
        small = cv2.cvtColor(small, cv2.COLOR_RGB2GRAY)
        self.frames[self.curr] = small.copy()

        if self.first:
            self.first = False
            self.frames[self.prev] = small.copy()

        self.calcFlow()
        self.swap()
        return

    def swap(self):
        tmp = self.curr
        self.curr = self.prev
        self.prev = tmp
        return

    def calcFlow(self):
        self.flow.calc(self.frames[self.prev], self.frames[self.curr], self.flows)
        mag, ang = cv2.cartToPolar(self.flows[..., 0], -self.flows[..., 1], angleInDegrees=True)
        mag[np.isinf(mag)] = 0
        mag[mag > self.threshold] = 0

        self.flows[..., 0] = mag
        self.flows[..., 1] = ang
        return

    def getFlow(self):
        tmp = self.flows[self.offset[1]:self.offset[1] + self.size[1],
              self.offset[0]:self.offset[0] + self.size[0], ]
        return tmp

    def getFullFlow(self):
        return self.flows
