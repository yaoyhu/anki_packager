import argparse
import os
from os import environ as env
import json
from tqdm import tqdm
import signal

### config
from anki_packager.utils import get_user_config_dir

### logger
from anki_packager.logger import logger

### AI
from anki_packager.ai import MODEL_DICT

### Dictionaries
from anki_packager.dict.youdao import YoudaoScraper
from anki_packager.dict.ecdict import Ecdict
from anki_packager.dict.eudic import EUDIC

### Anki
from anki_packager.packager.deck import AnkiDeckCreator


def create_signal_handler(anki, youdao, audio_files, DECK_NAME, pbar):
    def signal_handler(sig, frame):
        pbar.close()
        logger.info("\033[1;31m程序被 <Ctrl-C> 异常中止...\033[0m")
        logger.info("正在写入已处理完毕的卡片...")
        anki.write_to_file(f"{DECK_NAME}.apkg", audio_files)
        youdao._clean_temp_dir()
        logger.info("正在退出...")
        exit(0)

    return signal_handler


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--word", dest="word", type=str, help="word to add")

    parser.add_argument(
        "--retry",
        action="store_true",
        help="Retry processing failed words only from config/failed.txt",
    )

    parser.add_argument(
        "--disable_ai",
        dest="disable_ai",
        action="store_true",
        help="Disable AI completions",
    )

    # ./prog --eudicid: run eudic.get_studylist()
    parser.add_argument(
        "--eudicid",
        action="store_true",
        help="Display EUDIC studylist by id",
    )

    parser.add_argument(
        "--eudic",
        action="store_true",
        help="Use EUDIC book instead of vocabulary.txt",
    )

    parser.add_argument(
        "--openai_key",
        dest="openai_key",
        type=str,
        default="",
        help="OpenAI api key",
    )

    parser.add_argument(
        "--gemini_key",
        dest="gemini_key",
        type=str,
        help="Google Gemini api key",
    )

    parser.add_argument(
        "--model", dest="model", type=str, help="custome AI model"
    )

    parser.add_argument(
        "-p",
        "--proxy",
        dest="proxy",
        type=str,
        default="",
        help="Default proxy like: http://127.0.0.1:7890",
    )

    parser.add_argument(
        "--api_base",
        metavar="API_BASE_URL",
        dest="api_base",
        type=str,
        help="Default base url other than the OpenAI's official API address",
    )

    options = parser.parse_args()

    ### set config according to config directory or parsed arguments
    config_dir = get_user_config_dir()
    config_path = os.path.join(config_dir, "config")

    ## 1. read config.json
    with open(os.path.join(config_path, "config.json"), "r") as ai_cfg:
        cfg = json.load(ai_cfg)
        API_KEY = cfg["API_KEY"]
        PROXY = cfg["PROXY"]
        API_BASE = cfg["API_BASE"]
        MODEL = cfg["MODEL"]
        EUDIC_TOKEN = cfg["EUDIC_TOKEN"]
        EUDIC_ID = cfg["EUDIC_ID"]
        DECK_NAME = cfg["DECK_NAME"]
    ai_cfg.close()
    logger.info("配置读取完毕")

    # display eudict id only
    if options.eudicid:
        logger.info("设置：仅读取欧路词典 ID")
        eudic = EUDIC(EUDIC_TOKEN, EUDIC_ID)
        eudic.get_studylist()
        exit(0)

    # only add word into vocabulary.txt line by line
    elif options.word:
        WORD = options.word
        vocab_path = os.path.join(config_path, "vocabulary.txt")
        with open(vocab_path, "a") as f:
            f.write(WORD + "\n")
        logger.info(f"单词: {WORD} 已添加进 {vocab_path}")
        exit(0)

    words = []
    retry_words = []
    number_words = 0
    audio_files = []
    ai = None

    anki = AnkiDeckCreator(f"{DECK_NAME}")
    ecdict = Ecdict()
    youdao = YoudaoScraper()

    # TODO: Improve readability
    if options.disable_ai:
        logger.info("AI 功能已关闭")
    else:
        PROXY = options.proxy
        if PROXY != "":
            env["HTTP_PROXY"] = PROXY
            env["HTTPS_PROXY"] = PROXY

        ### API_KEY in config.json not set, get key from cli based on the model
        if not API_KEY:
            # model must be valid
            MODEL = MODEL or options.model
            if not MODEL:
                logger.error("Set AI model in config.json or --model")
                exit(1)
            if MODEL in ["gpt-4o"]:
                # walrus operator: set API_KEY if OPENAI_API_KEY is not None
                if OPENAI_API_KEY := (
                    options.openai_key or env.get("OPENAI_API_KEY")
                ):
                    API_KEY = OPENAI_API_KEY
                else:
                    logger.error("OPENAI API key is missing")
                    exit(1)
            elif MODEL in ["deepseek-ai/DeepSeek-V2.5"]:
                if DEEPSEEK_API_KEY := (
                    options.deepseek_key or env.get("DEEPSEEK_API_KEY")
                ):
                    API_KEY = DEEPSEEK_API_KEY
                else:
                    logger.error("DeepSeek API key is missing")
                    exit(1)
            elif MODEL in ["gemini-2.0-flash"]:
                if GEMINI_API_KEY := (
                    options.gemini_key or env.get("GEMINI_API_KEY")
                ):
                    API_KEY = GEMINI_API_KEY
                else:
                    logger.error("Gemini API key is missing")
                    exit(1)
            else:
                logger.error("Invalid AI model")
                exit(1)
        elif not MODEL:
            ### api key is set in config.json, but model is not set
            MODEL = options.model
            if not MODEL:
                logger.error("Set AI model in config.json or --model")
                exit(1)

        if not API_BASE:
            API_BASE = options.api_base

        ai = MODEL_DICT[MODEL](MODEL, API_KEY, API_BASE)
        logger.info(f"当前使用的 AI 模型: {MODEL}")

    ## 4. vocabulary.txt or eudic data
    if options.eudic:
        logger.info("配置: 对欧路词典生词本单词进行处理...")
        eudic = EUDIC(EUDIC_TOKEN, EUDIC_ID)
        eudic_words = eudic.get_words()["data"]
        for word in eudic_words:
            words.append(word["word"])
        number_words = len(words)
    else:
        logger.info(
            f"配置: 对默认生词本单词{config_path}/vocabulary.txt 进行处理..."
        )
        with open(os.path.join(config_path, "vocabulary.txt"), "r") as vocab:
            try:
                for word in vocab:
                    words.append(word.strip())
                number_words = len(words)
            except FileNotFoundError:
                logger.error("vocabulary.txt not found")
                exit(1)
            except Exception as e:
                logger.error(f"Error reading vocabulary.txt: {e}")
                exit(1)
        vocab.close()

    pbar = tqdm(total=number_words, desc="开始处理")
    signal.signal(
        signal.SIGINT,
        create_signal_handler(anki, youdao, audio_files, DECK_NAME, pbar),
    )

    def process_word(word, ai, anki, youdao, ecdict, audio_files, pbar):
        data = {}
        data["Word"] = word

        # Get audio pronunciation from gtts
        audio_path = youdao._get_audio(word)
        if not audio_path:
            raise Exception("Failed to get audio")

        audio_files.append(audio_path)
        # 只使用文件名作为 sound 标签的值
        audio_filename = os.path.basename(audio_path)
        data["Pronunciation"] = audio_filename

        # Get ECDICT definition
        dict_def = ecdict.ret_word(word)
        if not dict_def:
            raise Exception("Failed to get ECDICT definition")
        data["ECDict"] = dict_def

        # Get Youdao dictionary information
        youdao_result = youdao.get_word_info(word)
        if not youdao_result:
            raise Exception("Failed to get Youdao information")

        data["Youdao"] = youdao_result

        # Get AI explanation if AI is enabled
        if ai is not None:
            try:
                ai_explanation = ai.explain(word)
                data["AI"] = ai_explanation
            except Exception as e:
                raise Exception(f"Failed to get AI explanation: {str(e)}")
        else:
            data["AI"] = {}

        # TODO: Longman English explain

        # Add note to deck
        anki.add_note(data)
        pbar.update(1)
        pbar.set_description(f"单词 {word} 添加成功")
        return True

    retry_words = []
    for word in words:
        try:
            process_word(word, ai, anki, youdao, ecdict, audio_files, pbar)
        except Exception as e:
            retry_words.append(word)
            logger.info(f"单词{word}处理出错: {e}，将会重试...")
            continue

    if retry_words:
        logger.info("对处理出错单词进行重试...")
        failed_words = []
        for word in retry_words:
            try:
                process_word(word, ai, anki, youdao, ecdict, audio_files, pbar)
            except Exception as e:
                logger.error(f"重试仍然失败... '{word}': {e}")
                failed_words.append(word)

        if failed_words:
            failed_file = os.path.join(config_path, "failed.txt")
            with open(failed_file, "w") as f:
                for word in failed_words:
                    f.write(f"{word}\n")
            logger.info(f"处理失败的单词已写入: {config_path}/failed.txt")

    # 关闭 pbar 避免多输出一次
    pbar.close()
    try:
        if anki.added:
            anki.write_to_file(f"{DECK_NAME}.apkg", audio_files)
            logger.info(f"牌组生成完毕，请打开 {DECK_NAME}.apkg")
    except Exception as e:
        logger.error(f"Error saving Anki deck: {e}")
    try:
        youdao._clean_temp_dir()
    except Exception as e:
        logger.error(f"Error cleaning up audio files: {e}")


if __name__ == "__main__":
    main()
