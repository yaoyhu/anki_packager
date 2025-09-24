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
from anki_packager.ai import llm

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

    # support user-defined txt file: ./prog --txt demo.txt
    parser.add_argument(
        "--txt",
        dest="txt_file",
        type=str,
        help="Use a custom txt file instead of vocabulary.txt",
    )

    parser.add_argument("--model", dest="model", type=str, help="custome AI model")

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
        ENV = cfg["ENV"]
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

    # AI 配置
    if options.disable_ai:
        logger.info("AI 功能已关闭")
    else:
        PROXY = options.proxy or PROXY
        if PROXY:
            env["HTTP_PROXY"] = PROXY
            env["HTTPS_PROXY"] = PROXY
            logger.info(f"使用代理: {PROXY}")

        API_BASE = options.api_base or API_BASE
        MODEL = options.model or MODEL
        if not MODEL:
            logger.error("未设置 AI 模型，请在配置文件或使用 --model 参数指定")
            exit(1)

        # 导入环境变量
        for key, value in ENV.items():
            if key in os.environ:
                logger.info(f"环境变量 '{key}' 已存在，将被配置文件中的值覆盖。")

            if value and isinstance(value, str):
                os.environ[key] = value
                logger.info(f"成功加载 '{key}' 到环境变量。")
            else:
                logger.debug(f"跳过 '{key}'，因为其值为空或格式不正确。")

        # 初始化 AI 模型
        try:
            ai = llm(MODEL, API_BASE)
            logger.info(f"当前使用的 AI 模型: {MODEL}")
        except Exception as e:
            logger.error(f"初始化 AI 模型失败: {e}")
            exit(1)
    ## 4. vocabulary source: eudic data, custom txt file, or default vocabulary.txt
    if options.eudic:
        logger.info("配置: 对欧路词典生词本单词进行处理...")
        eudic = EUDIC(EUDIC_TOKEN, EUDIC_ID)
        eudic_words = eudic.get_words()["data"]
        for word in eudic_words:
            words.append(word["word"])
        number_words = len(words)
    elif options.txt_file:
        txt_file_path = options.txt_file
        if not os.path.isabs(txt_file_path):
            # If relative path, resolve from current directory
            txt_file_path = os.path.abspath(txt_file_path)

        logger.info(f"配置: 对自定义单词文件 {txt_file_path} 进行处理...")
        try:
            with open(txt_file_path, "r") as vocab:
                for word in vocab:
                    word = word.strip()
                    if word:  # Skip empty lines
                        words.append(word)
                number_words = len(words)
        except FileNotFoundError:
            logger.error(f"文件 {txt_file_path} 未找到")
            exit(1)
        except Exception as e:
            logger.error(f"读取文件 {txt_file_path} 出错: {e}")
            exit(1)
    else:
        vocab_path = os.path.join(config_path, "vocabulary.txt")
        logger.info(f"配置: 对默认生词本单词 {vocab_path} 进行处理...")
        try:
            with open(vocab_path, "r") as vocab:
                for word in vocab:
                    word = word.strip()
                    if word:  # Skip empty lines
                        words.append(word)
                number_words = len(words)
            logger.info(f"从默认词库读取了 {number_words} 个单词")
        except FileNotFoundError:
            logger.error(f"默认词库文件 {vocab_path} 未找到")
            exit(1)
        except Exception as e:
            logger.error(f"读取默认词库文件出错: {e}")
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
