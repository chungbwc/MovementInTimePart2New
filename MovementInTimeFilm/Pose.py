import mediapipe as mp
import cv2
import numpy as np

from Flow import Flow
from Grid import Grid

BG = (0, 0, 0, 0)
THRESHOLD = 0.2
POSE_LEN = 33
DIM = 3
FRAMES = 10
WAIT = 2

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


class Pose:

    def __init__(self):
        self.first = True
        self.old = None
        self.new = None
        self.mask = None
        self.image = None
        self.pose = mp_pose.Pose(
            model_complexity=1,
            smooth_landmarks=True,
            enable_segmentation=True,
            smooth_segmentation=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.flows = Flow(POSE_LEN)
        self.display = None
        self.motion = Grid(FRAMES, DIM)
        self.tracking = False
        self.cnt = 0
        return

    def setDisplay(self, fd):
        self.display = fd
        return

    def track(self, f):
        rgb = cv2.cvtColor(f, cv2.COLOR_BGRA2RGB)
        result = self.pose.process(rgb)
        self.image = f.copy()
        if result.pose_landmarks:
            #            mp_drawing.draw_landmarks(
            #                self.image,
            #                result.pose_landmarks,
            #                mp_pose.POSE_CONNECTIONS,
            #                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

            self.mask = f.copy()
            condition = np.stack((result.segmentation_mask,) * 4, axis=-1) > 0.5
            bg_image = np.zeros(f.shape, dtype=np.uint8)
            bg_image[:] = BG
            self.image = np.where(condition, self.mask, bg_image)

        if result.pose_world_landmarks:
            if self.isVisible(result.pose_world_landmarks.landmark):
                self.tracking = True
                self.flows.update(result.pose_world_landmarks.landmark)
                self.display.update(self.flows.getPrev(), self.flows.getCurr())
                if self.cnt == 0:
                    self.motion.update(self.flows.getPrev(), self.flows.getFlows())
                self.cnt = self.cnt + 1
                self.cnt = self.cnt % WAIT
            else:
                self.flows.clear()
                self.motion.clear()
                self.tracking = False
        else:
            self.flows.clear()
            #            self.motion.update(self.flows.getPrev(), self.flows.getFlows())
            self.motion.clear()
            self.tracking = False
        return

    def getDrawing(self):
        return self.image

    def getImage(self):
        return self.image

    def getMask(self):
        return self.mask

    def isVisible(self, lms):
        visible = True
        for lm in lms:
            if lm.visibility < THRESHOLD:
                visible = False
                break
        return visible

    def isTracking(self):
        return self.tracking

    def getPoseLength(self):
        return POSE_LEN

    def getMotion(self):
        return self.motion.getMotion()

    def getFrames(self):
        return FRAMES

    def getGridSize(self):
        return [DIM, DIM]
