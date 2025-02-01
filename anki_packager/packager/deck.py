import genanki
import random


class AnkiDeckCreator:
    def __init__(self, deck_name: str):
        self.deck_id = random.randrange(1 << 30, 1 << 31)
        self.model_id = random.randrange(1 << 30, 1 << 31)
        self.deck = genanki.Deck(self.deck_id, deck_name)
        self.model = genanki.Model(
            self.model_id,
            "Simple Model",
            # Great template: https://skywind.me/blog/archives/2949
            fields=[
                {"name": "Word"},  # 词头
                {"name": "Pronunciation"},  # 音标
                {"name": "Front"},
                {"name": "ECDict"},  # Ecdict解释+考试大纲
                {"name": "Youdao"},  # 有道词典
                {"name": "AI"},  # AI助记
                {"name": "Longman"},  # Longman双解
                {"name": "Discrimination"},  # 近义词、同义词
            ],
            templates=[
                {
                    "name": "Word Card",
                    "qfmt": """
                    <div class="card-front">
                        <div class="word">{{Word}}</div>
                        <div class="pronunciation">{{Pronunciation}}</div>
                        <div class="front">{{Front}}</div>
                    </div>
                """,
                    "afmt": """
                    {{FrontSide}}
                    <hr id="answer">
                    <div class="card-back">
                        <div class="ecdict">{{ECDict}}</div>
                        <div class="longman">{{Youdao}}</div>
                        <div class="longman">{{Longman}}</div>
                        <div class="ai">{{AI}}</div>
                        <div class="discrimination">{{Discrimination}}</div>
                    </div>
                """,
                }
            ],
            css="""
                .card {
                    font-family: Arial, sans-serif;
                    text-align: center;  /* Center all content */
                    padding: 20px;
                    max-width: 800px;
                    margin: auto;
                    background-color: #f8f9fa;
                }
                
                /* Front side */
                .card-front {
                    margin-bottom: 20px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;  /* Center flexbox items */
                }
                .word {
                    font-size: 2.5em;
                    font-weight: bold;
                    color: #2c3e50;
                    margin-bottom: 10px;
                }
                .pronunciation {
                    font-size: 1.2em;
                    color: #7f8c8d;
                    margin-bottom: 15px;
                }
                
                /* Back side */
                .card-back {
                    margin-top: 20px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;  /* Center flexbox items */
                }
                .ecdict, .longman, .ai, .discrimination {
                    width: 100%;  /* Full width for content */
                    text-align: center;
                    margin-bottom: 15px;
                    padding: 10px;
                    border-radius: 5px;
                }
                .ecdict {
                    font-size: 1.1em;
                    color: #2c3e50;
                    line-height: 1.5;
                }
                .longman {
                    color: #34495e;
                    background: #ecf0f1;
                }
                .ai {
                    color: #2980b9;
                    background: #e8f4f8;
                }
                .discrimination {
                    color: #27ae60;
                    background: #e8f8f5;
                }
                
                hr#answer {
                    width: 80%;  /* Shorter line for better aesthetics */
                    border: none;
                    border-top: 2px solid #bdc3c7;
                    margin: 20px auto;  /* Center the line */
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
                current = [word]
            else:
                current.append(word)

        if current:
            parts.append(" ".join(current))

        return "<br>".join(parts)

    def format_youdao(self, data: dict) -> str:
        """format youdao example_phrases and example_sentences
        Demo:
            'example_phrases': [
            {'index': '1', 'english': 'environment variable', 'chinese': '环境变量 ; 访问所有环境变量'},
            {'index': '2', 'english': 'Random Variable', 'chinese': '数  随机变量 ;  数  随机变数 ; 无规变量 ; 无规变数'},
            {'index': '3', 'english': 'control variable', 'chinese': '自  控制变量 ; 控件变量 ; 控制变项'}],

            'example_sentences': [
            {'index': '1', 'english': 'The drill has variable speed control.', 'chinese': '这钻机有变速控制。', 'source': '《牛津词典》'},
            {'index': '2', 'english': 'The potassium content of foodstuffs is very variable.', 'chinese': '食品中钾的含量是多变的。', 'source': '《柯林斯英汉双解大词典》'},
            {'index': '3', 'english': 'The temperature remained constant while pressure was a variable in the experiment.', 'chinese': '做这实验时温度保持不变，但压力可变。', 'source': '《牛津词典》'
        Output:
            短语:
                1. environment variable 环境变量 ; 访问所有环境变量
                2. Random Variable 数  随机变量 ;  数  随机变数 ; 无规变量 ; 无规变数
                3. control variable 自  控制变量 ; 控件变量 ; 控制变项
            例句:
                1. The drill has variable speed control. 这钻机有变速控制。 (《牛津词典》)
                2. The potassium content of foodstuffs is very variable. 食品中钾的含量是多变的。 (《柯林斯英汉双解大词典》)
                3. The temperature remained constant while pressure was a variable in the experiment. 做这实验时温度保持不变，但压力可变。 (《牛津词典》)
        """
        result = []

        # Format phrases if they exist
        if "example_phrases" in data and data["example_phrases"]:
            result.append("短语:")
            for phrase in data["example_phrases"]:
                formatted_phrase = (
                    f"    {phrase['index']}. {phrase['english']} {phrase['chinese']}"
                )
                result.append(formatted_phrase)

        # Add blank line between phrases and sentences if both exist
        if (
            "example_phrases" in data
            and data["example_phrases"]
            and "example_sentences" in data
            and data["example_sentences"]
        ):
            result.append("")

        # Format sentences if they exist
        if "example_sentences" in data and data["example_sentences"]:
            result.append("例句:")
            for sentence in data["example_sentences"]:
                formatted_sentence = f"    {sentence['index']}. {sentence['english']} {sentence['chinese']} ({sentence['source']})"
                result.append(formatted_sentence)

        # Join all lines with <br> instead of newlines
        return "<br>".join(result)

    def add_note(self, data: dict[str, str]):
        note = genanki.Note(
            model=self.model,
            fields=[
                str(data["Word"]),
                f"[sound:{data['Pronunciation']}]",
                f'音标：[{data["ECDict"]["phonetic"]}]<br>考纲：{data["ECDict"]["tag"]}',
                self.format_pos(data["ECDict"]["translation"]),
                str(self.format_youdao(data["Youdao"])),
                str(data["AI"]),
                self.format_pos(data["ECDict"]["definition"]),
                str(data["Discrimination"]),
            ],
        )
        self.deck.add_note(note)

    def write_to_file(self, file_path: str, mp3_files: str):
        package = genanki.Package(self.deck)
        package.media_files = mp3_files
        package.write_to_file(file_path)
