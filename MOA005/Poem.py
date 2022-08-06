import numpy as np


class Poem:

    def __init__(self):
        self.size = (16, 7)
        self.len = self.size[0] * self.size[1]
        self.idx = -1
        self.textBox = np.empty(self.size, dtype=np.unicode_)
        self.clear()
        return

    def clear(self):
        self.textBox[:] = '\u3000'
        return

    def reset(self):
        self.idx = -1
        self.clear()
        return

    def addChar(self, c):
        self.idx = self.idx + 1
        if self.idx >= self.len:
            self.idx = 0
            self.clear()
        x = self.size[0] - 1 - self.idx // self.size[1]
        y = self.idx % self.size[1]
        self.textBox[x][y] = c
        return

    def getString(self):
        tx = self.textBox.flatten(order='F')
        st = ""
        for i in range(0, len(tx), self.size[0]):
            line = tx[i: i + self.size[0]]
            for c in line:
                st += c
            st += "\n"
        return st
