import genanki
import random


class AnkiDeckCreator:
    def __init__(self, deck_name: str):
        self.added = False
        self.deck_name = deck_name
        self.deck_id = random.randrange(1 << 30, 1 << 31)
        self.model_id = random.randrange(1 << 30, 1 << 31)
        self.deck = genanki.Deck(self.deck_id, deck_name)
        self.model = genanki.Model(
            self.model_id,
            "Anki Packager",
            fields=[
                {"name": "Word"},  # 词头
                {"name": "Pronunciation"},  # 读音
                {"name": "Front"},  # 音标 + 考试大纲
                {"name": "ECDict"},  # Ecdict 中文解释
                {"name": "Longman"},  # Longman
                {"name": "Youdao"},  # 有道词典示例短语和句子
                {"name": "AI"},  # AI助记、词源
                {"name": "Discrimination"},  # 辨析
                {"name": "Story"},  # 故事
            ],
            templates=[
                {
                    "name": "Dictionary Card",
                    "qfmt": """
<div class="card-front">
    <div class="header-center">
        <div class="word">{{Word}}</div>
        <div class="front">{{Front}}</div>
        <div class="pronunciation">[{{Pronunciation}}]</div>
    </div>
</div>
""",
                    "afmt": """
{{FrontSide}}
<hr class="dashed">
<div class="card-back">
    <div class="ecdict">{{ECDict}}</div>
    <hr class="dashed">
    <div class="ai">{{AI}}</div>
    <hr class="dashed">
    <div class="examples">{{Youdao}}</div>
    <hr class="dashed">
    <div class="discrimination">{{Discrimination}}</div>
    <hr class="dashed">
    <div class="longman">{{Longman}}</div>
    <hr class="dashed">
    <div class="story">{{Story}}</div>
</div>
""",
                }
            ],
            css="""
.card {
    font-family: Arial, sans-serif;
    text-align: left;
    padding: 20px;
    max-width: 800px;
    margin: auto;
    background-color: white;
    line-height: 1.6;
}

/* 虚线分隔符 */
.dashed {
    border: none;
    border-top: 1px dashed #99a;  /* 使用灰蓝色，更接近图片 */
    margin: 15px 0;
    width: 100%;
}

/* Front side */
.card-front {
    margin-bottom: 20px;
}

/* Centered header section */
.header-center {
    text-align: center;
    margin-bottom: 20px;
}

.word {
    font-size: 2.2em;
    font-weight: bold;
    color: #000;
    margin-bottom: 5px;
}

.pronunciation {
    font-size: 1.1em;
    color: #0645AD;  /* Dictionary blue color */
    margin-bottom: 10px;
}

.front {
    color: #666;
    margin-bottom: 15px;
    font-size: 0.90em;
}

/* Back side */
.card-back {
    margin-top: 20px;
}

.ecdict {
    margin: 15px 0;
    text-align: center;
}

.longman {
    margin: 15px 0;
}

.examples {
    color: #2F4F4F;
    margin: 15px 0;
}

.examples em {
    color: #0645AD;  /* Blue for highlighted terms */
    font-style: normal;
    font-weight: bold;
}

.ai {
    color: #666;
    margin: 15px 0;
}

.discrimination {
    color: #333;
    margin: 15px 0;
}

/* Example sentences */
.example {
    color: #2F4F4F;
    margin-left: 20px;
    margin-bottom: 10px;
}

/* Chinese text */
.chinese {
    color: #666;
    margin-left: 20px;
}
            """,
        )

    def format_pos(self, text: str) -> str:
        """Format definition with line breaks between parts of speech"""
        if not text:
            return ""

        parts = []
        current = []

        for word in text.split():
            # Check for part of speech markers
            if any(
                word.startswith(pos + ".")
                for pos in ["n", "v", "vt", "vi", "adj", "adv"]
            ):
                if current:
                    parts.append(" ".join(current))
                # make part of speech bold, italic and red
                word = f"<b><i><font color='red'>{word}</font></i></b>"
                current = [word]
            else:
                # make chinese translation purple
                word = f"<font color='purple'>{word}</font>"
                current.append(word)

        if current:
            parts.append(" ".join(current))

        return "<br>".join(parts)

    def format_trans(self, translation: str, tense: str, distribution: str) -> str:
        """Add tense and distribution of each word in Translation part"""
        if not tense:
            # AI is disabled
            return f"{translation}<br><br>{distribution}"

        return f"{translation}<br><br>{tense}<br><br>{distribution}"

    def format_youdao(self, data: dict) -> str:
        """format youdao example_phrases and example_sentences"""
        result = []

        # Format phrases if they exist
        if "example_phrases" in data and data["example_phrases"]:
            result.append("【短语】")
            phrases = []
            for phrase in data["example_phrases"]:
                formatted_phrase = f"<li><b><font color='brown'>{phrase['english']}</font></b> {phrase['chinese']}</li>"
                phrases.append(formatted_phrase)

            result.append("".join(phrases))

        # Format sentences if they exist
        if "example_sentences" in data and data["example_sentences"]:
            result.append("【例句】")
            phrases = []
            for sentence in data["example_sentences"]:
                formatted_sentence = f"<li><b><font color='brown'>{sentence['english']}</font></b> {sentence['chinese']}</li>"
                phrases.append(formatted_sentence)

            result.append("".join(phrases))

        return "<br>".join(result)

    def add_note(self, data: dict):
        note = genanki.Note(
            model=self.model,
            fields=[
                # 词头
                data.get("Word", ""),
                # 读音
                f"[sound:{data.get('Pronunciation', '')}]",
                # 音标 + 考试大纲 + 语料库词频: [ә'bændәn] (高考 四级 六级 考研 托福 GRE 2057/2182)
                f"[<font color=blue>{data.get('ECDict', {}).get('phonetic', '')}</font>] ({data.get('ECDict', {}).get('tag', '')} {data.get('ECDict', {}).get('bnc', '')}/{data.get('ECDict', {}).get('frq', '')})",
                # Ecdict 中文解释 + 释义分布 + 时态
                self.format_trans(
                    self.format_pos(data.get("ECDict", {}).get("translation", "")),
                    data.get("ECDict", {}).get("distribution", ""),
                    data.get("AI", {}).get("tenses", ""),
                ),
                # TODO ECDICT for now, will be implemented later
                f"【英解】<br>{self.format_pos(data.get('ECDict', {}).get('definition', ''))}",
                # 有道词典示例短语和句子
                self.format_youdao(data.get("Youdao", {})),
                # AI助记、词源
                ""
                if not data.get("AI")
                else f"【词源】<br>{data.get('AI', {}).get('origin', {}).get('etymology', '')}<br><br> \
                【助记】<li>联想：{data.get('AI', {}).get('origin', {}).get('mnemonic', {}).get('associative', '')}</li>\
                <li>谐音： {data.get('AI', {}).get('origin', {}).get('mnemonic', {}).get('homophone', '')}</li>",
                # 词语辨析
                ""
                if not data.get("ECDict", {}).get("diffrentiation", "")
                else f"【辨析】{data.get('ECDict', {}).get('diffrentiation', '')}",
                # 故事
                ""
                if not data.get("AI")
                else f"【故事】 {data.get('AI', {}).get('story', {}).get('english', '')}<br><br>{data.get('AI', {}).get('story', {}).get('chinese', '')}",
            ],
        )
        self.deck.add_note(note)
        self.added = True

    def write_to_file(self, file_path: str, mp3_files):
        package = genanki.Package(self.deck)
        package.media_files = mp3_files
        package.write_to_file(file_path)
