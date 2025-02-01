import argparse
import os
from os import environ as env
import json


### AI
from anki_packager.ai.gpt import ChatGPT
from anki_packager.ai.gemini import Gemini

### Dictionaries
from anki_packager.dict.youdao import YoudaoScraper
from anki_packager.dict.ecdict import Ecdict

### Anki
from anki_packager.packager.deck import AnkiDeckCreator


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--word", dest="word", type=str, help="word to add")

    # option to disable AI: not recommended
    parser.add_argument(
        "--disable_ai",
        dest="disable_ai",
        action="store_true",
        help="Disable AI completions",
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

    # if no arguments, print help
    if not any(vars(options).values()):
        parser.print_help()
        exit(0)

    # only add word into vocabulary.txt line by line
    if options.word:
        WORD = options.word
        cwd = os.getcwd()
        vocab_path = os.path.join(cwd, "config", "vocabulary.txt")
        with open(vocab_path, "a") as f:
            f.write(WORD + "\n")
        print(f"{WORD} added to v.txt")
        exit(0)

    config_path = os.path.join(os.getcwd(), "config")
    ## 1. ai-related: config.json
    with open(os.path.join(config_path, "config.json"), "r") as ai_cfg:
        ai_data = json.load(ai_cfg)
        API_KEY = ai_data["API_KEY"]
        PROXY = ai_data["PROXY"]
        API_BASE = ai_data["API_BASE"]
        MODEl = ai_data["MODEL"]
    ai_cfg.close()

    ## 2. prompt-related: prompt.json
    # with open(os.path.join(config_path, "prompt.json"), "r") as prompt_cfg:
    #     prompt_data = json.load(prompt_cfg)
    #     PROMPT = prompt_data["PROMPT"]
    # prompt_cfg.close()

    ## 3. anki-related: anki_template.json
    # with open(os.path.join(config_path, "anki_template.json"), "r") as anki_cfg:
    #     anki_data = json.load(anki_cfg)
    #     ANKI_TEMPLATE = anki_data["ANKI_TEMPLATE"]

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

        if API_KEY is None:
            MODEL = MODEl or options.model
            if MODEL is None:
                raise ValueError("Set AI model in config.json or --model")
            if MODEl in ["openai", "gpt4o"]:
                # walrus operator: set API_KEY if OPENAI_API_KEY is not None
                if OPENAI_API_KEY := (options.openai_key or env.get("OPENAI_API_KEY")):
                    API_KEY = OPENAI_API_KEY
                    ai = ChatGPT(API_KEY, API_BASE)
                else:
                    raise ValueError("OPENAI API key is missing")
            elif MODEL == "gemini":
                if GEMINI_API_KEY := (options.gemini_key or env.get("GEMINI_API_KEY")):
                    API_KEY = GEMINI_API_KEY
                    ai = Gemini(API_KEY, API_BASE)
                else:
                    raise ValueError("Gemini API key is missing")
            else:
                API_KEY = ""

        if API_BASE is None:
            API_BASE = options.api_base

    ## 4. vocabulary.txt
    with open(os.path.join(config_path, "vocabulary.txt"), "r") as vocab:
        try:
            for word in vocab:
                words.append(word.strip())
        except FileNotFoundError:
            print("vocabulary.txt not found")
        except Exception as e:
            print(e)
    vocab.close()

    for word in words:
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
                "synonyms": [],
                "antonyms": [],
            }
            if youdao_result.get("example_phrases"):
                examples["example_phrases"] = youdao_result["example_phrases"]
            if youdao_result.get("example_sentences"):
                examples["example_sentences"] = youdao_result["example_sentences"]
            # TODO: not finished yet!
            if youdao_result.get("synonyms"):
                examples["synonyms"] = youdao_result["synonyms"]
            if youdao_result.get("antonyms"):
                examples["antonyms"] = youdao_result["antonyms"]
            data["Youdao"]["example_phrases"] = examples["example_phrases"]
            data["Youdao"]["example_sentences"] = examples["example_sentences"]
            data["Discrimination"]["synonyms"] = examples["synonyms"]
            data["Discrimination"]["antonyms"] = examples["antonyms"]

        # TODO: Get AI explanation if AI is enabled
        # if ai is not None:
        #     try:
        #         ai_explanation = ai.explain(word)
        #         data["ai_explanation"] = ai_explanation
        #     except Exception as e:
        #         print(f"Error getting AI explanation for {word}: {e}")

        # TODO: Longman English explain

        # Add note to deck
        anki.add_note(data)

    anki.write_to_file("test.apkg", audio_files)

    # cleanup
    youdao._clean_audio(audio_files)
    # ecdict.__del__()


if __name__ == "__main__":
    main()
