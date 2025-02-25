import argparse
import os
from os import environ as env
import json

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


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--word", dest="word", type=str, help="word to add")

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
        "--openai_key", dest="openai_key", type=str, default="", help="OpenAI api key"
    )

    parser.add_argument(
        "--gemini_key", dest="gemini_key", type=str, help="Google Gemini api key"
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
    config_path = os.path.join(os.getcwd(), "config")
    ## 1. read config.json
    with open(os.path.join(config_path, "config.json"), "r") as ai_cfg:
        cfg = json.load(ai_cfg)
        API_KEY = cfg["API_KEY"]
        PROXY = cfg["PROXY"]
        API_BASE = cfg["API_BASE"]
        MODEL = cfg["MODEL"]
        EUDIC_TOKEN = cfg["EUDIC_TOKEN"]
        EUDIC_ID = cfg["EUDIC_ID"]
    ai_cfg.close()

    # display eudict id only
    if options.eudicid:
        eudic = EUDIC(EUDIC_TOKEN, EUDIC_ID)
        eudic.get_studylist()
        exit(0)

    # only add word into vocabulary.txt line by line
    elif options.word:
        WORD = options.word
        cwd = os.getcwd()
        vocab_path = os.path.join(cwd, "config", "vocabulary.txt")
        with open(vocab_path, "a") as f:
            f.write(WORD + "\n")
        logger.info(f"{WORD} added to vocabulary.txt")
        exit(0)

    words = []
    audio_files = []
    data = {}
    ai = None

    anki = AnkiDeckCreator("Test")
    ecdict = Ecdict()
    youdao = YoudaoScraper()

    # set AI-related configrations if AI enabled
    if options.disable_ai is False:
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
                if OPENAI_API_KEY := (options.openai_key or env.get("OPENAI_API_KEY")):
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
                if GEMINI_API_KEY := (options.gemini_key or env.get("GEMINI_API_KEY")):
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

    ## 4. vocabulary.txt or eudic data
    if options.eudic:
        eudic = EUDIC(EUDIC_TOKEN, EUDIC_ID)
        eudic_words = eudic.get_words()["data"]
        for word in eudic_words:
            words.append(word["word"])
    else:
        with open(os.path.join(config_path, "vocabulary.txt"), "r") as vocab:
            try:
                for word in vocab:
                    words.append(word.strip())
            except FileNotFoundError:
                logger.error("vocabulary.txt not found")
                exit(1)
            except Exception as e:
                logger.error(f"Error reading vocabulary.txt: {e}")
                exit(1)
        vocab.close()

    try:
        for word in words:
            try:
                # Initialize empty data dictionary for each word
                data = {
                    "Word": word,
                    "Pronunciation": "",
                    "ECDict": "",
                    "Youdao": {
                        "example_phrases": [],
                        "example_sentences": [],
                    },
                    "AI": "",
                    "Longman": "",
                    "Discrimination": {
                        "synonyms": [],
                        "antonyms": [],
                    },
                    "Story": "",
                }

                # Get audio pronunciation from gtts
                audio = youdao._get_audio(word)
                if audio:
                    audio_files.append(audio)
                    data["Pronunciation"] = audio

                # Get ECDICT definition
                dict_def = ecdict.ret_word(word)
                if dict_def:
                    data["ECDict"] = dict_def

                # Get Youdao dictionary information
                youdao_result = youdao.get_word_info(word)
                if youdao_result:
                    examples = {
                        "example_phrases": [],
                        "example_sentences": [],
                    }
                    if youdao_result.get("example_phrases"):
                        examples["example_phrases"] = youdao_result["example_phrases"]
                    if youdao_result.get("example_sentences"):
                        examples["example_sentences"] = youdao_result[
                            "example_sentences"
                        ]
                    data["Youdao"]["example_phrases"] = examples["example_phrases"]
                    data["Youdao"]["example_sentences"] = examples["example_sentences"]

                # Get AI explanation if AI is enabled
                if ai is not None:
                    try:
                        ai_explanation = ai.explain(word)
                        data["AI"] = ai_explanation
                    except Exception as e:
                        logger.error(f"Error getting AI explanation for {word}: {e}")
                else:
                    data["AI"] = {}

                # TODO: Longman English explain

                # Add note to deck
                anki.add_note(data)
                logger.info(f"Word: \033[1;31m{word}\033[0m added...")

            except Exception as e:
                logger.error(f"Error processing word '{word}': {e}")
                # Continue with next word even if current one fails
                continue

    except Exception as e:
        logger.error(f"Fatal error occurred: {e}")

    finally:
        try:
            # Always try to save processed words and cleanup
            if anki.added:  # Only save if there are any processed notes
                logger.info("Saving processed words to Anki deck...")
                anki.write_to_file("test.apkg", audio_files)
        except Exception as e:
            logger.error(f"Error saving Anki deck: {e}")

        try:
            # Always attempt to clean up audio files
            logger.info("Cleaning up audio files...")
            youdao._clean_audio(audio_files)
        except Exception as e:
            logger.error(f"Error cleaning up audio files: {e}")


if __name__ == "__main__":
    main()
