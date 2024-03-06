from panda3d.physics import *

from direct.particles.Particles import Particles
from direct.particles.ParticleEffect import ParticleEffect
from direct.particles.ForceGroup import *
import random
import os


class PartSystem:
    def __init__(self, label):
        self.p = ParticleEffect()
        self.p.reset()
        self.p.setPos(0, 0, 0)
        self.p.setHpr(0, 0, 0)
        self.p.setScale(1, 1, 1)
        self.label = label
        return

    def setup(self):
        p0 = Particles(self.label)
        # Particles parameters
        #        p0.setFactory("PointParticleFactory")
        p0.setFactory("ZSpinParticleFactory")
        #        p0.setRenderer("PointParticleRenderer")
        # p0.setRenderer("LineParticleRenderer")
        p0.setRenderer("SpriteParticleRenderer")
        #        p0.setEmitter("DiscEmitter")
        p0.setEmitter("PointEmitter")

        p0.setPoolSize(800)
        p0.setBirthRate(0.02)
        p0.setLitterSize(250)
        p0.setLitterSpread(100)
        p0.setLocalVelocityFlag(True)
        p0.setSystemGrowsOlderFlag(False)
        p0.setSystemLifespan(0)

        # Factory parameters
        p0.factory.setLifespanBase(1.2)
        p0.factory.setLifespanSpread(0.2)
        p0.factory.setMassBase(2.0)
        p0.factory.setMassSpread(0.01)
        p0.factory.setTerminalVelocityBase(120.0)
        p0.factory.setTerminalVelocitySpread(1.0)

        p0.factory.setInitialAngle(0)
        p0.factory.setInitialAngleSpread(30)
        p0.factory.setFinalAngle(180)
        p0.factory.setFinalAngleSpread(30)

        p0.renderer.setAlphaMode(BaseParticleRenderer.PR_ALPHA_IN_OUT)
        #        p0.renderer.setUserAlpha(0.9)
        # p0.renderer.setUserAlpha(True)
        #        p0.renderer.setPointSize(10.00)
        p0.renderer.setTexture(base.loader.loadTexture("data" +
                                                       os.path.sep + "image" + os.path.sep + "smoke.png"))
        p0.renderer.setColor(LVector4(1, 1, 1, 0.1))
        p0.renderer.setXScaleFlag(True)
        p0.renderer.setYScaleFlag(True)
        p0.renderer.setInitialXScale(0.005)
        p0.renderer.setFinalXScale(0.06)
        p0.renderer.setInitialYScale(0.005)
        p0.renderer.setFinalYScale(0.06)
        p0.renderer.setNonanimatedTheta(True)
        p0.renderer.setAlphaBlendMethod(BaseParticleRenderer.PP_BLEND_CUBIC)
        p0.renderer.setAlphaDisable(False)

        # col1 = LVector4(0.2, 0.2, 0.8, 0.6)
        # col2 = LVector4(0.5, 0.5, 0.5, 0.3)
        #        p0.renderer.setStartColor(col1)
        #        p0.renderer.setEndColor(col2)
        #        p0.renderer.setBlendType(PointParticleRenderer.PP_ONE_COLOR)
        #        p0.renderer.setBlendType(PointParticleRenderer.PP_BLEND_LIFE)
        #        p0.renderer.setBlendMethod(BaseParticleRenderer.PP_BLEND_CUBIC)
        # p0.renderer.setHeadColor(col1)
        # p0.renderer.setTailColor(col2)

        p0.emitter.setEmissionType(BaseParticleEmitter.ET_RADIATE)
        p0.emitter.setAmplitude(0.7)
        p0.emitter.setAmplitudeSpread(0.1)
        p0.emitter.setOffsetForce(LVector3(0, 0, 0.01))

        #        p0.emitter.setExplicitLaunchVector(LVector3(1.0000, 0.0000, 0.0000))
        p0.emitter.setRadiateOrigin(LPoint3(0, 0, 0))

        p0.emitter.setLocation(LPoint3(0, 0, 0))

        #        p0.emitter.setRadius(0.00300)
        #        p0.emitter.setOuterAngle(359)
        #        p0.emitter.setInnerAngle(0.0000)
        #        p0.emitter.setOuterMagnitude(1.0000)
        #        p0.emitter.setInnerMagnitude(0.2000)
        #        p0.emitter.setCubicLerping(False)
        self.p.addParticles(p0)

        f0 = ForceGroup('gravity')
        force0 = LinearVectorForce(LVector3(0, 0, -0.002), 20, True)
        force0.setActive(True)
        f0.addForce(force0)
        force1 = LinearJitterForce(1.5, True)
        force1.setActive(True)
        f0.addForce(force1)

        force2 = LinearCylinderVortexForce()
        force2.setVectorMasks(1, 1, 1)
        force2.setActive(True)
        f0.addForce(force2)

        self.p.addForceGroup(f0)
        return

    def getNode(self):
        return self.p
