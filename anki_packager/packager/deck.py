import genanki
import random
import re


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
                {"name": "Phonetic_Symbols"},  # 音标
                {"name": "Examination_Syllabus"},  # 考试大纲
                {"name": "ECDict"},  # Ecdict 中文解释
                {"name": "Longman"},  # Longman
                {"name": "Youdao"},  # 有道词典示例短语和句子
                {"name": "Etymology_AI"},  # 词源
                {"name": "Associative_Mnemonic_AI"},  # 联想助记
                {"name": "Homophone_Mnemonic_AI"},  # 谐音助记
                {"name": "Discrimination"},  # 辨析
                {"name": "Story"},  # 故事
            ],
            templates=[
                {
                    "name": "Dictionary Card",
                    "qfmt": """
<div class="card-front">
    <div class="word-header">
        <div class="word-main">{{Word}}</div>
        <div class="word-meta">
            <span class="pronunciation-group">
                <div class="pronunciation">{{Pronunciation}}</div>
                <span class="phonetic-text">/{{Phonetic_Symbols}}/</span>
            </span>
        </div>
        <div class="exam-tags">{{Examination_Syllabus}}</div>
    </div>
</div>
""",
                    "afmt": """
{{FrontSide}}
<div class="card-back">
    <div class="ecdict">{{ECDict}}</div>
    <div class="etymology">{{Etymology_AI}}</div>
    <div class="associative_mnemonic">{{Associative_Mnemonic_AI}}</div>
    <div class="homophone_mnemonic">{{Homophone_Mnemonic_AI}}</div>
    <div class="examples">{{Youdao}}</div>
    <div class="discrimination">{{Discrimination}}</div>
    <div class="longman">{{Longman}}</div>
    <div class="story">{{Story}}</div>
</div>
""",
                }
            ],
            css="""
/* Color scheme variables */
:root {
    /* Light mode (default) colors */
    --bg-color: #ffffff;
    --text-color: #333333;
    --secondary-text: #666666;
    --tertiary-text: #2F4F4F;
    --highlight-color: #0645AD;
    --accent-color: #990000;
    --divider-color: #ddd;
    --pos-color: #990000;
    --cn-text-color: #8B008B;
    --phrase-color: #8B4513;
    
    /* Card gradients */
    --card-bg-start: #ffffff;
    --card-bg-end: #f9fafb;
    --card-border-color: #e5e7eb;
    
    /* Mnemonic section colors */
    --etymology-color: #4A90E2;
    --etymology-bg: rgba(74, 144, 226, 0.08);
    --associative-color: #50C878;
    --associative-bg: rgba(80, 200, 120, 0.08);
    --homophone-color: #9B59B6;
    --homophone-bg: rgba(155, 89, 182, 0.08);
    
    /* Target word highlight */
    --target-word-color: #0D47A1;
    --target-word-bg: rgba(255, 235, 59, 0.3);
    --target-word-border: #0D47A1;
    
    /* Story section backgrounds */
    --story-english-bg: rgba(6, 69, 173, 0.03);
    --story-chinese-bg: rgba(139, 0, 139, 0.03);
    
    /* Card and section backgrounds */
    --card-section-bg: #ffffff;
    --card-border: #e6eaf0;
}

/* Dark mode colors */
@media (prefers-color-scheme: dark) {
    :root {
        --bg-color: rgb(44, 44, 44);
        --text-color: #e0e0e0;
        --secondary-text: #b0b0b0;
        --tertiary-text: #a0c0c0;
        --highlight-color: #7cb8ff;
        --accent-color: #ff7c7c;
        --divider-color: #555;
        --pos-color: #ff9e64;
        --cn-text-color: #d183e8;
        --phrase-color: #e0c080;
        
        --card-bg-start: rgb(44, 44, 44);
        --card-bg-end: rgb(44, 44, 44);
        --card-border-color: #555;
        
        /* Dark mode mnemonic colors */
        --etymology-color: #6BA4E8;
        --etymology-bg: rgba(107, 164, 232, 0.15);
        --associative-color: #6FD89A;
        --associative-bg: rgba(111, 216, 154, 0.15);
        --homophone-color: #B37FD8;
        --homophone-bg: rgba(179, 127, 216, 0.15);
        
        /* Dark mode target word highlight */
        --target-word-color: #00E5FF;
        --target-word-bg: rgba(0, 229, 255, 0.2);
        --target-word-border: #00E5FF;
        
        /* Dark mode story backgrounds */
        --story-english-bg: rgba(107, 164, 232, 0.08);
        --story-chinese-bg: rgba(179, 127, 216, 0.08);
        
        /* Dark mode card backgrounds */
        --card-section-bg: rgb(44, 44, 44);
        --card-border: #555;
    }
}

/* Night mode in Anki also triggers dark mode */
.nightMode,
.night_mode {
    --bg-color: rgb(44, 44, 44);
    --text-color: #e0e0e0;
    --secondary-text: #b0b0b0;
    --tertiary-text: #a0c0c0;
    --highlight-color: #7cb8ff;
    --accent-color: #ff7c7c;
    --divider-color: #555;
    --pos-color: #ff9e64;
    --cn-text-color: #d183e8;
    --phrase-color: #e0c080;
    
    --card-bg-start: rgb(44, 44, 44);
    --card-bg-end: rgb(44, 44, 44);
    --card-border-color: #555;
    
    /* Dark mode mnemonic colors */
    --etymology-color: #6BA4E8;
    --etymology-bg: rgba(107, 164, 232, 0.15);
    --associative-color: #6FD89A;
    --associative-bg: rgba(111, 216, 154, 0.15);
    --homophone-color: #B37FD8;
    --homophone-bg: rgba(179, 127, 216, 0.15);
    
    /* Dark mode target word highlight */
    --target-word-color: #00E5FF;
    --target-word-bg: rgba(0, 229, 255, 0.2);
    --target-word-border: #00E5FF;
    
    /* Dark mode story backgrounds */
    --story-english-bg: rgba(107, 164, 232, 0.08);
    --story-chinese-bg: rgba(179, 127, 216, 0.08);
    
    /* Dark mode card backgrounds */
    --card-section-bg: rgb(44, 44, 44);
    --card-border: #555;
}

/* Base body styling */
html,
body {
    background-color: #f5f5f5;
}

@media (prefers-color-scheme: dark) {
    html,
    body {
        background-color: rgb(44, 44, 44) !important;
    }
}

.nightMode html,
.night_mode html,
.nightMode body,
.night_mode body {
    background-color: rgb(44, 44, 44) !important;
}

.card {
    font-family: Georgia, "Times New Roman", Times, serif;
    text-align: left;
    padding: 24px;
    max-width: 1100px;
    width: 95%;
    margin: 20px auto;
    background: var(--bg-color) !important;
    color: var(--text-color);
    line-height: 1.8;
    border-radius: 0;
    border: none;
    box-shadow: none;
}

/* 虚线分隔符 */
.dashed {
    border: none;
    border-top: 1px solid var(--divider-color);
    margin: 24px 0;
    width: 100%;
    opacity: 0.3;
}

/* Front side - Cambridge Dictionary style */
.card-front {
    margin-bottom: 24px;
    padding: 24px 28px;
    background: var(--card-section-bg) !important;
    border-radius: 12px;
    border: 1px solid var(--card-border);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

/* Word header */
.word-header {
    text-align: left;
}

.word-main {
    font-size: 3em;
    font-weight: 700;
    color: var(--text-color);
    margin-bottom: 12px;
    letter-spacing: -0.5px;
    line-height: 1.1;
}

/* Pronunciation group with speaker icon */
.word-meta {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
}

.pronunciation-group {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 1.15em;
    color: var(--secondary-text);
}

.speaker-icon {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    opacity: 0.7;
    transition: all 0.2s;
    user-select: none;
    color: var(--secondary-text);
}

.speaker-icon svg {
    width: 20px;
    height: 20px;
    vertical-align: middle;
}

.speaker-icon:hover {
    opacity: 1;
    transform: scale(1.1);
    color: var(--highlight-color);
}

.speaker-icon:active {
    transform: scale(0.95);
}

.phonetic-text {
    font-family: Georgia, "Lucida Sans Unicode", "Arial Unicode MS", serif;
    color: var(--secondary-text);
    font-style: italic;
    font-weight: 400;
}

/* Exam tags */
.exam-tags {
    display: inline-flex;
    gap: 6px;
    flex-wrap: wrap;
    font-size: 0.85em;
    color: var(--secondary-text);
    margin-top: 8px;
}

/* Back side */
.card-back {
    margin-top: 24px;
    display: flex;
    flex-direction: column;
    gap: 0;
}

.ecdict,
.examples,
.discrimination,
.longman,
.story {
    background: transparent;
    border: none;
    border-radius: 0;
    padding: 12px 0;
    box-shadow: none;
    color: var(--text-color);
    margin-bottom: 8px;
}

/* Further reduce padding for specific sections */
.story {
    padding: 8px 0;
}

.ecdict {
    text-align: left;
}

.longman {
    color: var(--text-color);
}

.examples {
    color: var(--tertiary-text);
}

.examples .example-list {
    list-style: none;
    padding-left: 0;
    margin: 4px 0 8px 0;
}

.examples .example-item {
    margin: 8px 0;
    padding: 6px 10px;
    border-left: 2px solid var(--highlight-color);
    background: transparent;
    border-radius: 0;
    box-shadow: none;
}

.examples .eng-sentence {
    color: var(--text-color);
    font-weight: 500;
    font-size: 1em;
    line-height: 1.6;
}

.examples .cn-sentence {
    color: var(--secondary-text);
    margin-top: 2px;
    font-size: 0.9em;
    line-height: 1.5;
}

.examples .sentence-source {
    color: var(--secondary-text);
    font-size: 0.85em;
    margin-top: 2px;
}

.examples .highlight-word {
    color: var(--highlight-color);
    font-weight: 700;
}

.examples .section-title {
    color: var(--text-color);
    font-weight: 700;
    margin: 12px 0 6px 0;
    display: block;
    padding: 0;
    border-radius: 0;
    background: transparent;
    font-size: 1em;
}

.examples em {
    color: var(--highlight-color);
    font-style: normal;
    font-weight: 600;
}

.examples .highlight-word {
    color: var(--highlight-color);
    font-weight: 600;
    background: none;
}

/* Mnemonic sections with distinct styling */
.etymology,
.associative_mnemonic,
.homophone_mnemonic {
    background: transparent;
    border-radius: 8px;
    padding: 12px 16px;
    margin: 8px 0;
    box-shadow: none;
    color: var(--text-color);
    line-height: 1.8;
}

/* Section icons styling */
.section-icon {
    display: inline-block;
    margin-right: 4px;
    font-size: 1em;
    opacity: 0.8;
}

/* Hide empty mnemonic sections */
.etymology:empty,
.associative_mnemonic:empty,
.homophone_mnemonic:empty {
    display: none;
    margin: 0;
    padding: 0;
}

.etymology {
    border-left: 3px solid var(--etymology-color);
    background: var(--etymology-bg);
}

.associative_mnemonic {
    border-left: 3px solid var(--associative-color);
    background: var(--associative-bg);
}

.homophone_mnemonic {
    border-left: 3px solid var(--homophone-color);
    background: var(--homophone-bg);
}

/* Target word highlighting - maximum visibility for ADHD */
.target-word-highlight {
    font-weight: 700;
    background: var(--target-word-bg);
    color: var(--target-word-color);
    border-bottom: 2px solid var(--target-word-border);
    padding: 2px 4px;
    border-radius: 3px;
    display: inline-block;
}

/* Story section styling - more compact */
.story .story-english {
    color: var(--text-color);
    font-weight: 400;
    line-height: 1.6;
    margin-bottom: 8px;
    padding: 0;
    background: transparent;
    border-radius: 0;
    font-size: 1em;
}

.story .story-chinese {
    color: var(--secondary-text);
    line-height: 1.6;
    padding: 0;
    background: transparent;
    border-radius: 0;
    font-size: 0.9em;
}

/* Hide empty sections to prevent white space */
.ecdict:empty,
.story:empty,
.discrimination:empty,
.longman:empty,
.examples:empty {
    display: none !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Hide sections with only whitespace or only the title */
.ecdict:not(:has(*:not(br))):not(:has(text)):empty,
.story:has(br):not(:has(*:not(br))):empty,
.discrimination:has(br):not(:has(*:not(br))):empty {
    display: none !important;
}

.discrimination {
    color: var(--text-color);
    margin: 15px 0;
}

/* Example sentences */
.example {
    color: var(--tertiary-text);
    margin-left: 20px;
    margin-bottom: 10px;
}

/* Chinese text */
.chinese {
    color: var(--secondary-text);
    margin-left: 20px;
}

/* Responsive design for mobile devices */
@media (max-width: 768px) {
    .card {
        width: 100%;
        padding: 16px 20px;
        margin: 0;
        border-radius: 0;
    }
    
    .word-main {
        font-size: 2.2em;
    }
    
    .card-front {
        padding: 16px 20px;
    }
    
    .pronunciation-group {
        font-size: 1em;
    }
    
    .examples .eng-sentence {
        font-size: 1em;
    }
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
                word = f"<b><i><span class='pos-marker'>{word}</span></i></b>"
                current = [word]
            else:
                word = f"<span class='cn-text'>{word}</span>"
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

        target_word = data.get("word", "")

        def norm(text: str) -> str:
            """Trim leading/trailing whitespace to avoid blank head lines."""
            return text.strip() if isinstance(text, str) else ""

        def highlight_word(text: str) -> str:
            """Highlight the target word inside example sentences."""
            if not target_word or not text:
                return text or ""

            pattern = re.compile(rf"\b{re.escape(target_word)}\b", flags=re.IGNORECASE)
            return pattern.sub(
                lambda match: f"<span class='highlight-word'>{match.group(0)}</span>",
                text,
            )

        # Format phrases if they exist
        if "example_phrases" in data and data["example_phrases"]:
            phrases = []
            for phrase in data["example_phrases"]:
                english = highlight_word(norm(phrase.get("english", "")))
                chinese = norm(phrase.get("chinese", ""))
                if not english and not chinese:
                    continue
                formatted_phrase = (
                    "<li class='example-item'>"
                    f"<div class='eng-sentence'><b><span class='phrase-text'>{english}</span></b></div>"
                    f"<div class='cn-sentence'>{chinese}</div>"
                    "</li>"
                )
                phrases.append(formatted_phrase)

            if phrases:
                result.append("<div class='section-title'>【短语】</div>")
                result.append(
                    f"<ul class='example-list phrases'>{''.join(phrases)}</ul>"
                )

        # Format sentences if they exist
        if "example_sentences" in data and data["example_sentences"]:
            phrases = []
            for sentence in data["example_sentences"]:
                english = highlight_word(norm(sentence.get("english", "")))
                chinese = norm(sentence.get("chinese", ""))
                source = norm(sentence.get("source", ""))
                if not english and not chinese and not source:
                    continue

                source_html = (
                    f"<div class='sentence-source'>{source}</div>" if source else ""
                )

                formatted_sentence = (
                    "<li class='example-item'>"
                    f"<div class='eng-sentence'><b>{english}</b></div>"
                    f"<div class='cn-sentence'>{chinese}</div>"
                    f"{source_html}"
                    "</li>"
                )
                phrases.append(formatted_sentence)

            if phrases:
                result.append("<div class='section-title'>【例句】</div>")
                result.append(
                    f"<ul class='example-list sentences'>{''.join(phrases)}</ul>"
                )

        return "".join(result)

    def highlight_target_word(self, text: str, target_word: str) -> str:
        """Highlight the target word with maximum visibility for ADHD focus."""
        if not target_word or not text:
            return text or ""

        pattern = re.compile(rf"\b({re.escape(target_word)})\b", flags=re.IGNORECASE)
        return pattern.sub(
            lambda match: f"<span class='target-word-highlight'>{match.group(0)}</span>",
            text,
        )

    def add_note(self, data: dict):
        target_word = data.get("Word", "")

        # Get AI data with highlighting
        etymology_text = ""
        if data.get("AI"):
            etymology_raw = data.get("AI", {}).get("origin", {}).get("etymology", "")
            etymology_text = f"<span class='section-icon'>📖</span> 【词源】<br>{self.highlight_target_word(etymology_raw, target_word)}"

        associative_text = ""
        if data.get("AI"):
            associative_raw = (
                data.get("AI", {})
                .get("origin", {})
                .get("mnemonic", {})
                .get("associative", "")
            )
            associative_text = f"<span class='section-icon'>💭</span> 【联想助记】<br>{self.highlight_target_word(associative_raw, target_word)}"

        homophone_text = ""
        if data.get("AI"):
            homophone_raw = (
                data.get("AI", {})
                .get("origin", {})
                .get("mnemonic", {})
                .get("homophone", "")
            )
            homophone_text = f"<span class='section-icon'>🔤</span> 【谐音助记】<br>{self.highlight_target_word(homophone_raw, target_word)}"

        # Story with highlighted target word in English section
        story_text = ""
        if data.get("AI"):
            story_english = data.get("AI", {}).get("story", {}).get("english", "")
            story_chinese = data.get("AI", {}).get("story", {}).get("chinese", "")
            story_english_highlighted = self.highlight_target_word(
                story_english, target_word
            )
            story_text = f"【故事】<br><div class='story-english'>{story_english_highlighted}</div><br><div class='story-chinese'>{story_chinese}</div>"

        note = genanki.Note(
            model=self.model,
            fields=[
                # 词头
                target_word,
                # 读音
                f"[sound:{data.get('Pronunciation', '')}]",
                # 音标 + 考试大纲 + 语料库词频: [ә'bændәn] (高考 四级 六级 考研 托福 GRE 2057/2182)
                f"{data.get('ECDict', {}).get('phonetic', '')}",
                f"{data.get('ECDict', {}).get('tag', '')} {data.get('ECDict', {}).get('bnc', '')}/{data.get('ECDict', {}).get('frq', '')}",
                # Ecdict 中文解释 + 释义分布 + 时态
                self.format_trans(
                    self.format_pos(data.get("ECDict", {}).get("translation", "")),
                    data.get("ECDict", {}).get("distribution", ""),
                    data.get("AI", {}).get("tenses", ""),
                ),
                # TODO: use better English source
                f"【英解】<br>{self.format_pos(data.get('ECDict', {}).get('definition', ''))}",
                # 有道词典示例短语和句子
                self.format_youdao(data.get("Youdao", {})),
                # AI词源、助记 with emoji icons and word highlighting
                etymology_text,
                associative_text,
                homophone_text,
                # 词语辨析
                ""
                if not data.get("ECDict", {}).get("diffrentiation", "")
                else f"【辨析】{data.get('ECDict', {}).get('diffrentiation', '')}",
                # 故事 with word highlighting
                story_text,
            ],
        )
        self.deck.add_note(note)
        self.added = True

    def write_to_file(self, file_path: str, mp3_files):
        package = genanki.Package(self.deck)
        package.media_files = mp3_files
        package.write_to_file(file_path)
