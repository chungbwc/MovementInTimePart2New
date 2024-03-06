import glob
import os
import random
import xml.etree.ElementTree
import xml.etree.ElementTree as ET


class Loader:

    def __init__(self, dr):
        self.dirname = dr
        files = sorted(filter(os.path.isfile, glob.glob(self.dirname + '*')))
        self.files = []
        self.charName = []
        self.idx = -1
        for f in files:
            fName = os.path.basename(f)
            self.files.append(fName)
            self.charName.append(os.path.basename(f)[5:6])

        return

    def getCount(self):
        return len(self.files)

    def getCharFile(self, i):
        if 0 <= i < len(self.files):
            return self.files[i]
        else:
            return None

    def getNames(self):
        return self.charName

    def getName(self, i):
        return self.charName[i]

    def getRandomName(self):
        idx = random.randrange(0, len(self.charName))
        return self.charName[idx]

    def getNextName(self):
        self.idx = self.idx + 1
        self.idx = self.idx % len(self.charName)
        return self.charName[self.idx]

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
