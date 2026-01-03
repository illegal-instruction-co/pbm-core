import cv2
import numpy as np

def compute_shift(img_a, img_b):
    if img_a is None or img_b is None:
        return 0.0, 0.0, 0.0

    ia = np.float32(img_a)
    ib = np.float32(img_b)
    
    window = cv2.createHanningWindow((ia.shape[1], ia.shape[0]), cv2.CV_32F)
    
    (dx, dy), response = cv2.phaseCorrelate(ia, ib, window)
    
    return dx, dy, response
