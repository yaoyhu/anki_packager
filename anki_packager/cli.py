import argparse
import os
from os import environ as env
import json


### AI
from anki_packager.ai import MODEL_DICT

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
    # if not any(vars(options).values()):
    #     parser.print_help()
    #     exit(0)

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
        ai_json = json.load(ai_cfg)
        API_KEY = ai_json["API_KEY"]
        PROXY = ai_json["PROXY"]
        API_BASE = ai_json["API_BASE"]
        MODEL = ai_json["MODEL"]
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

        # API_KEY in config.json not set, get key from cli based on the model
        if API_KEY is None:
            # model must be valid
            MODEL = MODEL or options.model
            if MODEL is None:
                raise ValueError("Set AI model in config.json or --model")
            if MODEL in ["gpt-4o"]:
                # walrus operator: set API_KEY if OPENAI_API_KEY is not None
                if OPENAI_API_KEY := (options.openai_key or env.get("OPENAI_API_KEY")):
                    API_KEY = OPENAI_API_KEY
                else:
                    raise ValueError("OPENAI API key is missing")
            elif MODEL in ["deepseek-ai/DeepSeek-V2.5"]:
                if DEEPSEEK_API_KEY := (
                    options.deepseek_key or env.get("DEEPSEEK_API_KEY")
                ):
                    API_KEY = DEEPSEEK_API_KEY
                else:
                    raise ValueError("DeepSeek API key is missing")
            # TODO: support gemini
            elif MODEL == "gemini":
                if GEMINI_API_KEY := (options.gemini_key or env.get("GEMINI_API_KEY")):
                    API_KEY = GEMINI_API_KEY
                else:
                    raise ValueError("Gemini API key is missing")
            else:
                API_KEY = ""
        elif MODEL is None:
            # api key is set in config.json, but model is not set
            MODEL = options.model
            if MODEL is None:
                raise ValueError("Set AI model in config.json or --model")

        if API_BASE is None:
            API_BASE = options.api_base
        ai = MODEL_DICT[MODEL](MODEL, API_KEY, API_BASE)

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

        # Get AI explanation if AI is enabled
        if ai is not None:
            try:
                ai_explanation = ai.explain(word)
                data["AI"] = ai_explanation["ai"]
                # use ai explanation for synonyms and antonyms (for now maybe...)
                data["Discrimination"]["synonyms"] = ai_explanation["synonyms"]
                data["Discrimination"]["antonyms"] = ai_explanation["antonyms"]
            except Exception as e:
                print(f"Error getting AI explanation for {word}: {e}")

        # TODO: Longman English explain

        # Add note to deck
        anki.add_note(data)

    anki.write_to_file("test.apkg", audio_files)

    # cleanup
    youdao._clean_audio(audio_files)
    # ecdict.__del__()


if __name__ == "__main__":
    main()
