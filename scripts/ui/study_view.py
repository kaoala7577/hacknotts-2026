from PyQt6 import QWidget

class StudyView(QWidget): 
	def load_session_queue(self) -> None: pass 
	def display_tts_prompt(self, word_text: str) -> None: pass 
	def display_stt_prompt(self, video_path: str) -> None: pass 
	def submit_answer(self) -> None: pass 
	def record_response(self, grade: int) -> None: pass 