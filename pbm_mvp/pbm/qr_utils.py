import cv2
import numpy as np
from . import config

def compute_pixels_per_mm(frame, qr_detector):
    if isinstance(qr_detector, cv2.wechat_qrcode_WeChatQRCode):
        res, points = qr_detector.detectAndDecode(frame)
        if not res or points is None:
            return None
        pts = np.array(points[0])
    else:
        _, points, _ = qr_detector.detectAndDecode(frame)
        if points is None:
            return None
        pts = np.array(points[0])

    if pts.shape[0] != 4:
        return None

    w_px = np.linalg.norm(pts[0] - pts[1])
    if w_px <= 0:
        return None

    return w_px / config.QR_REAL_WIDTH_MM
