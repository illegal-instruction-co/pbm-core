import cv2
import time
import json
import numpy as np
import os
import hashlib
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from pbm import config, camera, roi, normalize, layers, shift, decision, features

class VerificationSession:
    def __init__(self):
        print("Initializing PBM Verification Tool...")
        try:
            self.cam = camera.Camera()
        except Exception as e:
            print(f"Error: {e}")
            self.cam = None

        self.qr_detector = cv2.QRCodeDetector()
        self.engine = decision.DecisionEngine()
        self.state = "SCANNING_QR"
        self.claimed_identity = None
        self.claimed_hash = None
        self.feature_samples = []
        self.REQUIRED_SAMPLES = 10
        self.final_result = "UNKNOWN"
        print("Press 'q' to quit. Press 'r' to reset.")

    def compare_features(self, measured, claimed):
        if measured is None or claimed is None:
            return False
            
        keys = ["f1", "a1", "f2", "a2", "rel_angle"]
        for k in keys:
            if k not in measured or k not in claimed:
                continue
            d = abs(measured[k] - claimed[k])
            limit = 10.0 if "a" in k else 20.0
            if d > limit:
                return False
        return True

    def process_frame(self, frame):
        roi_cnt = roi.find_roi(frame)
        if roi_cnt is None:
            self.engine.update(0, 0, 0)
            return None, None, "UNDECIDABLE"

        norm_img = normalize.normalize_roi(frame, roi_cnt)
        if norm_img is None:
            self.engine.update(0, 0, 0)
            return roi_cnt, None, "UNDECIDABLE"

        img_a, img_b = layers.separate_layers_fft(norm_img)
        if img_a is None or img_b is None:
            self.engine.update(0, 0, 0)
            return roi_cnt, norm_img, "UNDECIDABLE"

        dx, dy, conf = shift.compute_shift(img_a, img_b)
        decision_val = self.engine.update(dx, dy, conf)
        return roi_cnt, norm_img, decision_val

    def _verify_signature_and_hash(self, text, display_frame):
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return

        if "sig" not in payload or "data" not in payload:
            if "fp" in payload:
                print("Legacy/Unsigned QR Code detected. Rejecting.")
            return

        data = payload["data"]
        sig_hex = payload["sig"]
        
        try:
            with open("public_key.pem", "rb") as key_file:
                public_key = serialization.load_pem_public_key(key_file.read())
            
            signature = bytes.fromhex(sig_hex)
            json_data = json.dumps(data, sort_keys=True)
            public_key.verify(signature, json_data.encode())
            print("Signature Verified.")
            
            fp = data["fp"]
            claimed_id = data["id"]
            id_str = json.dumps(fp, sort_keys=True)
            recomputed_hash = hashlib.sha256(id_str.encode()).hexdigest()[:16]
            
            if recomputed_hash == claimed_id:
                print("Hash integrity verified.")
                self.claimed_identity = fp
                self.claimed_hash = claimed_id
                self.state = "LIVENESS_CHECK"
                self.engine = decision.DecisionEngine()
            else:
                print(f"Hash Mismatch! Claimed: {claimed_id}, Recomputed: {recomputed_hash}")
                cv2.putText(display_frame, "Integrity Error", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        except FileNotFoundError:
            print("ERROR: public_key.pem not found.")
        except Exception as e:
            print(f"Verification Failed: {e}")
            cv2.putText(display_frame, "INVALID SIG", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    def _handle_scanning_qr(self, display_frame, frame, **kwargs):
        cv2.putText(display_frame, "STEP 1: SCAN QR", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        text, points, _ = self.qr_detector.detectAndDecode(frame)
        if points is not None:
            points = points.astype(int)
            for i in range(len(points)):
                pt1 = tuple(points[i][0])
                pt2 = tuple(points[(i+1) % len(points)][0])
                cv2.line(display_frame, pt1, pt2, (255, 0, 0), 3)
        if text:
            self._verify_signature_and_hash(text, display_frame)

    def _handle_liveness(self, display_frame, decision_val, **kwargs):
        cv2.putText(display_frame, f"CHECKING PHY: {decision_val}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        if decision_val == "VALID_3D":
            self.state = "VERIFYING_IDENTITY"
            self.feature_samples = []

    def _handle_verifying(self, display_frame, norm_img, **kwargs):
        cv2.putText(display_frame, "MEASURING FINGERPRINT...", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        if norm_img is not None:
            feats = features.extract_features(norm_img)
            if feats:
                self.feature_samples.append(feats)
        
        if len(self.feature_samples) >= self.REQUIRED_SAMPLES:
            measured_identity, _ = features.compute_fingerprint(self.feature_samples)
            match = self.compare_features(measured_identity, self.claimed_identity)
            self.final_result = "GENUINE" if match else "MISMATCH"
            self.state = "RESULT"

    def _handle_result(self, display_frame, **kwargs):
        color = (0, 255, 0) if self.final_result == "GENUINE" else (0, 0, 255)
        cv2.putText(display_frame, f"RESULT: {self.final_result}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 4)
        cv2.putText(display_frame, f"ID: {self.claimed_hash}", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    def _step(self):
        frame = self.cam.get_frame()
        if frame is None:
            return False

        display_frame = frame.copy()
        roi_cnt, norm_img, decision_val = self.process_frame(frame)

        if self.state == "SCANNING_QR":
            self._handle_scanning_qr(display_frame=display_frame, frame=frame)
        elif self.state == "LIVENESS_CHECK":
            self._handle_liveness(display_frame=display_frame, decision_val=decision_val)
        elif self.state == "VERIFYING_IDENTITY":
            self._handle_verifying(display_frame=display_frame, norm_img=norm_img)
        elif self.state == "RESULT":
            self._handle_result(display_frame=display_frame)

        if roi_cnt is not None:
            cv2.polylines(display_frame, [roi_cnt], True, (0, 255, 0), 2)

        cv2.imshow("Verification", display_frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            return False
        if key == ord('r'):
            self.state = "SCANNING_QR"
            self.claimed_identity = None
            self.feature_samples = []
        return True

    def run(self):
        if not self.cam:
            return
        while self._step():
            pass
        self.cam.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    VerificationSession().run()
