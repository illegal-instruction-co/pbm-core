import cv2
import numpy as np
from . import config

def find_roi(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(blurred, 50, 150)
    
    kernel = np.ones((3,3), np.uint8)
    edged = cv2.dilate(edged, kernel, iterations=1)

    contours, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    frame_area = frame.shape[0] * frame.shape[1]
    best_cnt = None
    max_area = 0
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < frame_area * config.ROI_MIN_AREA_RATIO or area > frame_area * config.ROI_MAX_AREA_RATIO:
            continue
            
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, config.ROI_RECT_CLOSENESS * peri, True)
        
        if len(approx) == 4 and cv2.isContourConvex(approx):
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = float(w)/h
            if abs(aspect_ratio - 1.0) < config.ROI_ASPECT_RATIO_TOLERANCE:
                if area > max_area:
                    max_area = area
                    best_cnt = approx

    return best_cnt
