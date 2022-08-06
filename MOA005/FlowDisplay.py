from panda3d.core import *
import math
import numpy as np
import cv2


class FlowDisplay:

    def __init__(self, sz):
        self.bufSize = sz
        self.tex = Texture()
        self.flowNP = NodePath("flowDisplayNP")
        self.tex.setup_2d_texture(self.bufSize[0], self.bufSize[1],
                                  Texture.T_unsigned_byte, Texture.F_rgb8)

        cm = CardMaker("flowDisplay")
        cm.setFrameFullscreenQuad()
        cm.setUvRange(self.tex)
        card = NodePath(cm.generate())
        #        card.setDepthTest(True)
        #        card.setDepthWrite(True)
        #        card.setTwoSided(True)
        card.setScale(1.0, 0.001, 1.0)
        card.setPos(0, 0, 0)
        card.setHpr(0, 0, 0)
        #        card.setTransparency(TransparencyAttrib.MAlpha)
        card.setTexRotate(TextureStage.getDefault(), 180)
        card.setTexScale(TextureStage.getDefault(), -1, 1)
        card.setTexture(self.tex)
        card.reparentTo(self.flowNP)
        return

    def update(self, fl, fm):
        self.tex.setRamImage(self.drawFlow(fl, fm))
        return

    def drawFlow(self, data, fm):
        buffer = np.zeros((self.bufSize[1], self.bufSize[0], 3), dtype=np.uint8)
        max_radius = 12
        gap = 1
        dx = fm.shape[1] // data.shape[1]
        dy = fm.shape[0] // data.shape[0]
        offset = [(self.bufSize[0] - data.shape[1] * (max_radius * 2 + gap)) / 2,
                  (self.bufSize[1] - data.shape[0] * (max_radius * 2 + gap)) / 2]
        offset = [math.floor(offset[0]), math.floor(offset[1])]
        for y in range(data.shape[0]):
            yIdx = data.shape[0] - 1 - y * dy
            for x in range(data.shape[1]):
                rad = data[y][x][0]
                ang = data[y][x][1] * 360
                #                hls = (ang / 2, 255 * rad, 255)
                #                rgb = cv2.cvtColor(np.uint8([[hls]]), cv2.COLOR_HLS2RGB)[0][0]
                ctrx = x * (max_radius * 2 + gap) + offset[0]
                ctry = y * (max_radius * 2 + gap) + offset[1]
                col = fm[yIdx][x * dx]
                radius = math.floor(rad * max_radius * 0.4)
                outx = math.floor(ctrx + radius * math.cos(math.radians(ang)))
                outy = math.floor(ctry + radius * math.sin(math.radians(ang)))
                b = min(int(col[0]) * 2, 255)
                g = min(int(col[1]) * 2, 255)
                r = min(int(col[2]) * 2, 255)
                #                cv2.circle(buffer, (ctrx, ctry), radius, (b, g, r, 200), -1, cv2.LINE_AA)
                cv2.line(buffer, (ctrx, ctry), (outx, outy), (b, g, r, 250), 2, cv2.LINE_AA)
        return buffer

    def getNP(self):
        return self.flowNP
