import cv2
import json
import numpy as np
import collections
from cryptography.hazmat.primitives import serialization
from pbm import camera, roi, normalize, layers, decision, features, config
from pbm.pbm_scale import compute_pbm_scale
class VerificationSession:
    def __init__(self):
        self.cam = camera.Camera()
        self.engine = decision.DecisionEngine()
        self.qr = cv2.QRCodeDetector()
        self.state = "SCAN"
        self.features = []
        self.claimed = None
        self.parallax = []
        self.areas = []
    def _decode_qr(self, frame):
        if isinstance(self.qr, cv2.wechat_qrcode_WeChatQRCode):
            res, _ = self.qr.detectAndDecode(frame)
            return res[0] if res else ""
        text, _, _ = self.qr.detectAndDecode(frame)
        return text
    def _verify_qr_payload(self, text):
        payload = json.loads(text)
        with open("public_key.pem", "rb") as f:
            k = serialization.load_pem_public_key(f.read())
        s = json.dumps(payload["data"], sort_keys=True)
        k.verify(bytes.fromhex(payload["sig"]), s.encode())
        self.claimed = payload["data"]["fp"]
        self.state = "MEASURE"
    def _handle_scan_state(self, frame, display):
        cv2.putText(display, "STEP 1: SCAN QR", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        try:
            text = self._decode_qr(frame)
            if text: self._verify_qr_payload(text)
        except Exception:
            cv2.putText(display, "INVALID QR/SIG", (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow("Verify", display)
        return True
    def _draw_measurement_feedback(self, display, roi_cnt, decision_val):
        cv2.polylines(display, [roi_cnt], True, (0, 255, 0), 2)
        cv2.putText(display, f"LIVENESS: {decision_val}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        cv2.putText(display, f"MEASURING: {len(self.features)}/10", (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    def _compare_features(self, measured):
        diffs = {}
        for k in ["f1", "f2", "rel_angle"]:
            if k not in measured: continue
            diff = abs(measured[k] - self.claimed[k])
            if k == "rel_angle":
                if diff > 90: diff = 180 - diff
                limit = 5.0
            else:
                limit = 0.02
            diffs[k] = (diff, diff < limit)
        return diffs
    def _display_final_result(self, display, final_gen, scale_diff, scale_limit, diffs):
        print(f"DEBUG: Scale Diff: {scale_diff:.6f} (Limit: {scale_limit})")
        for k, (d, ok) in diffs.items():
            print(f"  {k}: {d:.4f} {'[OK]' if ok else '[FAIL]'}")
        res_txt = "GENUINE" if final_gen else "MISMATCH"
        color = (0, 255, 0) if final_gen else (0, 0, 255)
        cv2.putText(display, res_txt, (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 2, color, 4)
        cv2.imshow("Verify", display)
        cv2.waitKey(3000)
    def _finalize_verification(self, display):
        pbm_measured = compute_pbm_scale(self.parallax, self.areas)
        scale_diff = abs(pbm_measured - self.claimed["pbm_scale"])
        measured, _ = features.compute_fingerprint(self.features, pbm_measured)
        diffs = self._compare_features(measured)
        feat_ok = all(ok for _, ok in diffs.values())
        scale_limit = config.PBM_SCALE_EPS
        scale_ok = scale_diff < scale_limit
        final_gen = scale_ok and feat_ok
        self._display_final_result(display, final_gen, scale_diff, scale_limit, diffs)
        return False
    def _handle_measure_state(self, frame, display):
        roi_cnt = roi.find_roi(frame)
        if roi_cnt is None:
            self.engine.update(0, 0, 0, 0, 0)
            cv2.putText(display, "ALIGN PRODUCT", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
            cv2.imshow("Verify", display)
            return True
        norm = normalize.normalize_roi(frame, roi_cnt)
        dnx, dny, dfx, dfy, conf = layers.calculate_parallax_shift(norm)
        decision_val = self.engine.update(dnx, dny, dfx, dfy, conf)
        diff_mag = ((dnx - dfx)**2 + (dny - dfy)**2)**0.5
        self.parallax.append(diff_mag)
        self.areas.append(cv2.contourArea(roi_cnt))
        self._draw_measurement_feedback(display, roi_cnt, decision_val)
        if decision_val == "VALID_3D":
            feat = features.extract_features(norm)
            if feat: self.features.append(feat)
        if len(self.features) >= 10:
            return self._finalize_verification(display)
        cv2.imshow("Verify", display)
        return True
    def step(self):
        frame = self.cam.get_frame()
        if frame is None: return False
        display = frame.copy()
        if self.state == "SCAN":
            return self._handle_scan_state(frame, display)
        return self._handle_measure_state(frame, display)
    def run(self):
        while self.step():
            if cv2.waitKey(1) & 0xFF == ord("q"): break
        self.cam.release()
        cv2.destroyAllWindows()
if __name__ == "__main__":
    VerificationSession().run()
