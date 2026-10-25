# import sqlite stuff 
import sqlite3
import os
import logging
import numpy as np
from models.word import Word

class DatabaseManager: 
	def __init__(self)-> None:
		db_path = os.path.join(os.path.dirname(__file__), 'signdex.db')
		self.conn = sqlite3.connect(db_path)
		self.create_tables()

	def create_tables(self) -> None:
		cursor = self.conn.cursor()
		cursor.execute('''
		CREATE TABLE IF NOT EXISTS words (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			word TEXT UNIQUE NOT NULL
		)
		''')

		cursor.execute('''
		CREATE TABLE IF NOT EXISTS signs (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			word_id INTEGER NOT NULL,
			FOREIGN KEY (word_id) REFERENCES words(id)
		)
		''')

		cursor.execute('''
		CREATE TABLE IF NOT EXISTS sign_references (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			sign_id INTEGER NOT NULL,
			reference_data BLOB NOT NULL,
			FOREIGN KEY (sign_id) REFERENCES signs(id)
		)
		''')

		cursor.execute('''
		CREATE TABLE IF NOT EXISTS review_schedule (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			sign_id INTEGER NOT NULL,
			due_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			ease_factor REAL DEFAULT 2.5,
			repetitions INTEGER DEFAULT 0,
			interval INTEGER DEFAULT 1,
			FOREIGN KEY (sign_id) REFERENCES signs(id)
		)
		''')
		
		self.conn.commit()
		cursor.close()

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
		self.conn.commit()
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
		
	def add_sign_variation(self, word_id: int) -> int:
		cursor = self.conn.cursor()
		query = 'INSERT INTO signs(word_id) VALUES(?)'
		cursor.execute(query, (word_id,))
		self.conn.commit()
		sign_id = cursor.lastrowid
		cursor.close()
		return sign_id

	def get_sign_variations(self, word_id: int) -> list:
		cursor = self.conn.cursor()
		query = "SELECT id, word_id, reference_data FROM signs WHERE word_id = ?"
		cursor.execute(query, (word_id,))
		results = cursor.fetchall()
		cursor.close()
		return results
	
	def get_due_words(self, limit: int = 10) -> list: 
		cursor = self.conn.cursor()
		query = '''
		SELECT w.id, w.word
		FROM words w, review_schedule rs, signs s
		WHERE w.id = s.word_id AND s.id = rs.sign_id AND rs.due_date <= CURRENT_TIMESTAMP
		ORDER BY rs.due_date ASC
		LIMIT ?
		'''
		cursor.execute(query, (limit,))
		results = cursor.fetchall()
		cursor.close()
		return results

	def get_due_signs(self, limit: int = 10) -> list: 
		cursor = self.conn.cursor()
		query = '''
		SELECT s.id, s.word_id
		FROM signs s, review_schedule rs
		WHERE s.id = rs.sign_id AND rs.due_date <= CURRENT_TIMESTAMP
		ORDER BY rs.due_date ASC
		LIMIT ?
		'''
		cursor.execute(query, (limit,))
		results = cursor.fetchall()
		cursor.close()
		return results

	def update_due_word(self, word_id: int ) -> None: pass # add args for sm2
	def update_due_sign(self, sign_id: int ) -> None: pass # add args for sm2
	
	def add_sign_reference(self, sign_id: int, landmark_blob: bytes) -> bool: 
		cursor = self.conn.cursor()
		query = "INSERT INTO sign_references (sign_id, reference_data) VALUES (?, ?)"
		try:
			cursor.execute(query, (sign_id, landmark_blob))
			self.conn.commit()
		except sqlite3.IntegrityError:
			logging.warning(f"Sign reference for sign_id '{sign_id}' already exists in the database.")
			cursor.close()
			return False
		cursor.close()
		self.conn.commit()
		return True

	def get_sign_references(self, sign_id: int) -> list:
		cursor = self.conn.cursor()
		query = "SELECT id, sign_id, reference_data FROM sign_references WHERE sign_id = ?"
		cursor.execute(query, (sign_id,))
		results = cursor.fetchall()
		cursor.close()
		return results