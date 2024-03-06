import glob
import os


class FilmDir:

    def __init__(self, dr):
        self.films = sorted(filter(os.path.isfile, glob.glob(dr + "*")))
        for film in self.films:
            print(film)
        self.idx = -1
        return

    def nextFilm(self):
        self.idx = self.idx + 1
        if self.idx >= len(self.films):
            self.idx = 0
        name = self.films[self.idx]
        print(name.split(os.path.sep)[2])
        return name
