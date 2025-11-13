import os
import platform

from anki_packager.logger import logger


def get_user_config_dir():
    """
    Returns the platform-specific user configuration directory.

    - Windows: %APPDATA%/anki_packager
    - macOS/Linux: ~/.config/anki_packager
    """
    if platform.system() == "Windows":
        return os.path.join(os.environ.get("APPDATA", ""), "anki_packager")
    else:
        return os.path.expanduser("~/.config/anki_packager")


def initialize_config():
    """
    Make sure user config dir exists.

    Example:
    ~/.config/anki_packager/
        ├── config
        │   ├── config.toml
        │   ├── failed.txt
        │   └── vocabulary.txt
        └── dicts
            ├── 单词释义比例词典-带词性.mdx
            ├── 有道词语辨析.mdx
            ├── stardict.7z
            ├── stardict.csv
            └── stardict.db
    """
    config_dir = get_user_config_dir()
    os.makedirs(config_dir, exist_ok=True)
    config_subdir = os.path.join(config_dir, "config")
    os.makedirs(config_subdir, exist_ok=True)
    dicts_dir = os.path.join(config_dir, "dicts")
    os.makedirs(dicts_dir, exist_ok=True)

    # Default configuration in TOML format
    default_config = """
PROXY = ""
EUDIC_TOKEN = ""
EUDIC_ID = "0"
DECK_NAME = "anki_packager"

[[MODEL_PARAM]]
model = "gemini/gemini-2.5-flash"
api_key = "GEMINI_API_KEY"
rpm = 10                          # 每分钟请求次数

# [[MODEL_PARAM]]
# model = "openai/gpt-4o"
# api_key = "OPENAI_API_KEY"
# api_base = "YOUR_API_BASE"
# rpm = 200

"""

    config_path = os.path.join(config_subdir, "config.toml")
    if not os.path.exists(config_path):
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(default_config)

    vocab_path = os.path.join(config_subdir, "vocabulary.txt")
    if not os.path.exists(vocab_path):
        with open(vocab_path, "w", encoding="utf-8") as f:
            f.write("")

    failed_path = os.path.join(config_subdir, "failed.txt")
    if not os.path.exists(failed_path):
        with open(failed_path, "w", encoding="utf-8") as f:
            f.write("reform\nopen\n")

    logger.info(f"配置文件位于 {config_path}")
