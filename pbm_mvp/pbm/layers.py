import cv2
import numpy as np
from . import config

def separate_layers_fft(img):
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
    f = np.fft.fft2(img)
    fshift = np.fft.fftshift(f)
    
    rows, cols = img.shape
    crow, ccol = rows // 2, cols // 2
    
    mag_no_dc = np.abs(fshift).copy()
    cv2.circle(mag_no_dc, (ccol, crow), config.PEAK_MASK_RADIUS * 2, 0, -1)
    
    flat_indices = np.argsort(mag_no_dc.ravel())[::-1]
    
    peak_locs = []
    
    count = 0
    for idx in flat_indices[:500]:
        y, x = np.unravel_index(idx, mag_no_dc.shape)
        
        dist_from_dc = np.sqrt((x - ccol)**2 + (y - crow)**2)
        if dist_from_dc < config.GRID_FREQ_MIN or dist_from_dc > config.GRID_FREQ_MAX:
             continue
             
        is_distinct = True
        for (px, py) in peak_locs:
            if np.sqrt((x - px)**2 + (y - py)**2) < config.PEAK_MASK_RADIUS * 2:
                is_distinct = False
                break
        
        if is_distinct:
            peak_locs.append((x, y))
            count += 1
            if count >= 2:
                break
    
    if len(peak_locs) < 2:
        return None, None
        
    p1 = peak_locs[0]
    p2 = peak_locs[1]
    
    mask1 = np.zeros((rows, cols), np.uint8)
    mask2 = np.zeros((rows, cols), np.uint8)
    
    r = config.PEAK_MASK_RADIUS
    
    cv2.circle(mask1, p1, r, 1, -1)
    cv2.circle(mask1, (cols - p1[0], rows - p1[1]), r, 1, -1)
    
    cv2.circle(mask2, p2, r, 1, -1)
    cv2.circle(mask2, (cols - p2[0], rows - p2[1]), r, 1, -1)
    
    fshift1 = fshift * mask1
    fshift2 = fshift * mask2
    
    f_ishift1 = np.fft.ifftshift(fshift1)
    img_back1 = np.fft.ifft2(f_ishift1)
    img_back1 = np.abs(img_back1)
    
    f_ishift2 = np.fft.ifftshift(fshift2)
    img_back2 = np.fft.ifft2(f_ishift2)
    img_back2 = np.abs(img_back2)
    
    img_back1 = cv2.normalize(img_back1, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    img_back2 = cv2.normalize(img_back2, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    
    return img_back1, img_back2
