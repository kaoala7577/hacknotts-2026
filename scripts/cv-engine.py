import numpy as np 

class SignRecognitionEngine: 
	def extract_landmarks(self, cv_frame: np.ndarray) -> np.ndarray: pass 
	def draw_landmarks(self, cv_frame: np.ndarray) -> None: pass 
	def compute_dtw_distance(self, seq1: np.ndarray, seq2: np.ndarray) -> float: pass 
	def evaluate_sign(self, test_landmarks: np.ndarray, reference_list: list[np.ndarray]) -> float: pass 
	def select_best_take(self, takes_list: list[np.ndarray]) -> int: pass 