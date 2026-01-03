import cv2
from . import config

class Camera:
    def __init__(self, camera_index=config.CAMERA_INDEX):
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open camera {camera_index}")
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)
        
        ret, _ = self.cap.read()
        if not ret:
            raise RuntimeError(f"Camera {camera_index} opened but returned no frame")

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self):
        self.cap.release()
