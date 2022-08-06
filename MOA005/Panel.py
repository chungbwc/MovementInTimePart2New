import cv2
import numpy as np
import math
import os
from panda3d.core import *
from PIL import ImageFont, ImageDraw, Image


class Panel:

    def __init__(self, sz):
        self.width = sz[0]
        self.height = sz[1]
        self.step = 20
        self.rows = self.height // self.step
        self.cols = self.width // self.step
        self.backColour = (0, 0, 0)
        self.colour = (0, 0, 255)
        self.panelNP = NodePath("panel")
        self.tex = Texture()
        self.tex.setup_2d_texture(self.width, self.height,
                                  Texture.T_unsigned_byte, Texture.F_rgb8)
        self.frame = None
        self.last = -1
        self.curr = -1
        self.first = True

        fontFile = "data" + os.path.sep + "font" + os.path.sep + "simsun.ttc"
        self.font = ImageFont.truetype(fontFile, self.step)

        self.clearFrame()

        cm = CardMaker("panelCard")
        cm.setFrameFullscreenQuad()
        cm.setUvRange(self.tex)
        card = NodePath(cm.generate())
        #        card.setDepthTest(True)
        #        card.setDepthWrite(True)
        #        card.setTwoSided(True)
        #            card.setScale(3.2, 0.001, 1.8)
        card.setScale(1.0, 0.001, 1.0)
        card.setPos(0, 0, 0)
        card.setHpr(0, 0, 0)
        card.setTransparency(TransparencyAttrib.MAlpha)
        card.setTexRotate(TextureStage.getDefault(), 180)
        card.setTexScale(TextureStage.getDefault(), -1, 1)
        card.setTexture(self.tex)
        card.reparentTo(self.panelNP)
        return

    def getNP(self):
        return self.panelNP

    def clearFrame(self):
        self.frame = np.full((self.height, self.width, 3), self.backColour, np.uint8)
        return

    def reset(self):
        self.last = -1
        self.curr = -1
        self.first = True
        self.clearFrame()
        return

    def update(self, i, f, c):
        self.last = self.curr
        self.curr = i
        if self.first:
            self.first = False
            self.last = i

        y = self.curr % self.rows
        x = self.cols - 1 - self.curr // self.rows
        topCurr = y * self.step
        leftCurr = x * self.step
        cx = math.floor(f.shape[1] * (leftCurr + self.step // 2) / self.width)
        cy = math.floor(f.shape[0] * (topCurr + self.step // 2) / self.height)
        col = f[cy][cx]
        b = math.floor(col[0])
        g = math.floor(col[1])
        r = math.floor(col[2])

        y = self.last % self.rows
        x = self.cols - 1 - self.last // self.rows
        topLast = y * self.step
        leftLast = x * self.step

        cv2.line(self.frame, (leftCurr + self.step // 2, topCurr + self.step // 2),
                 (leftLast + self.step // 2, topLast + self.step // 2),
                 (b, g, r), 1, cv2.LINE_AA)
        #        cv2.rectangle(self.frame, (leftCurr, topCurr),
        #                      (leftCurr + self.step, topCurr + self.step),
        #                      (0, 0, 0, 0), -1)

        imgPil = Image.fromarray(self.frame)
        draw = ImageDraw.Draw(imgPil)
        draw.text((leftCurr, topCurr), c, font=self.font, fill=(255, 255, 255))

        self.frame = np.array(imgPil)

        # cv2.circle(self.frame, (leftCurr + self.step // 2, topCurr + self.step // 2),
        #           self.step // 2, (0, 0, 0, 255), -1, cv2.LINE_AA)

        self.tex.setRamImage(self.frame)
        return
