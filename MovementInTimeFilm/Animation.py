import cv2
import numpy as np
import math
import random

from panda3d.core import *


class Animation:

    def __init__(self, sz):
        self.width = sz[0]
        self.height = sz[1]
        self.colour = (0, 0, 0, 200)
        self.backColour = (255, 255, 255, 0)
        self.frame = np.full((self.height, self.width, 4), self.backColour, np.uint8)
        self.char = []
        self.lastPt = -1
        self.currPt = -1
        self.lastSt = -1
        self.currSt = -1
        self.numStrokes = 0
        self.writing = False
        self.rot = 0
        self.rotDelta = 1
        self.marker = [0, 0, 0]
        return

    def getFrame(self):
        return self.frame

    def clearFrame(self):
        self.frame = np.full((self.height, self.width, 4), self.backColour, np.uint8)
        return

    def update(self):
        if not self.writing:
            return

        stroke = self.char[self.currSt]
        if self.currPt >= len(stroke):
            self.lastSt = self.currSt
            self.currSt = self.currSt + 1
            self.lastPt = 0
            self.currPt = 0
            if self.currSt >= self.numStrokes:
                self.writing = False
            else:
                self.drawSegment(stroke)
                self.currPt = self.currPt + 1
        else:
            self.drawSegment(stroke)
            self.currPt = self.currPt + 1

        return

    def drawSegment(self, stroke):
        factor = 12.0
        oldPt = stroke[self.lastPt][0:2]
        newPt = stroke[self.currPt][0:2]
        thickness = stroke[self.currPt][2:3][0]
        self.marker[0] = newPt[0]
        self.marker[1] = newPt[1]
        self.marker[2] = thickness
        thickness = max(math.ceil(thickness * factor), 1)
        oldPt = (math.floor(oldPt[0] * self.width), math.floor(oldPt[1] * self.height))
        newPt = (math.floor(newPt[0] * self.width), math.floor(newPt[1] * self.height))
        cv2.line(self.frame, oldPt, newPt, self.colour, thickness, cv2.LINE_AA)
        self.lastPt = self.currPt
        return

    def writeChar2d(self, ch):
        self.char = ch
        self.newChar()
        self.clearFrame()
        self.writing = True
        #        r = random.randrange(100, 250)
        #        g = random.randrange(100, 250)
        #        b = random.randrange(100, 250)
        #        self.colour = (b, g, r, 250)
        return

    def newChar(self):
        self.numStrokes = len(self.char)
        self.currSt = 0
        self.currPt = 0
        self.lastSt = self.currSt
        self.lastPt = self.currPt
        return

    def oneChar2d(self, ch):
        self.clearFrame()
        self.char = ch
        self.newChar()
        r = random.randrange(100, 250)
        b = random.randrange(100, 250)
        r = random.randrange(100, 250)
        self.colour = (b, g, r, 250)

        self.writing = True
        for s in range(self.numStrokes):
            self.lastSt = self.currSt
            self.currSt = s
            stroke = self.char[self.currSt]
            self.currPt = 0
            self.lastPt = self.currPt
            for p in range(len(stroke)):
                self.currPt = p
                self.drawSegment(stroke)

        self.writing = False
        return

    def isWriting(self):
        return self.writing

    def getRot(self):
        return self.rot

    def rotate(self):
        self.rot = self.rot + self.rotDelta
        self.rot = self.rot % 360
        return

    def getPoint(self):
        return self.marker
