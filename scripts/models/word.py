

class Word:
    def __init__(self, word_id, word_text):
        self._id = word_id
        self._text = word_text

    def get_id(self):
        return self._id

    def get_text(self):
        return self._text

    def set_id(self, word_id):
        self._id = word_id

    def set_text(self, word_text):
        self._text = word_text