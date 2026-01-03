import numpy as np

def compute_pbm_scale(parallax_history, roi_history):
    if not parallax_history or not roi_history:
        return None

    mean_parallax = np.mean(parallax_history)
    mean_area = np.mean(roi_history)

    if mean_area <= 0:
        return None

    return mean_parallax / np.sqrt(mean_area)