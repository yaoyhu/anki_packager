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

    def add_note(self, data: dict[str, str]):
        note = genanki.Note(
            model=self.model,
            fields=[
                str(data["Word"]),
                f"[sound:{data['Pronunciation']}]",
                str(data["ECDict"]),
                str(data["Youdao"]),
                str(data["AI"]),
                str(data["Longman"]),
                str(data["Discrimination"]),
            ],
        )
        self.deck.add_note(note)

    def write_to_file(self, file_path: str, mp3_files: str):
        package = genanki.Package(self.deck)
        package.media_files = mp3_files
        package.write_to_file(file_path)
