from panda3d.core import *
from panda3d.bullet import *

import numpy as np
import os
import random

from PartSystem2 import PartSystem

HANDS = [15, 16]
POSE_LEN = 33


class FlowDisplay:

    def __init__(self, pn, pr):
        self.pLength = pn
        self.np = NodePath("poseflow")
        #        self.np.setRenderModeThickness(2)
        self.np.setPos(0, 0, 0)
        self.np.setHpr(0, 0, 0)
        self.np.setScale(1, 1, 1)
        self.np.setTransparency(True)
        self.np.setDepthTest(False)
        self.np.setDepthWrite(False)
        #        self.np.setTwoSided(True)

        self.ropeNP = NodePath("ropes")
        self.ropeNP.reparentTo(self.np)
        self.ropeNP.setScale(1, 1, 1)

#        self.ropeNP.setAttrib(
#            ColorWriteAttrib.make(ColorWriteAttrib.CRed |
#                                  ColorWriteAttrib.CGreen |
#                                  ColorWriteAttrib.CBlue))

        self.pose = self.makePose()
        self.poseNP = NodePath(self.pose)
        self.poseNP.setRenderModeThickness(1)
        self.poseNP.setTransparency(True)
        self.poseNP.setDepthTest(False)
        self.poseNP.setDepthWrite(False)
        #        self.poseNP.setTwoSided(True)
        self.poseNP.setColor(1, 1, 1, 0.5)
        self.poseNP.reparentTo(self.np)
#        self.poseNP.setAttrib(
#            ColorWriteAttrib.make(ColorWriteAttrib.CRed |
#                                  ColorWriteAttrib.CGreen |
#                                  ColorWriteAttrib.CBlue))

        self.offset = (2.0, 0.8)

        self.parent = pr
        self.ropes = []
        self.hands = []
        self.boxes = []
        self.partsys = []

        self.setupRopes()

        for i in range(len(HANDS)):
            p = PartSystem("p" + str(i))
            p.setup()
            self.partsys.append(p)

        for i in range(len(HANDS)):
            self.partsys[i].getNode().start(self.np, self.np)
            self.partsys[i].getNode().setPos(0, 0, 0)
            self.partsys[i].getNode().setAttrib(
                ColorWriteAttrib.make(ColorWriteAttrib.CRed |
                                      ColorWriteAttrib.CGreen |
                                      ColorWriteAttrib.CBlue))

        return

    def setupRopes(self):
        model = base.loader.loadModel("models" + os.path.sep + "box.egg")
        model.setPos(-0.5, -0.5, -0.5)
        model.flattenLight()

        box = BulletBoxShape(Vec3(0.5, 0.5, 0.5))

        for i in range(len(HANDS)):
            tnode = BulletRigidBodyNode('box')
            tnode.setMass(0)
            tnode.addShape(box)
            #            tpath = self.parent.render.attachNewNode(tnode)
            tpath = self.ropeNP.attachNewNode(tnode)
            tpath.setPos(0, 0, 0)
            tpath.setScale(0.1, 0.1, 0.1)
            self.parent.world.attachRigidBody(tnode)
            model.copyTo(tpath)
            self.hands.append(tpath)

        for i in range(len(HANDS)):
            tnode = BulletRigidBodyNode('box')
            tnode.setMass(0.002)
            tnode.addShape(box)
            #            tpath = self.parent.render.attachNewNode(tnode)
            tpath = self.ropeNP.attachNewNode(tnode)
            tpath.setPos(0, 0, -1)
            tpath.setScale(0.1, 0.1, 0.1)
            self.parent.world.attachRigidBody(tnode)
            model.copyTo(tpath)
            self.boxes.append(tpath)

        for i in range((len(HANDS))):
            rope = self.makeRope(self.parent.worldInfo, self.hands[i], self.boxes[i])
            self.ropes.append(rope)
            self.hands[i].hide()
            self.boxes[i].hide()
        return

    def update(self, old, new):
        for i in range(len(HANDS)):
            hand = new[HANDS[i]]
            #            self.hands[i].setPos(hand[0] - 1.8, hand[2], hand[1] - 0.7)
            self.hands[i].setPos(hand[0] + self.offset[0], hand[2], hand[1] + self.offset[1])
            boxPos = self.boxes[i].getPos()
            self.partsys[i].getNode().setPos(boxPos)

        gm = self.pose.modifyGeom(0)
        vdata = gm.modifyVertexData()
        vt = GeomVertexRewriter(vdata, 'vertex')
        for i in range(POSE_LEN):
            vt.setRow(i)
            vt.setData3f(old[i][0] + self.offset[0], old[i][2], old[i][1] + self.offset[1])
            vt.setRow(i + POSE_LEN)
            vt.setData3f(new[i][0] + self.offset[0], new[i][2], new[i][1] + self.offset[1])

        return

    def getNP(self):
        return self.np

    def makeRope(self, info, anchor, box):
        res = 9
        p1 = Point3(0, 0, 0)
        p2 = Point3(0, 0, -1)
        fixeds = 0

        bodyNode = BulletSoftBodyNode.makeRope(info, p1, p2, res, fixeds)
        bodyNode.setTotalMass(6.0)
        #        bodyNP = self.parent.render.attachNewNode(bodyNode)
        bodyNP = self.ropeNP.attachNewNode(bodyNode)
        self.parent.world.attachSoftBody(bodyNode)

        curve = NurbsCurveEvaluator()
        curve.reset(res + 2)

        bodyNode.linkCurve(curve)

        visNode = RopeNode('rope')
        visNode.setCurve(curve)
        visNode.setRenderMode(RopeNode.RMTape)
        #        visNode.setRenderMode(RopeNode.RMThread)
        visNode.setNormalMode(RopeNode.NMVertex)
        visNode.setUvMode(RopeNode.UVParametric)
        # visNode.setUvMode(RopeNode.UVDistance2)
        visNode.setNumSubdiv(4)
        visNode.setNumSlices(8)
        visNode.setThickness(0.03)
        #        visNP = self.parent.render.attachNewNode(visNode)
        visNP = self.ropeNP.attachNewNode(visNode)
        visNP.setColor(1.0, 0.1, 0.1, 0.9)
        #        visNP.setLightOff()
        #        visNP.setTexture(tex)
        idx = 0
        bodyNode.appendAnchor(idx, anchor.node())
        bodyNode.appendAnchor(bodyNode.getNumNodes() - 1, box.node())
        return visNP

    def makePose(self):
        fmt = GeomVertexFormat.getV3n3c4()
        vdata = GeomVertexData('line', fmt, Geom.UHStatic)
        vdata.setNumRows(2)
        vertex = GeomVertexWriter(vdata, 'vertex')
        normal = GeomVertexWriter(vdata, 'normal')
        color = GeomVertexWriter(vdata, 'color')

        for i in range(POSE_LEN):
            vertex.addData3f(0, 0, 0)
            color.addData4f(0.6, 0.6, 0.6, 0.8)
            normal.addData3f(0, 0, 1)

        for j in range(POSE_LEN):
            vertex.addData3f(0, 0, 0)
            color.addData4f(0.8, 0.8, 0.8, 1.0)
            normal.addData3f(0, 1, 0)

        geom = Geom(vdata)

        for k in range(POSE_LEN):
            prim = GeomLinestrips(Geom.UHStatic)
            prim.addVertices(k, k + POSE_LEN)
            prim.closePrimitive()
            geom.addPrimitive(prim)

        pose = GeomNode('poseflow')
        pose.addGeom(geom)
        return pose
