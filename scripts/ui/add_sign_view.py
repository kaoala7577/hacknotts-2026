from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt
from PyQt6 import uic
from pathlib import Path
import numpy as np

from .workers import CameraWorker

class AddSignView(QWidget): 
	def __init__(self, db_manager, cv_engine): 
		super().__init__()

		# auto load the UI file
		ui_path = Path(__file__).resolve().parent / "ui" / "design" / "add_sign.ui"
		uic.loadUi(str(ui_path), self)

		self.db_manager = db_manager
		self.cv_engine = cv_engine

		self.recorded_frames = [] # list of landmarks
		self.is_recording = False

		# multithreading for webcam
		self.camera_worker = CameraWorker(camera_index=0, cv_engine=self.cv_engine)
		self.camera_worker.frame_ready.connect(self.update_frame)
		self.camera_worker.start()

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

	def toggle_recording(self) -> None:
		"""
		toggles recording state and updates webcam helper + ui accordingly
		"""
		if self.is_recording:
			self.is_recording = False
			self.camera_worker.stop_recording()

			self.recorded_frames.append(self.camera_worker.landmark_ready)

			self.recordButton.setText("Record")
			self.status.setText("Ready to save!")
		else:
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
		if self.recorded_frames:
			self.recorded_frames.pop()
		self.status.setText("Last take cleared!")

	def save_new_sign(self) -> None: 
		"""
		push landmarks and sign name to database
		"""
		sign_name = self.lineEdit.text().strip()
		if not sign_name:
			self.status.setText("Enter a sign name first!")
			return
		
		if not self.recorded_frames:
			self.status.setText("Nothing to save!")
			return

		sequence = np.array(self.recorded_frames, dtype=np.float32)

		if not self.db_manager.get_word(sign_name):
			self.db_manager.add_word(sign_name)
		
		self.db_manager.save_sign_variation(sign_name, sequence)

		self.status.setText(f"Sign '{sign_name}' saved successfully!")
		self.lineEdit.clear()
		self.recorded_frames.clear()

	def closeEvent(self, event) -> None:
		if self.camera_worker.is_running:
			self.camera_worker.stop()
			event.accept()

		super().closeEvent(event)