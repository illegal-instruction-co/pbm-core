import numpy as np
import hashlib
import json
import cv2

def _get_peak_locs(mag, ccol, crow, limit=500, min_dist=20, max_dist=200):
    """Helper to find the top peaks that satisfy distance constraints."""
    flat_indices = np.argsort(mag.ravel())[::-1]
    peak_locs = []

    for idx in flat_indices[:limit]:
        y, x = np.unravel_index(idx, mag.shape)
        dist = np.sqrt((x - ccol) ** 2 + (y - crow) ** 2)

        if not (min_dist <= dist <= max_dist):
            continue

        if all(np.sqrt((x - px) ** 2 + (y - py) ** 2) >= 15 for px, py in peak_locs):
            peak_locs.append((x, y))
            if len(peak_locs) >= 2:
                break
    return peak_locs

def extract_features(norm_img):
    if norm_img is None:
        return None

    img_gray = cv2.cvtColor(norm_img, cv2.COLOR_BGR2GRAY) if len(norm_img.shape) == 3 else norm_img

    f = np.fft.fft2(img_gray)
    fshift = np.fft.fftshift(f)
    mag = np.abs(fshift)

    rows, cols = img_gray.shape
    crow, ccol = rows // 2, cols // 2

    cv2.circle(mag, (ccol, crow), 15, 0, -1)
    
    peak_locs = _get_peak_locs(mag, ccol, crow)

    if len(peak_locs) < 2:
        return None

    p1, p2 = peak_locs
    d1 = np.sqrt((p1[0] - ccol) ** 2 + (p1[1] - crow) ** 2) / cols
    d2 = np.sqrt((p2[0] - ccol) ** 2 + (p2[1] - crow) ** 2) / cols

    a1 = np.degrees(np.arctan2(p1[1] - crow, p1[0] - ccol)) % 180
    a2 = np.degrees(np.arctan2(p2[1] - crow, p2[0] - ccol)) % 180

    return {
        "f1": float(d1),
        "a1": float(a1),
        "f2": float(d2),
        "a2": float(a2),
        "rel_angle": float(abs(a1 - a2))
    }

def compute_fingerprint(history, pbm_scale):
    avg = {}
    for k in history[0].keys():
        avg[k] = np.mean([f[k] for f in history])

    avg["pbm_scale"] = pbm_scale

    identity = {k: round(v, 4) for k, v in avg.items()}

    s = json.dumps(identity, sort_keys=True)
    h = hashlib.sha256(s.encode()).hexdigest()[:16]

    return identity, h
