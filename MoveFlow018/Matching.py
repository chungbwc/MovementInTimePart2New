import csv
import numpy as np
from sklearn.neighbors import NearestNeighbors


class Matching:

    def __init__(self, f, fm, sz):
        self.dataValue, self.dataLabel = self.readcsv(f)
        self.numChars = len(self.dataLabel)
        self.nbrs = self.trainData()
        return

    def readcsv(self, csvf):
        with open(csvf, newline='', encoding='utf-8') as f:
            data = list(csv.reader(f, delimiter=','))

        value = [data[i][2:] for i in range(0, len(data))]
        label = [data[i][1:2][0] for i in range(0, len(data))]
        value = np.array(value, dtype=np.float32)

        return value, label

    def trainData(self):
        nbrs = NearestNeighbors(n_neighbors=1).fit(self.dataValue)
        return nbrs

    def matchData(self, mot):
        motion = mot.flatten().reshape((1, self.dataValue.shape[1]))
        distance, index = self.nbrs.kneighbors(motion)
        distance = distance[0][0]
        index = index[0][0]
        return distance, index

    def getCharName(self, idx):
        return self.dataLabel[idx]

    def getCharMotion(self, idx):
        return self.dataValue[idx]
