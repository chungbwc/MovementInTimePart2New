import numpy as np


class Flow:

    def __init__(self, pn):
        self.pLength = pn
        self.curr = None
        self.prev = None
        self.flows = None
        self.first = True
        self.clear()

        return

    def clear(self):
        self.curr = np.zeros((self.pLength, 3))
        self.prev = self.curr.copy()
        self.flows = self.curr.copy()
        self.first = True
        return

    def update(self, nd):
        self.prev = self.curr.copy()
        for i in range(self.curr.shape[0]):
            tx = nd[i].x
            ty = nd[i].y
            tz = nd[i].z
            self.curr[i] = [tx, ty, tz]
        if self.first:
            self.first = False
            self.prev = self.curr.copy()

        for i in range(self.curr.shape[0]):
            self.flows[i] = self.curr[i] - self.prev[i]
            self.flows[i][1] = -self.flows[i][1]

        return

    def getPrev(self):
        return self.prev

    def getCurr(self):
        return self.curr

    def getFlows(self):
        return self.flows
