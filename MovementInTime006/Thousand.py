import cv2
import numpy as np
import math
import os
from panda3d.core import *
from PIL import ImageFont, ImageDraw, Image


class Thousand:

    def __init__(self, sz, nm):
        self.size = sz
        self.names = nm
        self.step = 20
        self.rows = math.floor(self.size[1] / self.step)
        self.cols = math.floor(self.size[0] / self.step)
        self.backColour = (255, 255, 255)

        self.nodePath = NodePath("thousand")
        self.tex = Texture()
        self.tex.setup_2d_texture(self.size[0], self.size[1],
                                  Texture.T_unsigned_byte, Texture.F_rgb8)

        fontFile = "data" + os.path.sep + "font" + os.path.sep + "simsun.ttc"
        self.font = ImageFont.truetype(fontFile, self.step)

        self.image = None
        self.clearImage()

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
        #        card.setTransparency(TransparencyAttrib.MAlpha)
        card.setTexRotate(TextureStage.getDefault(), 180)
        card.setTexScale(TextureStage.getDefault(), -1, 1)
        card.setTexture(self.tex)
        card.reparentTo(self.nodePath)
        return

    def getNP(self):
        return self.nodePath

    def clearImage(self):
        self.image = Image.new("RGB", self.size, self.backColour)

    def update(self, fm):
        factor = 1.2
        self.clearImage()
        draw = ImageDraw.Draw(self.image)
        draw.rectangle((0, 0, self.size[0], self.size[1]), fill=self.backColour)
        frame = cv2.flip(fm, 0)

        for i in range(len(self.names)):
            x = (self.cols - 1 - i // self.rows) * self.step
            y = (i % self.rows) * self.step

            cx = x + self.step / 2
            cy = y + self.step / 2
            cx = math.floor(cx * frame.shape[1] / self.size[0])
            cy = math.floor(cy * frame.shape[0] / self.size[1])
            col = frame[cy][cx]
            b = col[0]
            g = col[1]
            r = col[2]
            a = col[3]

            b = math.floor(min(b * factor, 255))
            g = math.floor(min(g * factor, 255))
            r = math.floor(min(r * factor, 255))
            if a == 0:
                continue
            else:
                draw.text((x, y), self.names[i], font=self.font, fill=(b, g, r))

        self.tex.setRamImage(np.array(self.image))
        return
