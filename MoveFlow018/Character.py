import random

from panda3d.core import *
from panda3d.bullet import *


class Character:

    def __init__(self, sz, pr):
        self.size = sz
        self.tex = Texture()
        self.tex.setup_2d_texture(self.size[0], self.size[1],
                                  Texture.T_unsigned_byte, Texture.F_rgba8)
        self.parent = pr
        self.node = None
        self.vNP = None
        self.rot = 0
        self.rotDelta = 0.5
        return

    def makeChar(self, info):
        res = 32
        p00 = Point3(0, 0, 0)
        p10 = Point3(1, 0, 0)
        p01 = Point3(0, 0, 1)
        p11 = Point3(1, 0, 1)
        #        fixeds = 1 + 2 + 4 + 8
        fixeds = 4 + 8
        #        fixeds = 0

        self.node = BulletSoftBodyNode.makePatch(info, p00, p10, p01, p11, res, res, fixeds, True)
        material = self.node.appendMaterial()
        material.setLinearStiffness(0.25)
        material.setAngularStiffness(0.25)
        self.node.generateBendingConstraints(2, material)
        self.node.getCfg().setLiftCoefficient(0.04)
        self.node.getCfg().setDynamicFrictionCoefficient(0.0003)
        # node.getCfg().setAeroModel(BulletSoftBodyConfig.AMVertexTwoSided)
        #            node.getCfg().setAeroModel(BulletSoftBodyConfig.AMFaceTwoSided)
        self.node.getCfg().setAeroModel(BulletSoftBodyConfig.AMVertexPoint)
        self.node.setTotalMass(0.03)
        #        node.addForce(Vec3(0, 0, -0.5), 0)
        #        node.setWindVelocity(self.Vec3Rand() * 1.5)
        self.parent.world.attachSoftBody(self.node)
        #        shoulders = self.parent.flowDisplay.getShoulders()
        #        self.node.appendAnchor(0, shoulders[0].node())
        #        self.node.appendAnchor(res - 1, shoulders[1].node())

        fmt = GeomVertexFormat.getV3n3t2()
        geom = BulletHelper.makeGeomFromFaces(self.node, fmt, True)
        self.node.linkGeom(geom)
        nodeP = self.parent.charArea.attachNewNode(self.node)

        nov = GeomNode('char')
        nov.addGeom(geom)

        self.vNP = nodeP.attachNewNode(nov)
        self.vNP.setTexture(self.tex)
        BulletHelper.makeTexcoordsForPatch(geom, res, res)

        self.vNP.setTexRotate(TextureStage.getDefault(), 270)
        #        self.vNP.setTexScale(TextureStage.getDefault(), -1, 1)

        #        self.vNP.setPos(1.2, -1, -1.4)
        self.vNP.setPos(-2.3, 0, 0.3)
        #        vNP.setHpr(random.randrange(-30, 30), 0, 0)
        self.vNP.setHpr(40, 0, 0)
        self.vNP.setDepthTest(False)
        self.vNP.setDepthWrite(False)
        self.vNP.setTwoSided(True)
        self.vNP.setTransparency(True)
        return

    def updateTex(self, fm):
        self.tex.setRamImage(fm)
        return

    def updateWind(self):
        vx = random.random() - 0.5
        vy = random.random() - 0.5
        vz = random.random() - 0.5
        factor = 0.75
        self.node.setWindVelocity(Vec3(vx * factor, vy * factor, vz * factor))
        return

    def addForce(self, pt):
        factor = 0.01
        idx = self.node.getClosestNodeIndex(LVector3(pt[0], 0, pt[1]), True)
        self.node.addForce(LVector3(pt[0] * factor, pt[2] * factor, pt[1] * factor), idx)
        return

    def rotate(self):
        self.rot = self.rot + self.rotDelta
        self.rot = self.rot % 360
        self.vNP.setHpr(self.rot, 0, 0)
        return
