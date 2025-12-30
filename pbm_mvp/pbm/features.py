import numpy as np
import hashlib
import json
import cv2
from . import layers, normalize

def extract_features(norm_img):
    if norm_img is None:
        return None
        
    if len(norm_img.shape) == 3:
        img_gray = cv2.cvtColor(norm_img, cv2.COLOR_BGR2GRAY)
    else:
        img_gray = norm_img

    f = np.fft.fft2(img_gray)
    fshift = np.fft.fftshift(f)
    mag = np.abs(fshift)
    
    rows, cols = img_gray.shape
    crow, ccol = rows // 2, cols // 2
    
    cv2.circle(mag, (ccol, crow), 15, 0, -1)
    
    flat_indices = np.argsort(mag.ravel())[::-1]
    peak_locs = []
    
    for idx in flat_indices[:500]:
        y, x = np.unravel_index(idx, mag.shape)
        dist = np.sqrt((x - ccol)**2 + (y - crow)**2)
        
        if dist < 20 or dist > 200:
            continue
            
        is_distinct = True
        for px, py in peak_locs:
             if np.sqrt((x - px)**2 + (y - py)**2) < 15:
                 is_distinct = False
                 break
        
        if is_distinct:
            peak_locs.append((x, y))
            if len(peak_locs) >= 2:
                break
                
    if len(peak_locs) < 2:
        return None
        
    p1 = peak_locs[0]
    p2 = peak_locs[1]
    
    d1 = np.sqrt((p1[0] - ccol)**2 + (p1[1] - crow)**2)
    d2 = np.sqrt((p2[0] - ccol)**2 + (p2[1] - crow)**2)
    
    peaks = [(p1, d1), (p2, d2)]
    peaks.sort(key=lambda x: x[1])
    
    (pA, dA) = peaks[0]
    (pB, dB) = peaks[1]
    
    angleA = np.degrees(np.arctan2(pA[1] - crow, pA[0] - ccol))
    angleB = np.degrees(np.arctan2(pB[1] - crow, pB[0] - ccol))
    
    angleA = angleA % 180
    angleB = angleB % 180
    
    features = {
        "f1": float(dA),
        "a1": float(angleA),
        "f2": float(dB),
        "a2": float(angleB),
        "rel_angle": float(abs(angleA - angleB))
    }
    
    return features

def compute_fingerprint(feature_history):
    if not feature_history:
        return None, None
        
    avg_f = {}
    keys = feature_history[0].keys()
    
    for k in keys:
        vals = [f[k] for f in feature_history]
        avg_f[k] = np.mean(vals)
        
    identity_data = {k: round(v, 2) for k, v in avg_f.items()}
    
    id_str = json.dumps(identity_data, sort_keys=True)
    f_hash = hashlib.sha256(id_str.encode()).hexdigest()[:16]
    
    return identity_data, f_hash
