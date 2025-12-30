import cv2
import numpy as np
from . import config

def draw_hud(frame, roi_contour, decision, metrics):
    dx, dy, mag, conf, mean_mag, std_mag = metrics
    
    if roi_contour is not None:
        cv2.polylines(frame, [roi_contour], True, (0, 255, 255), 2)
    
    status_text = f"STATUS: {decision}"
    color_map = {
        "VALID_3D": (0, 255, 0),
        "INVALID_2D": (0, 0, 255)
    }
    draw_color = color_map.get(decision, (0, 255, 255))
        
    cv2.putText(frame, status_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                1.2, draw_color, 3)

    lines = [
        f"Shift dX, dY: {dx:.2f}, {dy:.2f}",
        f"Mag: {mag:.2f} px",
        f"Conf: {conf:.2f}",
        f"Stab(Mean/Std): {mean_mag:.2f} / {std_mag:.2f}"
    ]
    
    y = 90
    for line in lines:
        cv2.putText(frame, line, (20, y), cv2.FONT_HERSHEY_SIMPLEX, 
                    config.FONT_SCALE, (200, 200, 200), 2)
        y += 30

    return frame

def draw_debug(norm_img, img_a, img_b):
    if norm_img is None:
        return np.zeros((config.CANONICAL_SIZE, config.CANONICAL_SIZE), dtype=np.uint8)
    
    if len(norm_img.shape) == 3:
        norm_gray = cv2.cvtColor(norm_img, cv2.COLOR_BGR2GRAY)
    else:
        norm_gray = norm_img
        
    if img_a is None:
        img_a = np.zeros_like(norm_gray)
    if img_b is None:
        img_b = np.zeros_like(norm_gray)
        
    top = norm_gray
    h, w = top.shape
    
    bottom_a = cv2.resize(img_a, (w//2, h//2))
    bottom_b = cv2.resize(img_b, (w//2, h//2))
    bottom = np.hstack([bottom_a, bottom_b])
    
    combined = np.vstack([top, bottom])
    
    cv2.putText(combined, "Normalized ROI", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 255, 2)
    cv2.putText(combined, "Layer A", (10, h + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 255, 2)
    cv2.putText(combined, "Layer B", (w//2 + 10, h + 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, 255, 2)
    
    return combined
