#!/usr/bin/env python3

import numpy as np
import csv
from sklearn.neighbors import NearestNeighbors
from datetime import datetime

from Loader import Loader
from Writing import Writing
from Grid import Grid

csvFile = 'data/chars10x3x3.csv'
dim = 3
frames = 10
total = 0


def main():
    global total
    characters = Loader()
    writing = Writing(dim, dim)
    grid = Grid(frames, dim)
    total = characters.getCount()

    with open(csvFile, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)

        for i in range(total):
            charName = characters.getCharFile(i)[5:6]
            charXML = characters.getChar(i)
            writing.oneChar(charXML)
            oldPos, flows = writing.getCharData()
            grid.clear()
            grid.update(np.array(oldPos), np.array(flows))
            mov = grid.getmotion()
            olist = mov.flatten().tolist()
            olist.insert(0, i + 1)
            olist.insert(1, charName)
            writer.writerow(olist)

    return


def readcsv(csvf):
    arr = np.zeros([total, frames * dim * dim * 2])
    with open(csvf, newline='', encoding='utf-8') as f:
        data = list(csv.reader(f, delimiter=','))

        data_value = [data[i][2:] for i in range(0, len(data))]
        data_label = [data[i][1:2] for i in range(0, len(data))]

    start_time = datetime.now()
    char_array = np.array(data_value, dtype=np.float32)

    nbrs = NearestNeighbors(n_neighbors=1).fit(char_array)
    end_time = datetime.now()
    print('Training time {}'.format(end_time - start_time))

    size = frames * dim * dim * 2
    input_value = np.random.rand(1, size)
    start_time = datetime.now()
    distance, indices = nbrs.kneighbors(input_value)
    distance = distance[0][0]
    index = indices[0][0]
    print(data_label[index][0], distance)
    end_time = datetime.now()
    print('Prediction time {}'.format(end_time - start_time))

    return


if __name__ == '__main__':
    main()
    readcsv(csvFile)
