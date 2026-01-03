import numpy as np
import collections
from . import config
VALID_3D = "VALID_3D"
INVALID_2D = "INVALID_2D"
UNDECIDABLE = "UNDECIDABLE"
class DecisionEngine:
    def __init__(self):
        self.history = collections.deque(maxlen=config.DECISION_HISTORY_LEN)
    def update(self, dnx, dny, dfx, dfy, conf):
        self.history.append((dnx, dny, dfx, dfy, conf))
        return self._decide()
    def _decide(self):
        valid = [h for h in self.history if h[4] >= config.DECISION_MIN_CONF]
        if len(valid) < config.DECISION_HISTORY_LEN // 2:
            return UNDECIDABLE
        dnxs = np.array([h[0] for h in valid])
        dnys = np.array([h[1] for h in valid])
        dfxs = np.array([h[2] for h in valid])
        dfys = np.array([h[3] for h in valid])
        diff_x = dnxs - dfxs
        diff_y = dnys - dfys
        diff_vecs = np.stack([diff_x, diff_y], axis=1)
        diff_mags = np.linalg.norm(diff_vecs, axis=1)
        mean_diff = np.mean(diff_mags)
        norms = diff_mags.copy()
        norms[norms == 0] = 1e-6
        unit_vecs = diff_vecs / norms[:, None]
        mean_dir = np.linalg.norm(np.mean(unit_vecs, axis=0))
        sign_consistency = np.mean(np.sign(diff_x) == np.sign(np.mean(diff_x)))
        mags_near = np.sqrt(dnxs**2 + dnys**2)
        gain = diff_mags / (mags_near + 1e-6)
        mean_gain = np.mean(gain)
        mag_swing = np.percentile(mags_near, 95) - np.percentile(mags_near, 5)
        if config.SHOW_DEBUG:
            print(f"LIVENESS -> Diff:{mean_diff:.2f} Dir:{mean_dir:.2f} Sgn:{sign_consistency:.2f} Gain:{mean_gain:.3f} Swg:{mag_swing:.1f}")
        if mag_swing < config.DECISION_MIN_MAG_SWING:
            return UNDECIDABLE
        if mean_diff < config.DIFFERENTIAL_MOTION_THRESHOLD:
            return INVALID_2D
        if mean_dir < config.DIRECTIONAL_COHERENCE_THRESHOLD:
            return INVALID_2D
        if sign_consistency < config.SIGN_CONSISTENCY_THRESHOLD:
            return INVALID_2D
        if mean_gain < config.PARALLAX_GAIN_THRESHOLD:
            return INVALID_2D
        return VALID_3D
    def get_metrics(self):
        if len(self.history) == 0:
            return 0.0, 0.0, 0.0
        m = np.array(list(self.history))
        mags = np.sqrt(m[:, 0]**2 + m[:, 1]**2)
        return np.mean(mags), np.std(mags), np.mean(m[:, 4])
