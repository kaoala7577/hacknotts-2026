from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage
import cv2
import numpy as np

class CameraWorker(QThread):
    frame_ready = pyqtSignal(QImage)
    landmark_ready = pyqtSignal(np.ndarray)

    def __init__(self, camera_index=0, cv_engine=None):
        super().__init__()
        self.camera_index = camera_index
        self.cv_engine = cv_engine
        self.is_running = False
        self.is_recording = False

    def record(self) -> None:
        self.is_recording = True

    def stop_recording(self) -> None:
        self.is_recording = False

    def run(self) -> None:
        self.is_running = True
        cap = cv2.VideoCapture(self.camera_index)

        if not cap.isOpened():
            raise RuntimeError(f"Could not open webcam at {self.camera_index}")
        
        while self.is_running:
            ret, frame = cap.read()
            if not ret:
                break

            # mirror the user
            frame = cv2.flip(frame, 1)

            # when recording, process hand positions
            if self.is_recording and self.cv_engine:
                landmarks = self.cv_engine.extract_landmarks(frame)
                if landmarks is not None:
                    self.landmark_ready.emit(landmarks)

            height, width, colours = frame.shape
            bytes_per_line = colours * width
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            qt_image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888).copy()

            self.frame_ready.emit(qt_image)

            # limit to 30 fps
            self.msleep(30)
        cap.release()

    def stop(self) -> None:
        self.is_running = False
        self.wait()