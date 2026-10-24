from scripts.database.database import DatabaseManager

def test_add_word():
    db_manager = DatabaseManager()
    if db_manager.add_word("test_word"):
        print("Word added successfully.")
    else:
        print("Word already exists in the database.")

def test_get_word():
    db_manager = DatabaseManager()
    word = db_manager.get_word("test_word")
    if word:
        print(f"Retrieved word: {word.get_text()} with ID: {word.get_id()}")
    else:
        print("Word not found in the database.")

test_add_word()
test_get_word()