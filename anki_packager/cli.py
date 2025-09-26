import argparse
import asyncio
import os
from os import environ as env
import tomllib
from tqdm.asyncio import tqdm
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

MAX_RETRIES = 3  # 最大重试次数
RETRY_DELAY = 2  # 每次重试前的等待时间（秒）
CONCURRENCY_LIMIT = 40  # 并发数


def create_signal_handler(anki, audio_files, DECK_NAME):
    def signal_handler(sig, frame):
        logger.info("\033[1;31m程序被 <Ctrl-C> 异常中止...\033[0m")
        logger.info("正在写入已处理完毕的卡片...")
        anki.write_to_file(f"{DECK_NAME}.apkg", audio_files)
        logger.info("正在退出...")
        exit(0)

    return signal_handler


async def main():
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

    ## 1. read config.toml
    with open(os.path.join(config_path, "config.toml"), "rb") as f:
        cfg = tomllib.load(f)
        MODEL_PARAM = cfg["MODEL_PARAM"]
        PROXY = cfg["PROXY"]
        EUDIC_TOKEN = cfg["EUDIC_TOKEN"]
        EUDIC_ID = cfg["EUDIC_ID"]
        DECK_NAME = cfg["DECK_NAME"]

    logger.info("配置读取完毕")

    # display eudict id only
    if options.eudicid:
        logger.info("设置：仅读取欧路词典 ID")
        eudic = EUDIC(EUDIC_TOKEN, EUDIC_ID)
        await eudic.get_studylist()
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
    number_words = 0
    audio_files = []
    ai = None

    anki = AnkiDeckCreator(f"{DECK_NAME}")
    ecdict = Ecdict()

    # AI 配置
    if options.disable_ai:
        logger.info("AI 功能已关闭")
    else:
        PROXY = options.proxy or PROXY
        if PROXY:
            env["HTTP_PROXY"] = PROXY
            env["HTTPS_PROXY"] = PROXY
            logger.info(f"使用代理: {PROXY}")

        # 初始化 AI 模型
        try:
            ai = llm(MODEL_PARAM)
            logger.info(
                f"当前使用的 AI 模型: {[param['model'] for param in MODEL_PARAM]}"
            )
        except Exception as e:
            logger.error(f"初始化 AI 模型失败: {e}")
            exit(1)
    ## 4. vocabulary source: eudic data, custom txt file, or default vocabulary.txt
    if options.eudic:
        logger.info("配置: 对欧路词典生词本单词进行处理...")
        eudic = EUDIC(EUDIC_TOKEN, EUDIC_ID)
        r = await eudic.get_words()
        eudic_words = r["data"]
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

    signal.signal(
        signal.SIGINT,
        create_signal_handler(anki, audio_files, DECK_NAME),
    )
    async with YoudaoScraper() as youdao:
        logger.info(f"开始并发处理 {len(words)} 个单词...")
        with tqdm(total=len(words), desc="开始处理") as pbar:
            tasks = [
                task_wrapper(pbar, word, ai, anki, youdao, ecdict, audio_files)
                for word in words
            ]
            results = await asyncio.gather(*tasks, return_exceptions=True)

        successful_results = []
        failed_words = []

        for word, result in zip(words, results):
            if isinstance(result, Exception):
                failed_words.append(word)
                logger.error(f"未能成功处理 '{word}'. 错误: {result}")
            else:
                successful_results.append(result)

        if failed_words:
            failed_file = os.path.join(config_path, "failed.txt")
            logger.error(
                f"共 {len(failed_words)} 个单词处理失败，将它们写入 {failed_file}"
            )
            with open(failed_file, "w", encoding="utf-8") as f:
                for word in failed_words:
                    f.write(f"{word}\n")
        else:
            logger.info("所有单词均已成功处理！")

        try:
            if anki.added:
                anki.write_to_file(f"{DECK_NAME}.apkg", audio_files)
                logger.info(f"牌组生成完毕，请打开 {DECK_NAME}.apkg")
        except Exception as e:
            logger.error(f"Error saving Anki deck: {e}")


async def process_word(word, ai, anki, youdao, ecdict, audio_files):
    data = {}
    data["Word"] = word

    # Get audio pronunciation from gtts
    audio_path = await youdao._get_audio(word)
    if not audio_path:
        raise Exception("Failed to get audio")

    audio_files.append(audio_path)
    # 只使用文件名作为 sound 标签的值
    audio_filename = os.path.basename(audio_path)
    data["Pronunciation"] = audio_filename

    # Get ECDICT definition
    dict_def = await ecdict.ret_word(word)
    if not dict_def:
        raise Exception("Failed to get ECDICT definition")
    data["ECDict"] = dict_def

    # Get Youdao dictionary information
    youdao_result = await youdao.get_word_info(word)
    if not youdao_result:
        raise Exception("Failed to get Youdao information")

    data["Youdao"] = youdao_result

    # Get AI explanation if AI is enabled
    if ai is not None:
        try:
            ai_explanation = await ai.explain(word)
            data["AI"] = ai_explanation
        except Exception as e:
            raise Exception(f"Failed to get AI explanation: {str(e)}")
    else:
        data["AI"] = {}

    # TODO: Longman English explain

    # Add note to deck
    anki.add_note(data)
    return True


semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)


async def process_word_with_retries(word, ai, anki, youdao, ecdict, audio_files):
    """
    包含了重试和退避逻辑
    """
    for attempt in range(MAX_RETRIES):
        try:
            async with semaphore:
                result = await process_word(word, ai, anki, youdao, ecdict, audio_files)
            return result
        except Exception as e:
            logger.warning(
                f"处理 '{word}' 第 {attempt + 1}/{MAX_RETRIES} 次尝试失败: {e}"
            )
            if attempt + 1 == MAX_RETRIES:
                # 如果是最后一次尝试，则不再捕获异常，让它冒泡出去
                # gather(return_exceptions=True) 会捕获这个最终的异常
                logger.error(f"'{word}' 在所有 {MAX_RETRIES} 次尝试后最终失败。")
                raise
            await asyncio.sleep(RETRY_DELAY)


async def task_wrapper(pbar, word, ai, anki, youdao, ecdict, audio_files):
    """
    运行带重试逻辑的任务，并确保进度条在最后总会更新。
    """
    try:
        r = await process_word_with_retries(word, ai, anki, youdao, ecdict, audio_files)
        pbar.set_description(f"'{word}' 添加成功")
        return r
    except Exception:
        pbar.set_description(f"'{word}' 处理失败")
        raise
    finally:
        pbar.update(1)


if __name__ == "__main__":
    asyncio.run(main())
