import os
import requests
from gtts import gTTS
from bs4 import BeautifulSoup
from typing import Dict, List, Optional


class YoudaoScraper:
    def __init__(self):
        self.base_url = "https://m.youdao.com/result"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }

    # return the filename of the audio
    def _get_audio(self, word: str):
        filename = f"{word}.mp3"
        tts = gTTS(text=word, lang="en")
        tts.save(filename)
        return filename

    def _clean_audio(self, files):
        for file in files:
            try:
                os.remove(file)
            except OSError as e:
                print(f"Error deleting {file}: {e}")

    def get_word_info(self, word: str) -> Optional[Dict]:
        try:
            params = {"word": word, "lang": "en"}

            response = requests.get(self.base_url, params=params, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            result = {
                "word": word,
            }

            return result

        except Exception as e:
            print(f"Error fetching word '{word}': {str(e)}")
            return None


if __name__ == "__main__":
    # Usage example
    scraper = YoudaoScraper()
    result = scraper.get_word_info("hello")
    print(result)
