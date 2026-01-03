import cv2
import numpy as np
from . import config
def calculate_parallax_shift(img):
    if img is None:
        return 0, 0, 0, 0, 0
    if len(img.shape) == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    rows, cols = img.shape
    hann_row = np.hanning(rows)
    hann_col = np.hanning(cols)
    window = hann_row[:, np.newaxis] * hann_col[np.newaxis, :]
    img_float = img.astype(np.float32) * window
    f = np.fft.fft2(img_float)
    f_shift = np.fft.fftshift(f)
    crow, ccol = rows // 2, cols // 2
    y, x = np.ogrid[-crow:rows-crow, -ccol:cols-ccol]
    mask_near = (x**2 + y**2 <= config.GRID_FREQ_MAX**2) & (x**2 + y**2 > config.FREQ_SPLIT_PX**2)
    mask_far = (x**2 + y**2 <= config.FREQ_SPLIT_PX**2) & (x**2 + y**2 > config.GRID_FREQ_MIN**2)
    def get_layer_shift(mask):
        f_layer = f_shift * mask
        psd = np.abs(np.fft.ifftshift(f_layer))**2
        autocorr = np.fft.ifft2(psd)
        autocorr = np.abs(np.fft.fftshift(autocorr))
        cv2.circle(autocorr, (ccol, crow), config.PEAK_MASK_RADIUS, 0, -1)
        _, max_val, _, max_loc = cv2.minMaxLoc(autocorr)
        mean_val = np.mean(autocorr)
        if mean_val == 0: mean_val = 1e-5
        conf = min(1.0, (max_val / mean_val) / 100.0)
        dx = max_loc[0] - ccol
        dy = max_loc[1] - crow
        return float(dx), float(dy), float(conf)
    dnx, dny, c_n = get_layer_shift(mask_near)
    dfx, dfy, c_f = get_layer_shift(mask_far)
    return dnx, dny, dfx, dfy, (c_n + c_f) / 2.0
