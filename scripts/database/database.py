# import sqlite stuff 
import sqlite3
import os
import logging
import numpy as np
from .word import Word

class DatabaseManager: 
	def __init__(self)-> None:
		db_path = os.path.join(os.path.dirname(__file__), 'signdex.db')
		self.conn = sqlite3.connect(db_path)

	def close_db(self):
		self.conn.close()

	def add_word(self, text_key: str) -> bool:
		cursor = self.conn.cursor()
		query = "INSERT INTO words (word) VALUES (?)"
		try:
			cursor.execute(query, (text_key,))
			self.conn.commit()
		except sqlite3.IntegrityError:
			logging.warning(f"Word '{text_key}' already exists in the database.")
			cursor.close()
			return False
		cursor.close()
		return True		

	def get_word(self, word: str) -> Word:
		cursor = self.conn.cursor()
		query = "SELECT id, word FROM words WHERE word = ?"
		cursor.execute(query, (word,))
		result = cursor.fetchone()
		cursor.close()
		if result:
			return Word(result[0], result[1])
		else:
			logging.warning(f"Word '{word}' not found in the database.")
			return None
		
	def add_sign_variation(self, word_id: int, landmark_blob: bytes, video_path: str) -> int:
		cursor = self.conn.cursor()

	def get_sign_variations(self, word_id: int) -> list: pass 
	def get_due_words(self, limit: int = 10) -> list: pass 
	def get_due_signs(self, limit: int = 10) -> list: pass 
	def update_due_word(self, word_id: int ) -> None: pass # add args for sm2
	def update_due_sign(self, sign_id: int ) -> None: pass # add args for sm2
	def add_sign_reference(self, sign_id: int, landmark_blob: bytes) -> None: pass 