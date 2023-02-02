import cv2
from panda3d.core import *
import numpy as np


class Capture:

    def __init__(self, sz, f):
        self.fps = f
        self.cap_size = sz
#        self.cap = cv2.VideoCapture(cv2.CAP_ANY)
        self.cap = cv2.VideoCapture(1)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cap_size[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cap_size[1])
        #        self.cap.set(cv2.CAP_PROP_FPS, self.fps)

        self.tex = Texture()
        self.tex.setup_2d_texture(self.cap_size[0], self.cap_size[1], Texture.T_unsigned_byte, Texture.F_rgba8)
        self.frame = np.zeros((self.cap_size[1], self.cap_size[0], 4))

        cm = CardMaker("video")
        cm.setFrameFullscreenQuad()
        cm.setUvRange(self.tex)

        self.np = NodePath(cm.generate())
        #        self.np.setDepthTest(True)
        #        self.np.setDepthWrite(True)
        self.np.setTransparency(TransparencyAttrib.MAlpha)

        self.np.setScale(1.2, 0.001, 0.675)
        self.np.setHpr(0, 0, 0)
        self.np.setTexture(self.tex)
        return

    def getNodePath(self):
        return self.np

    def getFrame(self):
        return self.frame

    def update(self):
        ok, fm = self.cap.read()
        if ok:
            fm = cv2.cvtColor(fm, cv2.COLOR_BGR2BGRA)
            self.frame = cv2.flip(fm, -1)
        return

    def updateTex(self, f):
        if f is not None:
            self.tex.setRamImage(f)
        return

    def cleanUp(self):
        self.cap.release()
        return
