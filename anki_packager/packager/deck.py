import genanki
import random


class AnkiDeckCreator:
    def __init__(self, deck_name: str):
        self.deck_id = random.randrange(1 << 30, 1 << 31)
        self.model_id = random.randrange(1 << 30, 1 << 31)
        self.deck = genanki.Deck(self.deck_id, deck_name)
        self.model = genanki.Model(
            self.model_id,
            "Test Model",
            fields=[
                {"name": "Word"},  # 词头
                {"name": "Pronunciation"},  # 读音
                {"name": "Front"},  # 音标 + 考试大纲
                {"name": "ECDict"},  # Ecdict 中文解释
                {"name": "Longman"},  # Longman
                {"name": "Youdao"},  # 有道词典示例短语和句子
                {"name": "AI"},  # AI助记、词源
                {"name": "Discrimination"},  # 近义词、同义词
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
                            <div class="longman">{{Longman}}</div>
                            <hr class="dashed">
                            <div class="examples">{{Youdao}}</div>
                            <hr class="dashed">
                            <div class="ai">{{AI}}</div>
                            <hr class="dashed">
                            <div class="discrimination">{{Discrimination}}</div>
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
                # 词头
                str(data["Word"]),
                # 读音
                f"sound:{data['Pronunciation']}",
                # 音标 + 考试大纲
                f"[{data['ECDict']['phonetic']}] ({data['ECDict']['tag']})",
                # Ecdict 中文解释
                self.format_pos(data["ECDict"]["translation"]),
                # Longman
                self.format_pos(data["ECDict"]["definition"]),
                # 有道词典示例短语和句子
                str(self.format_youdao(data["Youdao"])),
                # AI助记、词源
                str(data["AI"]),
                # 近义词、同义词
                str(data["Discrimination"]),
            ],
        )
        self.deck.add_note(note)

    def write_to_file(self, file_path: str, mp3_files: str):
        package = genanki.Package(self.deck)
        package.media_files = mp3_files
        package.write_to_file(file_path)
