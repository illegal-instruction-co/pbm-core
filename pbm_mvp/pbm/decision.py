import numpy as np
import collections
from . import config

VALID_3D = "VALID_3D"
INVALID_2D = "INVALID_2D"
UNDECIDABLE = "UNDECIDABLE"

class DecisionEngine:
    def __init__(self):
        self.history = collections.deque(maxlen=config.DECISION_HISTORY_LEN)
    
    def update(self, dx, dy, conf):
        mag = np.sqrt(dx**2 + dy**2)
        self.history.append((mag, conf))
        return self._decide()
        
    def _decide(self):
        if len(self.history) < config.DECISION_HISTORY_LEN:
            return UNDECIDABLE
        
        mags = [m for m, c in self.history]
        confs = [c for m, c in self.history]
        
        mean_mag = np.mean(mags)
        std_mag = np.std(mags)
        mean_conf = np.mean(confs)
        
        if mean_conf < config.DECISION_MIN_CONF:
            return UNDECIDABLE
            
        if mean_mag > config.DECISION_EPS_SHIFT_PX:
            if std_mag < config.DECISION_STABILITY_STD_MAX:
                return VALID_3D
            else:
                return UNDECIDABLE
        else:
            if mean_conf >= config.DECISION_MIN_CONF:
                return INVALID_2D
                
        return UNDECIDABLE

    def get_metrics(self):
        if len(self.history) == 0:
            return 0.0, 0.0, 0.0
        mags = [m for m, c in self.history]
        confs = [c for m, c in self.history]
        return np.mean(mags), np.std(mags), np.mean(confs)
