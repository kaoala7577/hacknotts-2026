from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QWidget, QPushButton, QLineEdit
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt
from PyQt6 import uic
import os
import sys
import numpy as np

from workers import CameraWorker

REQUIRED_TAKES = 3

class AddSignView(QDialog): 
	def __init__(self, db_manager, cv_engine): 
		super().__init__()

		# auto load the UI file
		ui_path = os.path.abspath(os.curdir) + "/scripts/ui/design/add_sign.ui"
		uic.loadUi(str(ui_path), self)

		self.db_manager = db_manager
		self.cv_engine = cv_engine

		self.recorded_takes = 0
		self.recorded_frames = [[] for _ in range(REQUIRED_TAKES)]
		self.is_recording = False

		# multithreading for webcam
		self.camera_worker = CameraWorker(camera_index=0, cv_engine=self.cv_engine)
		self.camera_worker.frame_ready.connect(self.update_frame)
		self.camera_worker.landmark_ready.connect(self.handle_landmarks)
		self.camera_worker.start()

		# buttons
		self.recordButton.clicked.connect(self.toggle_recording)
		self.retryButton.clicked.connect(self.retry_take)
		self.saveButton.clicked.connect(self.save_new_sign)
		self.exitButton.clicked.connect(self.close)

	def update_frame(self, image: QImage) -> None:
		"""
		updates graphicView element to show webcam footage

		Args:
			image (QImage): webcam frame as a QImage
		"""
		pixmap = QPixmap.fromImage(image)
		# this scales it wrong but it works for now, will fix later
		scaled = pixmap.scaled(
			self.graphicsView.size(),
			Qt.AspectRatioMode.KeepAspectRatio,
			Qt.TransformationMode.SmoothTransformation
		)
		self.graphicsView.setPixmap(scaled)

	def handle_landmarks(self, landmarks: np.ndarray) -> None:
		"""
		handles the hand landmarks from the webcam feed

		Args:
			landmarks (np.ndarray): latest hand landmarks
		"""
		print(f"Landmarks received: {landmarks.shape if landmarks.size > 0 else 'No landmarks'}")
		if self.is_recording and self.recorded_takes < REQUIRED_TAKES:
			if np.any(landmarks != 0.0):
				self.recorded_frames[self.recorded_takes].append(landmarks)
				print(f"{self.recorded_takes}: {len(self.recorded_frames[self.recorded_takes])} frames")

	def toggle_recording(self) -> None:
		"""
		toggles recording state and updates webcam helper + ui accordingly

		Args:
			landmarks (np.ndarray): latest hand landmarks from the webcam feed
		"""
		
		if self.is_recording:
			self.is_recording = False
			self.camera_worker.stop_recording()
			print(self.recorded_frames)

			self.recordButton.setText("Record")

			self.recorded_takes += 1
			if self.recorded_takes < REQUIRED_TAKES:
				self.status.setText(f"Recorded {self.recorded_takes}/{REQUIRED_TAKES} takes!")
			else:
				self.status.setText("Ready to save!")
		else:
			if self.recorded_takes >= REQUIRED_TAKES:
				self.status.setText(f"Already recorded {REQUIRED_TAKES} takes!")
				return
			
			sign_name = self.lineEdit.text().strip()
			if not sign_name:
				self.status.setText("Enter a sign name first!")
				return
			
			self.is_recording = True
			self.camera_worker.record()

			self.recordButton.setText("Stop Recording")
			self.status.setText(f"Recording sign '{sign_name}'...")

	def evaluate_verification_take(self) -> None: pass 

	def retry_take(self) -> None: 
		print(self.recorded_takes)
		if self.recorded_frames[self.recorded_takes - 1]:
			self.recorded_takes -= 1
			self.recorded_frames[self.recorded_takes].clear()
			self.status.setText("Last take cleared!")
			print(self.recorded_takes)

	def save_new_sign(self) -> None: 
		"""
		push landmarks and sign name to database
		"""
		if self.is_recording:
			self.status.setText("Stop recording first!")
			return

		if self.recorded_takes < REQUIRED_TAKES:
			self.status.setText(f"Must record {REQUIRED_TAKES} takes before saving!")
			return

		sign_name = self.lineEdit.text().strip()
		if not sign_name:
			self.status.setText("Enter a sign name first!")
			return
		
		if not self.recorded_frames:
			self.status.setText("Nothing to save!")
			return

		word_obj = self.db_manager.get_word(sign_name)
		if word_obj is None:
			self.db_manager.add_word(sign_name)
			word_obj = self.db_manager.get_word(sign_name)

		if not word_obj:
			self.status.setText(f"Failed to add sign '{sign_name}' to database.")
			return

		sign_id = self.db_manager.add_sign_variation(word_obj.get_id())

		for take in self.recorded_frames:
			take_array = np.array(take, dtype=np.float32)
			landmark_blob = take_array.tobytes()
			self.db_manager.add_sign_reference(sign_id, landmark_blob)

		self.status.setText(f"Sign '{sign_name}' saved successfully!")
		self.lineEdit.clear()
		self.recorded_frames = [[] for _ in range(REQUIRED_TAKES)]
		self.recorded_takes = 0

	def closeEvent(self, event) -> None:
		if self.camera_worker.is_running:
			self.camera_worker.stop()
			event.accept()

		super().closeEvent(event)