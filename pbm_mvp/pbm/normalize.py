import cv2
import numpy as np
from . import config

def order_points(pts):
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def normalize_roi(frame, contour):
    if contour is None:
        return None

    pts = contour.reshape(4, 2)
    rect = order_points(pts)

    dst = np.array([
        [0, 0],
        [config.CANONICAL_SIZE - 1, 0],
        [config.CANONICAL_SIZE - 1, config.CANONICAL_SIZE - 1],
        [0, config.CANONICAL_SIZE - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(frame, M, (config.CANONICAL_SIZE, config.CANONICAL_SIZE))

    return warped