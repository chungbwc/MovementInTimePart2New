#!/usr/bin/env python3

from direct.showbase.ShowBase import ShowBase

from panda3d.core import *
from panda3d.bullet import BulletWorld

import os

from Capture import Capture
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
char_size = (400, 400)
panel_size = (840, 480)
fps = 30
skips = 7
grid_size = 3
match_threshold = 5.5
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
        self.exitFunc = self.cleanup

        self.accept("v", self.bufferViewer.toggleEnable)
        self.bufferViewer.setPosition("ulcorner")
        self.bufferViewer.setCardSize(1.0, 0.0)

        base.disableMouse()
        base.camera.setPos(0, -6, 0)
        base.camera.lookAt(0, 0, 0)
        #        base.camLens.setFov(25)
        base.setBackgroundColor(0, 0, 0)

        self.bufTex = Texture()
        self.bufTex.setMinfilter(Texture.FTLinear)
        self.win.addRenderTexture(self.bufTex, GraphicsOutput.RTMTriggeredCopyTexture)
        self.bufTex.setClearColor((0, 0, 0, 1))
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
        self.back.setColor(0.9, 0.9, 0.9, 0.5)
        self.back.setPos(0.5, 0, 0.5)
        self.back.setScale(0.5)
        self.win.triggerCopy()
        self.back.setTexture(self.bufTex)
        self.back.node().setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))

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

        self.capture = Capture(cap_size, fps)
        self.pose = Pose()
        self.flowDisplay = FlowDisplay(self.pose.getPoseLength(), self)
        self.pose.setDisplay(self.flowDisplay)
        self.poseGrid = GridDisplay(self.pose.getFrames(), cap_size)
        self.charGrid = GridDisplay(self.pose.getFrames(), cap_size)
        self.matching = Matching(csv_file, self.pose.getFrames(), grid_size)
        charDir = "data" + os.path.sep + "characters" + os.path.sep
        self.characters = Loader(charDir)
        self.char = Character(char_size, self)
        self.animation = Animation(char_size)
        self.thousand = Thousand(panel_size, self.characters.getNames())

        # Camera capture with OpenCV

        thouNP = self.thousand.getNP()
        thouNP.setPos(1.45, 0, -0.8)
        thouNP.setScale(1.4, 0.1, 0.8)
        thouNP.reparentTo(self.render)

        poseNP = self.flowDisplay.getNP()
        poseNP.setScale(1, 0.01, 1)
        poseNP.setPos(0, 2, 0)
        poseNP.reparentTo(self.render)
        poseNP.setTransparency(True)
        poseNP.setTwoSided(True)
        poseNP.setDepthWrite(False)
        poseNP.setDepthTest(False)
        poseNP.setColor(1, 1, 1, 0.9)
        poseNP.node().setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MNone))

        grid1NP = self.poseGrid.getNP()
        grid1NP.setPos(-1.8, 0, -0.8)
        grid1NP.setScale(1.0, 1, 0.56)
        grid1NP.reparentTo(self.render)

        grid2NP = self.charGrid.getNP()
        grid2NP.setPos(-0.6, 0, -0.8)
        grid2NP.setScale(1.0, 1, 0.56)
        grid2NP.reparentTo(self.render)

        self.charArea = NodePath("character")
        self.charArea.setPos(0, 0, 0)
        self.charArea.setScale(0.8, 0.1, 0.8)
        self.charArea.setHpr(0, 0, 0)
        self.charArea.reparentTo(self.render)

        self.char.makeChar(self.worldInfo)

        self.taskMgr.add(self.update, 'update')
        return

    def update(self, task):
        self.capture.update()
        self.pose.track(self.capture.getFrame())
        self.capture.updateTex(self.pose.getImage())
        self.thousand.update(self.pose.getImage())
        motion = self.pose.getMotion()
        self.poseGrid.update(motion)

        if (not self.animation.isWriting()) and self.pose.isTracking():
            dist, idx = self.matching.matchData(motion)
            if dist < match_threshold:
                c = self.characters.getName(idx)
                ch = self.characters.getChar(idx)
                mot = self.matching.getCharMotion(idx)
                mot = mot.reshape((self.pose.getFrames(), grid_size, grid_size, 2))
                self.charGrid.update(mot)
                self.animation.writeChar2d(ch)
                self.char.updateWind()
        else:
            for i in range(skips):
                self.animation.update()
            self.char.updateTex(self.animation.getFrame())
            point = self.animation.getPoint()
            self.char.addForce(point)

        self.char.rotate()

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


player = Demo()
player.run()
