import cv2
import json
import os
from cryptography.hazmat.primitives import serialization
from pbm import camera, roi, normalize, layers, decision, features
from pbm.pbm_scale import compute_pbm_scale

class EnrollmentSession:
    def __init__(self):
        self.cam = camera.Camera()
        self.engine = decision.DecisionEngine()
        self.state = "SEARCHING"
        self.features = []
        self.parallax = []
        self.areas = []
        self.REQ = 20

    def sign(self, data, hid):
        payload = {"id": hid, "fp": data}
        s = json.dumps(payload, sort_keys=True)
        with open("private_key.pem", "rb") as f:
            k = serialization.load_pem_private_key(f.read(), password=None)
        sig = k.sign(s.encode())
        return {"data": payload, "sig": sig.hex()}

    def step(self):
        try:
            frame = self.cam.get_frame()
            if frame is None: return False
            
            display = frame.copy()
            roi_cnt = roi.find_roi(frame)
            
            if roi_cnt is None:
                self.engine.update(0, 0, 0)
                cv2.putText(display, "ALIGN FRAME", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                cv2.imshow("Enrollment", display)
                return True

            norm = normalize.normalize_roi(frame, roi_cnt)
            dx, dy, conf = layers.calculate_parallax_shift(norm)
            decision_val = self.engine.update(dx, dy, conf)

            area = cv2.contourArea(roi_cnt)
            self.parallax.append((dx ** 2 + dy ** 2) ** 0.5)
            self.areas.append(area)

            # UI Feedback
            cv2.polylines(display, [roi_cnt], True, (0, 255, 0), 2)
            cv2.putText(display, f"LIVENESS: {decision_val}", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)
            cv2.putText(display, f"CAPTURED: {len(self.features)}/{self.REQ}", (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

            if decision_val == "VALID_3D":
                f = features.extract_features(norm)
                if f: self.features.append(f)

            if len(self.features) >= self.REQ:
                print("\nProcessing enrollment data...")
                pbm_scale = compute_pbm_scale(self.parallax, self.areas)
                identity, hid = features.compute_fingerprint(self.features, pbm_scale)
                qr_data = self.sign(identity, hid)
                
                import qrcode
                qr = qrcode.make(json.dumps(qr_data))
                os.makedirs("pattern_output", exist_ok=True)
                qr_path = "pattern_output/last_qr.png"
                qr.save(qr_path)
                
                print(f"SUCCESS! QR saved to {qr_path}")
                cv2.putText(display, "DONE! Check Console", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)
                cv2.imshow("Enrollment", display)
                cv2.waitKey(2000)
                return False

            cv2.imshow("Enrollment", display)
        except KeyboardInterrupt:
            return False
        return True

    def run(self):
        while self.step():
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        self.cam.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    EnrollmentSession().run()
