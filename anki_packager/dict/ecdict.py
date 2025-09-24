import os
import sqlite3

from anki_packager.logger import logger
from anki_packager.utils import get_user_config_dir

from anki_packager.dict import stardict

# https://github.com/liuyug/mdict-utils
from mdict_utils.reader import query
from mdict_utils.utils import ElapsedTimer


class Ecdict:
    def __init__(self):
        self.config_dir = get_user_config_dir()
        self.dicts_dir = os.path.join(self.config_dir, "dicts")
        # keep the package archive small
        self.seven_zip = os.path.join(self.dicts_dir, "stardict.7z")
        self.csv = os.path.join(self.dicts_dir, "stardict.csv")
        self.sqlite = os.path.join(self.dicts_dir, "stardict.db")
        self._convert()
        self.conn = sqlite3.connect(self.sqlite)
        self.cursor = self.conn.cursor()
        self.sd = stardict.StarDict(self.sqlite, False)

    def __del__(self):
        if hasattr(self, "conn"):
            self.cursor.close()
            self.conn.close()

    def _convert(self):
        if not os.path.exists(self.csv):
            # unzip stardict.csv in 7zip
            if not os.path.exists(self.seven_zip):
                raise FileNotFoundError(f"{self.seven_zip} 未找到!")

            import py7zr

            logger.info("首次使用: 正在解压词典到 anki_packager/dicts/stardict.csv")
            ar = py7zr.SevenZipFile(self.seven_zip, mode="r")
            ar.extractall(path=self.dicts_dir)
            ar.close()

        if not os.path.exists(self.sqlite):
            logger.info(
                "耐心等待(790M): 正在转换数据库 anki_packager/dicts/stardict.db"
            )
            stardict.convert_dict(self.sqlite, self.csv)

    async def ret_word(self, word):
        """Return ECDICT data
        dict: 包含以下 ECDICT 数据字段的字典：
        - word: 单词名称
        - phonetic: 音标，以英语英标为主
        - definition: 单词释义（英文），每行一个释义
        - translation: 单词释义（中文），每行一个释义
        - pos: 词语位置，用 "/" 分割不同位置
        - collins: 柯林斯星级
        - oxford: 是否是牛津三千核心词汇
        - tag: 字符串标签: zk/中考, gk/高考, cet4/四级 等等标签，空格分割
        - bnc: 英国国家语料库词频顺序
        - frq: 当代语料库词频顺序
        - exchange: 时态复数等变换，使用 "/" 分割不同项目
        - detail: json 扩展信息，字典形式保存例句（待添加）
        - audio: 读音音频 url （待添加）
        """
        data = self.sd.query(word)

        # 考纲标签
        data = self.parse_tag(data)
        # 释义分布
        data = self.get_distribution(data)
        # 词语辨析
        data = self.get_diffrentiation(data)
        return data

    def get_distribution(self, data):
        """
        Get word distribution from mdx dictionary
        """
        with ElapsedTimer(verbose=False):
            mdx_path = os.path.join(
                get_user_config_dir(),
                "dicts",
                "单词释义比例词典-带词性.mdx",
            )
            record = query(mdx_path, data["word"])
            if record:
                data["distribution"] = record
            return data

    def get_diffrentiation(self, data):
        """[《有道词语辨析》加强版](https://skywind.me/blog/archives/2941)"""
        with ElapsedTimer(verbose=False):
            mdx_path = os.path.join(get_user_config_dir(), "dicts", "有道词语辨析.mdx")
            record = query(mdx_path, data["word"])
            if record:
                data["diffrentiation"] = record
            return data

    def definition_newline(self, data):
        """Add newline to definition for each part-of-speech

        Demo:
            Input: data["definition"] = "n. 词义1 v. 词义2"
            Output: data["definition"] = "n. 词义1<br>v. 词义2"

        """
        definition = data.get("definition", "")
        if not definition:
            return data

        # Split on part of speech markers (like "n.", "v.", etc.)
        parts = []
        current = ""
        words = definition.split()

        for word in words:
            if len(word) >= 2 and word.endswith(".") and word[0].isalpha():
                if current:
                    parts.append(current.strip())
                current = word
            else:
                current += " " + word

        if current:
            parts.append(current.strip())

        data["definition"] = "<br>".join(parts)
        return data

    def parse_tag(self, data):
        """parse tag infomation and update data dict
        Demo:
            Input: data["tag"] = "zk gk cet4 cet6 ky ielts toefl"
            Output: data["tag"] = "中考 高考 四级 六级 考研 雅思 托福"
        """
        text = data.get("tag", "")
        if not text:
            return data

        tag_map = {
            "zk": "中考",
            "gk": "高考",
            "cet4": "四级",
            "cet6": "六级",
            "ky": "考研",
            "ielts": "雅思",
            "toefl": "托福",
            "gre": "GRE",
        }

        tags: str = text.split()
        result = [tag_map.get(tag, tag) for tag in tags]
        data["tag"] = " ".join(result)
        return data

    def parse_exchange(self, data):
        """parse exchange information and update data dict

        Demo:
            Input: data["exchange"] = "s:tests/d:tested/i:testing/p:tested/3:tests"
            Output: data["exchange"] = "复数:tests 过去式:tested 过去分词:tested 现在分词:testing 三单:tests"
        """
        text = data.get("exchange", "")
        if not text:
            return data

        exchange_map = {
            "s": "复数",
            "d": "过去式",
            "p": "过去分词",
            "i": "现在分词",
            "3": "三单",
            "r": "比较级",
            "t": "最高级",
            "0": "原型",
            "1": "第一人称单数",
        }

        result = []
        for item in text.split("/"):
            if ":" in item:
                key, value = item.split(":")
                if key in exchange_map:
                    result.append(f"{exchange_map[key]}: {value}")

        data["exchange"] = " ".join(result)
        return data
