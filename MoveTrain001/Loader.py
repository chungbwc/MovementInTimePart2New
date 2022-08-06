import glob
import os
import xml.etree.ElementTree
import xml.etree.ElementTree as ET


class Loader:
    def __init__(self):
        self.dirname = 'characters/'
        files = sorted(filter(os.path.isfile, glob.glob(self.dirname + '*')))
        self.files = []
        self.idx = -1
        for f in files:
            self.files.append(os.path.basename(f))
        return

    def getCount(self):
        return len(self.files)

    def getCharFile(self, i):
        return self.files[i]

    def getChar(self, i):
        fname = self.dirname + self.files[i]
        tree = ET.parse(fname)
        root = tree.getroot()
        char = []
        for st in root:
            stroke = []
            for pt in st:
                stroke.append([float(pt[0].text), float(pt[1].text), float(pt[2].text)])
            char.append(stroke)

        return char

    def getNext(self):
        self.idx = self.idx + 1
        if self.idx >= len(self.files):
            self.idx = 0

        return self.getChar(self.idx)
