import cv2
import numpy as np
from . import config

def calculate_parallax_shift(img):
    if img is None:
        return 0, 0, 0
        
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
    rows, cols = img.shape

    hann_row = np.hanning(rows)
    hann_col = np.hanning(cols)
    window = hann_row[:, np.newaxis] * hann_col[np.newaxis, :]
    img_float = img.astype(np.float32) * window

    f = np.fft.fft2(img_float)
    
    power_spectrum = np.abs(f)**2
    
    autocorr = np.fft.ifft2(power_spectrum)
    autocorr = np.abs(autocorr)

    autocorr_shifted = np.fft.fftshift(autocorr)
    
    crow, ccol = rows // 2, cols // 2

    mask_radius = config.PEAK_MASK_RADIUS * 2 
    cv2.circle(autocorr_shifted, (ccol, crow), mask_radius, 0, -1)
    
    _, max_val, _, max_loc = cv2.minMaxLoc(autocorr_shifted)
    
    mean_val = np.mean(autocorr_shifted)
    if mean_val == 0: mean_val = 1e-5
    confidence = max_val / mean_val
    
    confidence = min(1.0, confidence / 100.0) 

    peak_x, peak_y = max_loc
    
    dx = peak_x - ccol
    dy = peak_y - crow

    return float(dx), float(dy), float(confidence)
