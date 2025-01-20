import genanki
import random


class AnkiDeckCreator:
    def __init__(self, deck_name: str, deck_id: int, model: genanki.Model, notes: list):
        self.deck_id = random.randrange(1 << 30, 1 << 31)
        self.model_id = random.randrange(1 << 30, 1 << 31)
        self.model = genanki.Model(
            self.model_id,
            "Simple Model",
            fields=[
                {"name": "Word"},
                {"name": "Pronunciation"},
                {"name": "Image"},
                {"name": "Examples"},  # Youdao examples without translation
                {"name": "DictDef"},  # ECDICT definition
                {"name": "AIExplanation"},  # AI generated explanation
                {"name": "YoudaoExplanation"},  # Youdao translation and notes
            ],
            templates=[
                {
                    "name": "Word Card",
                    "qfmt": """
                    <div class="word">{{Word}}</div>
                    <div class="pronunciation">{{Pronunciation}}</div>
                    {{#Image}}<div class="image">{{Image}}</div>{{/Image}}
                    <div class="examples">{{Examples}}</div>
                """,
                    "afmt": """
                    {{FrontSide}}
                    <hr id="answer">
                    <div class="dict-def">{{DictDef}}</div>
                    <div class="ai-explanation">{{AIExplanation}}</div>
                    <div class="youdao">{{YoudaoExplanation}}</div>
                """,
                }
            ],
            css="""
                .word { font-size: 2em; font-weight: bold; }
                .pronunciation { color: #666; margin-bottom: 1em; }
                .image { max-width: 300px; margin: 1em 0; }
                .examples { color: #333; font-style: italic; }
                .dict-def { margin-top: 1em; }
                .ai-explanation { margin-top: 1em; color: #2c5282; }
                .youdao { margin-top: 1em; color: #445; }
            """,
        )

    def add_note(self, data: dict[str, str]):
        note = genanki.Note(
            model=self.model,
            fields=[
                data["word"],
                data["pronunciation"],
                data["image"],
                data["examples"],
                data["dict_def"],
                data["ai_explanation"],
                data["youdao_explanation"],
            ],
        )
        self.note.add_note(note)

    def write_to_file(self, file_path: str):
        genanki.Package(self.deck).write_to_file(file_path)
