# import sqlite stuff 

class DatabaseManager: 
	def init_db(self) -> None: pass 
	def add_word(self, text_key: str) -> int: pass 
	def add_sign_variation(self, word_id: int, landmark_blob: bytes, video_path: str) -> int: pass 
	def get_sign_variations(self, word_id: int) -> list: pass 
	def get_due_words(self, limit: int = 10) -> list: pass 
	def get_due_signs(self, limit: int = 10) -> list: pass 
	def update_due_word(self, word_id: int ) -> None: pass # add args for sm2
	def update_due_sign(self, sign_id: int ) -> None: pass # add args for sm2
	def add_sign_reference(self, sign_id: int, landmark_blob: bytes) -> None: pass 