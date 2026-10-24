import numpy as np 
import cv2
import mediapipe as mp
import os
from pathlib import Path
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean

VIDEO_FOLDER = "./test_videos/references"
VIDEO_FILENAMES = os.listdir(VIDEO_FOLDER)
video_paths = []
for f in VIDEO_FILENAMES:
	video_paths.append(f"{VIDEO_FOLDER}/{f}")
VIDEO_FILENAME = "name_ref_1.mp4"
REF_FILENAME = "./test_videos/name_comparison.mp4"
TASK_FILE =  Path(__file__).parent / "hand_landmarker.task"

class SignRecognitionEngine:
	def __init__(self, task_file_path: str):
		BaseOptions = mp.tasks.BaseOptions
		HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
		# HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
		VisionRunningMode = mp.tasks.vision.RunningMode

		# def print_result(result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    	# 	print('hand landmarker result: {}'.format(result))

		self.options = HandLandmarkerOptions(
			base_options=BaseOptions(model_asset_path=task_file_path),
			num_hands=2,
			running_mode=VisionRunningMode.VIDEO
			#running_mode=VisionRunningMode.LIVE_STREAM,
			#result_callback=print_result
		)

	def start_detecting(self) -> None:
		self.detector = mp.tasks.vision.HandLandmarker.create_from_options(self.options)

	def stop_detecting(self) -> None:
		self.detector.close()

	def video_to_mp_image(self, path: str) -> np.ndarray:
		cap = cv2.VideoCapture(path)

		if not cap.isOpened():
			raise FileNotFoundError(f"Could not open {path}")
		
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

	def videos_to_mp_image(self, paths: np.ndarray) -> np.ndarray:
		images = []
		for path in paths: images.append(self.video_to_mp_image(path))
		return images
	
	def extract_landmarks(self, cv_frame: np.ndarray) -> np.ndarray:
		self.start_detecting()
		sequence_data = []
		
		for frame in cv_frame:
			video, timestamp_ms = frame
			detection_result = self.detector.detect_for_video(video, timestamp_ms)

			left_hand = [0.0] * 63 # 21 joints * 3 (xyz) coords
			right_hand = [0.] * 63

			if detection_result.hand_landmarks and detection_result.handedness:
				for landmarks, hand_side in zip(detection_result.hand_landmarks, detection_result.handedness):
					hand_label = hand_side[0].category_name

					flattened = []
					for landmark in landmarks:
						flattened.extend([landmark.x, landmark.y, landmark.z])

					if hand_label == 'Left':
						left_hand = flattened
					elif hand_label == 'Right':
						right_hand = flattened

			combined = left_hand + right_hand
			sequence_data.append(combined)
		
		self.stop_detecting()
		return np.array(sequence_data, dtype=np.float32)
	
	def draw_landmarks(self, cv_frame: np.ndarray, landmarks: np.ndarray) -> np.ndarray: pass
	
	def normalise_landmarks(self, cv_video: np.ndarray, landmarks: np.ndarray) -> np.ndarray: pass

	def play_video(self, cv_frame: np.ndarray) -> None: pass

	def compute_dtw_distance(self, references: np.ndarray, comparison: np.ndarray) -> float:
		distances = []
		for refs in references:
			dtw_distance, _ = fastdtw(comparison, refs, dist=euclidean)
			distances.append(dtw_distance)
		return min(distances)

	def evaluate_sign(self, test_landmarks: np.ndarray, reference_list: np.ndarray) -> float: pass 
	def select_best_take(self, takes_list: list[np.ndarray]) -> int: pass 

engine = SignRecognitionEngine(str(TASK_FILE))
videos = engine.videos_to_mp_image(video_paths)
ref = engine.video_to_mp_image(REF_FILENAME)
landmarks = []
for video in videos:
	landmarks.append(engine.extract_landmarks(video))

ref_landmarks = engine.extract_landmarks(ref)
print(engine.compute_dtw_distance(landmarks, ref_landmarks))