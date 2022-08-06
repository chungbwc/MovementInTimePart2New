from panda3d.core import *
from panda3d.bullet import *

import numpy as np
import os
import random

HANDS = [15, 16]


class FlowDisplay:

    def __init__(self, pn, pr):
        self.pLength = pn
        self.np = NodePath("poseflow")
        self.np.setRenderModeThickness(2)
        self.np.setPos(0, 0, 0)
        self.np.setHpr(0, 0, 0)
        self.np.setScale(1, 1, 1)

        self.ropeNP = NodePath("ropes")
        self.ropeNP.reparentTo(self.np)
        self.ropeNP.setScale(1, 1, 1)

        self.parent = pr
        self.ropes = []
        self.hands = []

        self.setupRopes()
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

        for i in range((len(HANDS))):
            rope = self.makeRope(self.parent.worldInfo, self.hands[i])
            self.ropes.append(rope)
            self.hands[i].hide()
        return

    def update(self, old, new):
        for i in range(len(HANDS)):
            hand = new[HANDS[i]]
            #            self.hands[i].setPos(hand[0] - 1.8, hand[2], hand[1] - 0.7)
            self.hands[i].setPos(hand[0] + 2.0, hand[2], hand[1] + 0.8)
        return

    def getNP(self):
        return self.np

    def makeRope(self, info, anchor):
        res = 9
        p1 = Point3(0, 0, 0)
        p2 = Point3(0, 0, -1)
        fixeds = 0

        bodyNode = BulletSoftBodyNode.makeRope(info, p1, p2, res, fixeds)
        bodyNode.setTotalMass(5.0)
        #        bodyNP = self.parent.render.attachNewNode(bodyNode)
        bodyNP = self.ropeNP.attachNewNode(bodyNode)
        self.parent.world.attachSoftBody(bodyNode)

        curve = NurbsCurveEvaluator()
        curve.reset(res + 2)

        bodyNode.linkCurve(curve)

        visNode = RopeNode('rope')
        visNode.setCurve(curve)
        visNode.setRenderMode(RopeNode.RMTape)
        visNode.setNormalMode(RopeNode.NMVertex)
        visNode.setUvMode(RopeNode.UVParametric)
        # visNode.setUvMode(RopeNode.UVDistance2)
        visNode.setNumSubdiv(8)
        visNode.setNumSlices(16)
        visNode.setThickness(0.015)
        #        visNP = self.parent.render.attachNewNode(visNode)
        visNP = self.ropeNP.attachNewNode(visNode)
        visNP.setColor(random.random() / 2 + 0.5,
                       random.random() / 2 + 0.5,
                       random.random() / 2 + 0.5, 0.8)
        #        visNP.setLightOff()
        #        visNP.setTexture(tex)
        idx = 0
        bodyNode.appendAnchor(idx, anchor.node())
        return visNP
