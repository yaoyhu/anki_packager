import os
import sqlite3

# https://github.com/skywind3000/ECDICT
from anki_packager.dict.ECDICT import stardict


class Ecdict:
    def __init__(self):
        # ecdict path: ./ECDICT/
        self.ecdict_path = os.path.join(os.path.dirname(__file__), "ECDICT")
        self.csv = os.path.join(self.ecdict_path, "stardict.csv")
        self.sqlite = os.path.join(self.ecdict_path, "stardict.db")
        self._convert()
        self.conn = sqlite3.connect(self.sqlite)
        self.cursor = self.conn.cursor()
        self.sd = stardict.StarDict(self.sqlite, False)

    def __del__(self):
        if hasattr(self, "conn"):
            self.cursor.close()
            self.conn.close()

    def _convert(self):
        if not os.path.exists(self.sqlite):
            stardict.convert_dict(self.sqlite, self.csv)

    def ret_word(self, word):
        return self.sd.query(word)


if __name__ == "__main__":
    ecdict = Ecdict()
    print(ecdict.ret_word("hello"))
    print("")
    print(ecdict.ret_word("world"))
    print("")
    print(ecdict.ret_word("python"))
    print("")
    print(ecdict.ret_word("dictionary"))
