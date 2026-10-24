import numpy as np 
import cv2
import mediapipe as mp
import os
from pathlib import Path

folder = "./test_videos/references"
VIDEO_FILENAMES = os.listdir(folder)
VIDEO_FILENAME = "name_ref_1.mp4"
TASK_FILE =  Path(__file__).parent / "hand_landmarker.task"

class SignRecognitionEngine:
	def __init__(self, task_file_path: str):
		BaseOptions = mp.tasks.BaseOptions
		HandLandmarker = mp.tasks.vision.HandLandmarker
		HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
		# HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
		VisionRunningMode = mp.tasks.vision.RunningMode

		# def print_result(result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    	# 	print('hand landmarker result: {}'.format(result))

		options = HandLandmarkerOptions(
			base_options=BaseOptions(model_asset_path=task_file_path),
			num_hands=2,
			running_mode=VisionRunningMode.VIDEO
			#running_mode=VisionRunningMode.LIVE_STREAM,
			#result_callback=print_result
		)

		self.detector = HandLandmarker.create_from_options(options)
	
	def video_to_mp(self, path: str) -> np.ndarray:
		video_path = f"{folder}/{path}"
		cap = cv2.VideoCapture(video_path)

		if not cap.isOpened():
			raise FileNotFoundError(f"Could not open {video_path}")
		
		fps = cap.get(cv2.CAP_PROP_FPS)
		frame_index = 0

		frames = []

		while cap.isOpened():
			ret, frame = cap.read()
			if not ret:
				break

			rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
			mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
			timestamp_ms = int((frame_index / fps) * 1000)

			frames.append((mp_image, timestamp_ms))
			frame_index += 1
		cap.release()
		cv2.destroyAllWindows()

		return frames
	
	def extract_landmarks(self, cv_frame: np.ndarray) -> np.ndarray:
		landmarks = []
		for frame in cv_frame:
			video, timestamp_ms = frame
			print(video, timestamp_ms)
			
			detection_result = self.detector.detect_for_video(video, timestamp_ms)

			landmarks.append(detection_result)
		return landmarks
	
	def draw_landmarks(self, cv_frame: np.ndarray, landmarks: np.ndarray) -> np.ndarray: pass
	def play_video(self, cv_frame: np.ndarray) -> None: pass
	def compute_dtw_distance(self, seq1: np.ndarray, seq2: np.ndarray) -> float:pass
		
	def evaluate_sign(self, test_landmarks: np.ndarray, reference_list: list[np.ndarray]) -> float: pass 
	def select_best_take(self, takes_list: list[np.ndarray]) -> int: pass 

engine = SignRecognitionEngine(str(TASK_FILE))
video = engine.video_to_mp(VIDEO_FILENAME)
landmarks = engine.extract_landmarks(video)
# print(landmarks)