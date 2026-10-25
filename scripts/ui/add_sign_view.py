from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout, QWidget, QPushButton, QLineEdit
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt
from PyQt6 import uic
import os
import sys
import numpy as np

from cv_engine import SignPassMark
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

		self.verification_mode = False
		self.verification_frames = []

		# multithreading for webcam
		self.camera_worker = CameraWorker(camera_index=0, cv_engine=self.cv_engine)
		self.camera_worker.frame_ready.connect(self.update_frame)
		self.camera_worker.landmark_ready.connect(self.handle_landmarks)
		self.camera_worker.start()

		# buttons
		self.recordButton.clicked.connect(self.toggle_recording)
		self.retryButton.clicked.connect(self.retry_take)
		self.saveButton.clicked.connect(self.verify_sign)
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
		if self.is_recording:
			if np.any(landmarks != 0.0):
				if self.verification_mode:
					self.verification_frames.append(landmarks)
				elif self.recorded_takes < REQUIRED_TAKES:
					self.recorded_frames[self.recorded_takes].append(landmarks)

	def toggle_recording(self) -> None:
		"""
		toggles recording state and updates webcam helper + ui accordingly

		Args:
			landmarks (np.ndarray): latest hand landmarks from the webcam feed
		"""
		
		if self.is_recording:
			self.is_recording = False
			self.camera_worker.stop_recording()

			self.recordButton.setText("Record")

			if self.verification_mode:
				if len(self.verification_frames) == 0:
					self.status.setText("No verification take recorded!")
					return
			
				self.status.setText(f"Verification take recorded!")

			else:
				if len(self.recorded_frames[self.recorded_takes]) > 0:
					self.recorded_takes += 1
				
				if self.recorded_takes < REQUIRED_TAKES:
					self.status.setText(f"Recorded {self.recorded_takes}/{REQUIRED_TAKES} takes!")
				else:
					self.status.setText("Time to verify!")
		else:
			if self.verification_mode:
				self.verification_frames.clear()

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

	def retry_take(self) -> None: 
		if self.verification_mode:
			self.verification_frames.clear()
			self.status.setText("Verification take cleared! Try again.")
		elif self.recorded_frames[self.recorded_takes - 1]:
			self.recorded_takes -= 1
			self.recorded_frames[self.recorded_takes].clear()
			self.status.setText("Last take cleared!")

	def can_process(self) -> bool:
		if self.is_recording:
			self.status.setText("Stop recording first!")
			return False

		if self.recorded_takes < REQUIRED_TAKES:
			self.status.setText(f"Must record {REQUIRED_TAKES} takes before saving!")
			return False

		sign_name = self.lineEdit.text().strip()
		if not sign_name:
			self.status.setText("Enter a sign name first!")
			return False
		
		if not self.recorded_frames:
			self.status.setText("Nothing to process!")
			return False

		return True
	
	def verify_sign(self) -> None:
		"""
		verifies the sign against the recorded takes
		"""
		if not self.can_process():
			return

		self.swap_last_button()
		self.verification_mode = True

	def compare_sign(self) -> SignPassMark:
		if not self.can_process():
			return

		comparison_array = np.array(self.verification_frames, dtype=np.float32)
		reference_takes = [np.array(take, dtype=np.float32) for take in self.recorded_frames]
		distances = self.cv_engine.compute_dtw_distance(reference_takes, comparison_array)
		closest = self.cv_engine.compare_sign(distances)
		result = self.cv_engine.evaluate_sign(closest)

		print(f"Result: {closest:.2f} ({result.name})")
		
		if result is not SignPassMark.FAIL:
			self.status.setText(f"Verification passed! {100-closest:.2f}% match!")
			# if exceptional match, add verification frame to reference data too
			if result == SignPassMark.EXCEPTIONAL:
				self.recorded_frames.append(self.verification_frames)
		else:
			self.status.setText(f"Verification failed! {100-closest:.2f}% match. Try again.")

		self.swap_last_button()
		return result

	def save_new_sign(self) -> None: 
		"""
		push landmarks and sign name to database
		"""
		if not self.can_process():
			return

		sign_name = self.lineEdit.text().strip()

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
		self.verification_mode = False
		self.verification_frames.clear()

	def swap_last_button(self) -> None:
		if self.verification_mode:
			self.saveButton.setText("Save")
			self.saveButton.clicked.disconnect()
			self.saveButton.clicked.connect(self.save_new_sign)
		else:
			self.status.setText("Verification time! Record a verification take and compare to save.")
			self.saveButton.setText("Compare")
			self.saveButton.clicked.disconnect()
			self.saveButton.clicked.connect(self.compare_sign)
	
	def closeEvent(self, event) -> None:
		if self.camera_worker.is_running:
			self.camera_worker.stop()
			event.accept()

		super().closeEvent(event)