import os
import sqlite3

# https://github.com/skywind3000/ECDICT
from anki_packager.dict.ECDICT import stardict


class Ecdit:
    def __init__(self):
        # ecdict path: ./ECDICT/
        self.ecdict_path = os.path.join(os.path.dirname(__file__), "ECDICT")
        self.csv = os.path.join(self.ecdict_path, "startdict.csv")
        self.sqlite = os.path.join(self.ecdict_path, "ecdict.db")
        self._convert()
        self.conn = sqlite3.connect(self.sqlite)
        self.cursor = self.conn.cursor()
        self.sd = stardict.StarDict(self.sqlite, False)

    def _convert(self):
        if not os.path.exists(self.sqlite):
            stardict.convert_dict(self.sqlite, self.csv)

    def ret_word(self, word):
        return self.sd.query(word)
