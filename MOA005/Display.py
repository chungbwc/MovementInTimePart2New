from panda3d.core import *
import math
import numpy as np
import cv2


class Display:

    def __init__(self, cn, sz):
        self.count = cn
        self.bufSize = sz
        self.frameNP = NodePath("frames")
        self.tex = []
        self.idx = 0
        self.step = 0.01
        self.rot = 0
        self.rotDelta = 0

        self.tex = Texture()
        self.tex.setup_2d_texture(self.bufSize[0], self.bufSize[1],
                                  Texture.T_unsigned_byte, Texture.F_rgba8)
        self.movement = np.zeros((self.bufSize[1], self.bufSize[0], 4), np.uint8)

        cm = CardMaker("motion")
        cm.setFrameFullscreenQuad()
        cm.setUvRange(self.tex)
        card = NodePath(cm.generate())
        card.setDepthTest(True)
        card.setDepthWrite(True)
        card.setTwoSided(True)
        #            card.setScale(3.2, 0.001, 1.8)
        card.setScale(1.0, 0.001, 1.0)
        card.setPos(0, 0, 0)
        card.setHpr(0, 0, 0)
        card.setTransparency(TransparencyAttrib.MAlpha)
        card.setTexRotate(TextureStage.getDefault(), 180)
        card.setTexScale(TextureStage.getDefault(), -1, 1)
        card.setTexture(self.tex)
        card.reparentTo(self.frameNP)

        return

    def getNP(self):
        return self.frameNP

    def update(self, ch):
        if ch.shape[0] != self.count:
            return

        self.movement = np.zeros((self.bufSize[1], self.bufSize[0], 4), np.uint8)
        for i in range(self.count):
            data = ch[i]
            self.drawCircle(data, i)

        self.tex.setRamImage(self.movement)

        self.rot = self.rot + self.rotDelta
        self.rot = self.rot % 360
        return

    def drawCircle(self, data, lv):
        max_radius = 50
        gap = 15
        offset = [(self.bufSize[0] - data.shape[0] * (max_radius * 2 + gap)) / 2,
                  (self.bufSize[1] - data.shape[1] * (max_radius * 2 + gap)) / 2]
        offset = [math.floor(offset[0]), math.floor(offset[1])]
        alpha = math.floor(150.0 * lv / self.count) + 50
        for i in range(data.shape[0]):
            for j in range(data.shape[1]):
                rad = data[i][j][0]
                ang = data[i][j][1] * 360
#                hls = (ang / 2, math.floor(rad * 255), 255)
                hls = (90, math.floor(rad * 255), 255)
                rgb = cv2.cvtColor(np.uint8([[hls]]), cv2.COLOR_HLS2RGB)[0][0]
                ctrx = i * (max_radius * 2 + gap) + offset[0]
                ctry = j * (max_radius * 2 + gap) + offset[1]
                radius = math.floor(rad * max_radius)
                outx = math.floor(ctrx + radius * math.cos(math.radians(ang)))
                outy = math.floor(ctry + radius * math.sin(math.radians(ang)))
                newx = math.floor((ctrx + outx) / 2)
                newy = math.floor((ctry + outy) / 2)
                r = int(rgb[0])
                g = int(rgb[1])
                b = int(rgb[2])
                #                cv2.circle(self.movement, (ctrx, ctry),
                #                           radius, (b, g, r, alpha), -1, cv2.LINE_AA)
                cv2.circle(self.movement, (newx, newy),
                           radius // 2, (b, g, r, alpha), -1, cv2.LINE_AA)
        #                cv2.line(self.movement, (ctrx, ctry), (outx, outy),
        #                         (255-b, 255-g, 255-r, alpha), 2, cv2.LINE_AA)
        return

    def getRot(self):
        return self.rot
