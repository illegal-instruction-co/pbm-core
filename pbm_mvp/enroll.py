import cv2
import time
import json
import numpy as np
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from pbm import config, camera, roi, normalize, layers, shift, decision, viz, features

class EnrollmentSession:
    def __init__(self):
        print("Initializing PBM Enrollment Tool...")
        print("Ensure the product is placed on a stable surface.")
        try:
            self.cam = camera.Camera()
        except Exception as e:
            print(f"Error: {e}")
            self.cam = None
            
        self.engine = decision.DecisionEngine()
        self.state = "SEARCHING"
        self.feature_samples = []
        self.REQUIRED_SAMPLES = 20
        print("Press 'q' to quit. Press 'r' to reset.")

    def sign_enrollment_data(self, identity_data, f_hash):
        data_payload = {
            "id": f_hash,
            "fp": identity_data
        }
        json_data = json.dumps(data_payload, sort_keys=True)
        try:
            with open("private_key.pem", "rb") as key_file:
                private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None
                )
            signature = private_key.sign(json_data.encode())
            return {
                "data": data_payload,
                "sig": signature.hex()
            }
        except FileNotFoundError:
            print("ERROR: private_key.pem not found. Cannot sign data.")
            print("Please run keygen.py first.")
        except Exception as e:
            print(f"ERROR: Signing failed: {e}")
        return None

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

    def _handle_searching(self, display_frame, roi_cnt, **kwargs):
        cv2.putText(display_frame, "ALIGN FRAME", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
        if roi_cnt is not None:
            self.state = "LIVENESS_CHECK"
            self.engine = decision.DecisionEngine()

    def _handle_liveness(self, display_frame, decision_val, **kwargs):
        cv2.putText(display_frame, f"CHECKING PHY: {decision_val}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        cv2.putText(display_frame, "MOVE CAMERA SLIGHTLY", (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)
        if decision_val == "VALID_3D":
            self.state = "CAPTURING_FEATURES"
            self.feature_samples = []

    def _handle_capturing(self, display_frame, norm_img, **kwargs):
        cv2.putText(display_frame, f"EXTRACTING: {len(self.feature_samples)}/{self.REQUIRED_SAMPLES}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(display_frame, "HOLD STILL", (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        if norm_img is not None:
            feats = features.extract_features(norm_img)
            if feats:
                self.feature_samples.append(feats)
        if len(self.feature_samples) >= self.REQUIRED_SAMPLES:
            self.state = "DONE"

    def _handle_done(self, display_frame, **kwargs):
        cv2.putText(display_frame, "ENROLLMENT COMPLETE", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
        cv2.imshow("Enrollment", display_frame)
        cv2.waitKey(1)
        identity_data, f_hash = features.compute_fingerprint(self.feature_samples)
        print("\n" + "="*40)
        print("ENROLLMENT SUCCESSFUL")
        print("="*40)
        print(f"Physical Fingerprint: {json.dumps(identity_data, indent=2)}")
        print(f"Fingerprint Hash: {f_hash}")
        print("-" * 40)
        print("DATA FOR QR CODE GENERATION:")
        qr_output = self.sign_enrollment_data(identity_data, f_hash)
        if qr_output:
            print(json.dumps(qr_output))
        print("="*40 + "\n")
        cv2.waitKey(3000)
        return True

    def _step(self):
        frame = self.cam.get_frame()
        if frame is None:
            return False

        display_frame = frame.copy()
        roi_cnt, norm_img, decision_val = self.process_frame(frame)
        
        handler_name = self.state
        if handler_name == "SEARCHING":
            self._handle_searching(display_frame, roi_cnt)
        elif handler_name == "LIVENESS_CHECK":
            self._handle_liveness(display_frame, decision_val)
        elif handler_name == "CAPTURING_FEATURES":
            self._handle_capturing(display_frame, norm_img)
        elif handler_name == "DONE":
            if self._handle_done(display_frame):
                return False

        if roi_cnt is not None:
            cv2.polylines(display_frame, [roi_cnt], True, (0, 255, 0), 2)
        
        cv2.imshow("Enrollment", display_frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            return False
        if key == ord('r'):
            self.state = "SEARCHING"
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
    EnrollmentSession().run()
