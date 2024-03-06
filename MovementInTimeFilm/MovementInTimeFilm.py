#!/usr/bin/env python3

from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase

from panda3d.core import *
from panda3d.bullet import BulletWorld

import os
import datetime
import numpy as np
import cv2

from Capture import Capture
from FilmDir import FilmDir
from Pose import Pose
from FlowDisplay import FlowDisplay
from GridDisplay import GridDisplay
from Matching import Matching
from Character import Character
from Animation import Animation
from Loader import Loader
from Thousand import Thousand

# loadPrcFileData("", "show-frame-rate-meter #t")
# loadPrcFileData("", "sync-video #f")

loadPrcFileData("", "threading-model Cull/Draw")
loadPrcFileData("", "textures-power-2 none")

dimen = [1920, 1080]
cap_size = (640, 360)
film_size = (720, 360)
char_size = (400, 400)
panel_size = (840, 480)
office = [8, 24]

fps = 30
skips = 15
grid_size = 3
match_threshold = 5.4
csv_file = "data" + os.path.sep + "csv" + os.path.sep + "chars10x3x3.csv"


class Demo(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        properties = WindowProperties()
        properties.setTitle('Winnie the Pooh')
        properties.setSize(dimen[0], dimen[1])
        properties.setCursorHidden(True)
        properties.setFullscreen(True)
        properties.setMouseMode(WindowProperties.M_absolute)
        self.openMainWindow()
        self.win.requestProperties(properties)
        self.graphicsEngine.openWindows()
        base.setFrameRateMeter(False)

        #        self.clock.setMode(ClockObject.MLimited)
        #        self.clock.setFrameRate(fps)

        self.accept('escape', self.userExit)
        self.accept('arrow_right', self.nextFilm)
        self.exitFunc = self.cleanup

        self.accept("v", self.bufferViewer.toggleEnable)
        self.bufferViewer.setPosition("ulcorner")
        self.bufferViewer.setCardSize(1.0, 0.0)

        base.disableMouse()
        base.camera.setPos(0, -6, 0)
        base.camera.lookAt(0, 0, 0)
        #        base.camLens.setFov(25)
        base.setBackgroundColor(1, 1, 1)
        base.enableParticles()

        self.bufTex = Texture()
        self.bufTex.setMinfilter(Texture.FTLinear)
        self.win.addRenderTexture(self.bufTex, GraphicsOutput.RTMTriggeredCopyTexture)
        self.bufTex.setClearColor((1, 1, 1, 1))
        self.bufTex.clearImage()

        self.backCam = self.makeCamera2d(self.win, sort=-10)
        self.background = NodePath("background")
        self.backCam.reparentTo(self.background)

        self.background.setDepthTest(False)
        self.background.setDepthWrite(False)
        self.background.setTransparency(True)
        self.background.setTwoSided(True)
        self.backCam.node().getDisplayRegion(0).setClearDepthActive(False)

        #        self.back = self.win.getTextureCard()
        bcard = CardMaker("back")
        bcard.setFrameFullscreenQuad()
        bcard.setUvRange(Point2(0.5, 0.5), Point2(1, 1))
        #        bcard.setUvRange(self.bufTex)

        self.back = NodePath(bcard.generate())

        self.back.reparentTo(self.background)
        self.back.setTransparency(True)
        self.back.setColor(0.5, 0.5, 0.5, 0.4)
        self.back.setPos(0.5, 0, 0.5)
        self.back.setScale(0.5)
        self.win.triggerCopy()
        self.back.setTexture(self.bufTex)
        self.back.node().setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MNone))

        alight = AmbientLight('ambientLight')
        alight.setColor(Vec4(0.8, 0.8, 0.8, 1))
        alightNP = self.render.attachNewNode(alight)

        dlight = DirectionalLight('directionalLight')
        dlight.setDirection(Vec3(5, 0, -2))
        dlight.setColor(Vec4(0.7, 0.7, 0.7, 1))
        dlightNP = self.render.attachNewNode(dlight)

        self.render.clearLight()
        self.render.setLight(alightNP)
        self.render.setLight(dlightNP)

        self.world = None
        self.worldInfo = None
        self.prepareWorld()

        self.filmDir = FilmDir("data" + os.path.sep + "film" + os.path.sep)

        self.capture = Capture(cap_size, fps)
        self.pose = Pose()
        self.flowDisplay = FlowDisplay(self.pose.getPoseLength(), self)
        self.pose.setDisplay(self.flowDisplay)
        self.poseGrid = GridDisplay(self.pose.getFrames(), cap_size)
        #        self.charGrid = GridDisplay(self.pose.getFrames(), cap_size)
        self.matching = Matching(csv_file, self.pose.getFrames(), grid_size)
        self.idx = -1
        charDir = "data" + os.path.sep + "characters" + os.path.sep
        self.characters = Loader(charDir)
        self.char = Character(char_size, self)
        self.animation = Animation(char_size)
        self.thousand = Thousand(panel_size, self.characters.getNames())

        self.filmTex = Texture()
        self.filmTex.setup_2d_texture(film_size[0], film_size[1], Texture.T_unsigned_byte, Texture.F_rgb8)

        self.cap = None
        self.playFilm()

        # Camera capture with OpenCV

        thouNP = self.thousand.getNP()
        thouNP.setPos(1.45, 0, -0.8)
        thouNP.setScale(1.4, 0.01, 0.8)
        thouNP.setLightOff()
        thouNP.reparentTo(self.render)

        poseNP = self.flowDisplay.getNP()
        poseNP.setScale(1, 0.01, 1)
        poseNP.setPos(0, 2, 0)
        poseNP.setLightOff()
        poseNP.reparentTo(self.render)
        poseNP.setTransparency(True)
        #        poseNP.setTwoSided(True)
        poseNP.setDepthWrite(False)
        poseNP.setDepthTest(False)
        poseNP.setColor(1, 1, 1, 0.9)
        poseNP.node().setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MNone))

        grid1NP = self.poseGrid.getNP()
        grid1NP.setPos(-1.1, 0, -1)
        grid1NP.setScale(1.2, 1, 0.675)
        grid1NP.setLightOff()
        grid1NP.reparentTo(self.render)

        self.charArea = NodePath("character")
        self.charArea.setPos(0, 0, 0)
        #        self.charArea.setScale(0.8, 0.1, 0.8)
        self.charArea.setScale(1.0, 0.1, 1.0)
        self.charArea.setHpr(0, 0, 0)
        self.charArea.setLightOff()
        self.charArea.reparentTo(self.render)

        self.char.makeChar(self.worldInfo)

        fontFile = "data" + os.path.sep + "font" + os.path.sep + "simsun.ttc"
        chineseFont = self.loader.loadFont(fontFile)

        textArea = NodePath("title")
        textArea.setColor(0.1, 0.1, 0.1)
        textArea.reparentTo(self.render)

        text1 = TextNode("gridtext")
        text1.setText("Motion data visualisation in 10 frames")
        text1NP = textArea.attachNewNode(text1)
        text1NP.setScale(0.05, 0.05, 0.05)
        text1NP.setPos(-2.5, -0.01, -0.1)
        text1NP.hide()

        text2 = TextNode("posetext")
        text2.setText("Hands and pose visualisation")
        text2NP = textArea.attachNewNode(text2)
        text2NP.setScale(0.05, 0.05, 0.05)
        text2NP.setPos(0.1, -0.01, 1.4)
        text2NP.hide()

        self.text3 = TextNode("chartext")
        self.text3.setFont(chineseFont)
        self.text3.setText("")
        text3NP = textArea.attachNewNode(self.text3)
        text3NP.setScale(0.1, 0.1, 0.1)
        text3NP.setPos(-1.8, -0.01, 0.15)
        text3NP.setColor(0.8, 0, 0)

        text4 = TextNode("thousandtext")
        text4.setText("Thousand Character Classic")
        text4NP = textArea.attachNewNode(text4)
        text4NP.setScale(0.05, 0.05, 0.05)
        text4NP.setPos(0.1, -0.01, -0.1)
        text4NP.hide()

        self.taskMgr.add(self.update, 'update')
        return

    def nextFilm(self):
        self.playFilm()
        self.poem.reset()
        self.panel.reset()
        return

    def playFilm(self):
        film = self.filmDir.nextFilm()
        self.cap = cv2.VideoCapture(film)

        if not self.cap.isOpened():
            print("Cannot open film")

        return

    def update(self, task):
        now = datetime.datetime.now()
        hour = now.hour
        if hour < office[0] or hour >= office[1]:
            print("Good Bye")
            self.userExit()

        ok, frame = self.cap.read()
        if not ok:
            print("Exit now")
            self.userExit()
            self.nextFilm()
            return task.cont

        if frame is not None:
            frame = cv2.flip(frame, 0)
            self.filmTex.setRamImage(frame)

        self.capture.update()
        self.pose.track(self.capture.getFrame())
        self.capture.updateTex(self.pose.getImage())
        self.thousand.update(self.pose.getImage())

        if (not self.animation.isWriting()) and self.pose.isTracking():
            motion = self.pose.getMotion()
            self.poseGrid.update(motion)

            dist, self.idx = self.matching.matchData(motion)
            if dist < match_threshold:
                c = self.characters.getName(self.idx)
                ch = self.characters.getChar(self.idx)

                self.text3.setText(c)
                self.animation.writeChar2d(ch)
                self.char.updateWind()
        else:
            for i in range(skips):
                self.animation.update()
            self.char.updateTex(self.animation.getFrame())
            point = self.animation.getPoint()
            self.char.addForce(point)
            self.char.rotate()

        if self.animation.isWriting():
            motion = self.matching.getCharMotion(self.idx)
            motion = motion.reshape((self.pose.getFrames(), grid_size, grid_size, 2))
            self.poseGrid.update(motion)

        if (task.frame % 2) == 0:
            self.win.triggerCopy()

        dt = self.clock.getDt()
        self.world.doPhysics(dt, 10, 0.005)
        return task.cont

    def cleanup(self):
        self.capture.cleanUp()
        self.enableMouse()
        return

    def prepareWorld(self):
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -2.5))
        self.worldInfo = self.world.getWorldInfo()
        self.worldInfo.setAirDensity(1.2)
        self.worldInfo.setWaterDensity(0)
        self.worldInfo.setWaterOffset(0)
        self.worldInfo.setWaterNormal(Vec3(0, 0, 0))


if __name__ == "__main__":
    player = Demo()
    player.run()
