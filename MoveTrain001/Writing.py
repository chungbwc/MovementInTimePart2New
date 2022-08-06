import cv2
import numpy as np
import math


class Writing:

    def __init__(self, w, h):
        self.width = w
        self.height = h
        self.frame = np.full((self.height, self.width, 3), (0, 0, 255), np.uint8)
        self.char = []
        self.lastPt = -1
        self.currPt = -1
        self.lastSt = -1
        self.currSt = -1
        self.numStrokes = 0
        self.writing = False
        self.oldPos = []
        self.flows = []
        return

    def getFrame(self):
        return self.frame

    def clearFrame(self):
        self.frame = np.full((self.height, self.width, 3), (0, 0, 255), np.uint8)
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
        factor = 10.0
        oldPt = stroke[self.lastPt][0:2]
        newPt = stroke[self.currPt][0:2]
        thickness = stroke[self.currPt][2:3][0]
        thickness = max(math.ceil(thickness * factor), 1)
        oldPt = (math.floor(oldPt[0] * self.width), math.floor(oldPt[1] * self.height))
        newPt = (math.floor(newPt[0] * self.width), math.floor(newPt[1] * self.height))
        cv2.line(self.frame, oldPt, newPt, (0, 0, 0), thickness, cv2.LINE_AA)
        self.lastPt = self.currPt
        return

    def procStroke(self, stroke):
        oldPt = stroke[self.lastPt][0:3]
        newPt = stroke[self.currPt][0:3]
        flows = [newPt[0] - oldPt[0],
                 newPt[1] - oldPt[1],
                 newPt[2] - oldPt[2]]
        self.oldPos.append(oldPt)
        self.flows.append(flows)

        self.lastPt = self.currPt
        return

    def writeChar(self, ch):
        self.char = ch
        self.newChar()
        self.clearFrame()
        self.writing = True
        return

    def newChar(self):
        self.numStrokes = len(self.char)
        self.currSt = 0
        self.currPt = 0
        self.lastSt = self.currSt
        self.lastPt = self.currPt
        self.oldPos = []
        self.flows = []
        return

    def oneChar(self, ch):
        self.char = ch
        self.newChar()
        self.clearFrame()
        self.writing = True
        for s in range(self.numStrokes):
            self.lastSt = self.currSt
            self.currSt = s
            stroke = self.char[self.currSt]
            self.currPt = 0
            self.lastPt = self.currPt
            for p in range(len(stroke)):
                self.currPt = p
                #                self.drawSegment(stroke)
                self.procStroke(stroke)

        self.writing = False
        return

    def getStatus(self):
        return self.writing

    def getCharData(self):
        return self.oldPos, self.flows
