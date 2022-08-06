#!/usr/bin/env python3

from panda3d.core import *
import cv2
import os
import numpy as np

from direct.showbase.DirectObject import DirectObject
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBase import ShowBase

from panda3d.bullet import BulletWorld
from panda3d.bullet import BulletHelper
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletDebugNode
from panda3d.bullet import BulletTriangleMesh
from panda3d.bullet import BulletTriangleMeshShape
from panda3d.bullet import BulletSoftBodyNode
from panda3d.bullet import BulletSoftBodyConfig

from FilmDir import FilmDir
from OpFlow import OpFlow
from Grid import Grid
from Display import Display
from FlowDisplay import FlowDisplay
from Loader import Loader
from Poem import Poem
from Matching import Matching
from Animation import Animation
from Character import Character
from Panel import Panel

# Tell Panda3D to use OpenAL, not FMOD
# loadPrcFileData("", "audio-library-name p3openal_audio")
# loadPrcFileData("", "win-size 1280 720")
# loadPrcFileData("", "show-frame-rate_meter #f")
loadPrcFileData("", "sync-video #f")
loadPrcFileData("", "textures-power-2 none")
loadPrcFileData("", "text-use-harfbuzz #t")

screen_size = (1920, 1080)
buf_size = (960, 480)
film_size = (720, 360)
char_size = (400, 400)
grid_size = 3
num_frames = 10
match_threshold = 6.5
csv_file = "data" + os.path.sep + "csv" + os.path.sep + "chars10x3x3.csv"


class MediaPlayer(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        properties = WindowProperties()
        #        properties.setFullscreen(True)
        properties.setTitle('Winnie the Pooh')
        properties.setSize(screen_size[0], screen_size[1])
        properties.setCursorHidden(True)
        self.openMainWindow()
        self.win.requestProperties(properties)
        self.graphicsEngine.openWindows()
        base.setFrameRateMeter(False)
        self.disable_mouse()

        self.clock.setMode(ClockObject.MLimited)
        self.clock.setFrameRate(30)

        self.accept('escape', self.userExit)
        self.accept('arrow_right', self.nextFilm)
        self.exitFunc = self.cleanup

        base.camera.setPos(0, -6, 0)
        base.camera.lookAt(0, 0, 0)
        base.setBackgroundColor(0, 0, 0)

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

        self.worldNP = None
        self.world = None
        self.worldInfo = None

        self.prepareWorld()

        self.scale = 15
        self.filmDir = FilmDir("data" + os.path.sep + "film" + os.path.sep)
        self.flows = OpFlow(film_size[0] // self.scale, film_size[1] // self.scale, self.scale)
        self.grid = Grid(num_frames, grid_size)
        self.display = Display(num_frames, buf_size)
        self.flowDisplay = FlowDisplay(buf_size)
        self.matching = Matching(csv_file, num_frames, grid_size)
        charDir = "data" + os.path.sep + "characters" + os.path.sep
        self.characters = Loader(charDir)
        self.poem = Poem()
        self.panel = Panel((840, 480))

        self.animation = Animation(char_size)
        self.char = Character(char_size, self)

        self.filmTex = Texture()
        self.filmTex.setup_2d_texture(film_size[0], film_size[1], Texture.T_unsigned_byte, Texture.F_rgb8)

        self.cap = None
        self.playFilm()

        self.displayNP = self.display.getNP()
        self.displayNP.setPos(-1.2, 0, -0.95)
        self.displayNP.setScale(1.4, 1, 0.7)
        self.displayNP.setHpr(0, 0, 0)
        self.displayNP.reparentTo(self.render)

        self.panelNP = self.panel.getNP()
        self.panelNP.setPos(1.4, 0, 0.7)
        self.panelNP.setScale(1.2, 1, 0.68)
        self.panelNP.setHpr(0, 0, 0)
        self.panelNP.reparentTo(self.render)

        self.flowNP = self.flowDisplay.getNP()
        self.flowNP.setPos(-1.3, 0, 0.75)
        self.flowNP.setScale(1.4, 1, 0.7)
        self.flowNP.setHpr(0, 0, 0)
        self.flowNP.reparentTo(self.render)

        self.poemText = TextNode("poem")
        font = self.loader.loadFont("data/font/simsun.ttc")

        self.poemText.setFont(font)

        text_card = CardMaker("text")
        cardNP = NodePath(text_card.generate())
        self.textNP = cardNP.attachNewNode(self.poemText)
        cardNP.reparentTo(self.render)
        cardNP.setScale(1, 0, 1)
        cardNP.setPos(0.2, 0, -3)
        cardNP.setColor(0, 0, 0)

        self.textNP.setScale(0.15)
        self.textNP.setColor(0.4, 0.5, 0.5)
        self.textNP.setPos(0, 0, 2.7)
        self.textNP.hide()

        self.charArea = NodePath("character")
        self.charArea.setPos(0, 0, 0)
        self.charArea.setScale(1.2, 1, 1.2)
        self.charArea.setHpr(0, 0, 0)
        self.charArea.reparentTo(self.render)

        self.char.makeChar(self.worldInfo)

        self.taskMgr.add(self.update, "update")
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

    def prepareWorld(self):
        #        self.worldNP = self.charArea.attachNewNode('World')
        self.world = BulletWorld()
        self.world.setGravity(Vec3(0, 0, -2))
        self.worldInfo = self.world.getWorldInfo()
        self.worldInfo.setAirDensity(1.2)
        self.worldInfo.setWaterDensity(0)
        self.worldInfo.setWaterOffset(0)
        self.worldInfo.setWaterNormal(Vec3(0, 0, 0))

        return

    def update(self, task):
        ok, frame = self.cap.read()
        if not ok:
            print("Exit now")
            self.userExit()

            self.nextFilm()
            return task.cont

        if frame is not None:
            frame = cv2.flip(frame, 0)
            self.filmTex.setRamImage(frame)
            self.flows.update(frame)
            self.grid.update(self.flows.getFlow())
            motion = self.grid.getMotion()
            self.display.update(motion)
            self.displayNP.setHpr(self.display.getRot(), 0, 0)
            self.flowDisplay.update(self.flows.getFullFlow(), frame)

            if not self.animation.isWriting():
                dist, idx = self.matching.matchData(motion)
                if dist < match_threshold:
                    c = self.characters.getName(idx)
                    self.poem.addChar(c)
                    text = self.poem.getString()
                    self.poemText.setText(text)
                    ch = self.characters.getChar(idx)
                    self.animation.writeChar2d(ch)
                    self.char.updateWind()
                    txt = self.characters.getName(idx)
                    self.panel.update(idx, frame, txt)

        if self.animation.isWriting():
            for i in range(15):
                self.animation.update()
            self.char.updateTex(self.animation.getFrame())
            self.char.rotate()
            point = self.animation.getPoint()
            self.char.addForce(point)

        self.char.rotate()

        #        dt = globalClock.getDt()
        dt = self.clock.getDt()
        self.world.doPhysics(dt, 10, 0.008)

        return task.cont

    def cleanup(self):
        self.cap.release()
        self.enableMouse()
        return


if __name__ == "__main__":
    player = MediaPlayer()
    player.run()
