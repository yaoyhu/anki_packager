import os
import re
import shutil
import tempfile
import requests
from gtts import gTTS
from bs4 import BeautifulSoup
from typing import Dict, Optional
from anki_packager.logger import logger


class YoudaoScraper:
    def __init__(self):
        self.base_url = "https://m.youdao.com/result"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        self.tmp = tempfile.mkdtemp()

    def _get_audio(self, word: str):
        """return the filename of the audio and the temp directory that needs to be cleaned up"""
        filename = os.path.join(self.tmp, f"{word}.mp3")
        tts = gTTS(text=word, lang="en")
        tts.save(filename)
        return filename

    def _clean_temp_dir(self):
        """Clean up a temporary directory and its contents."""
        try:
            if os.path.exists(self.tmp):
                shutil.rmtree(self.tmp)
                logger.info(f"音频临时文件夹已清理: {self.tmp}")
        except Exception as e:
            logger.error(f"音频临时文件夹 {self.tmp} 清理失败: {e}")

    def get_word_info(self, word: str) -> Optional[Dict]:
        try:
            params = {"word": word, "lang": "en"}

            response = requests.get(self.base_url, params=params, headers=self.headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            result = {
                "word": word,
                "example_phrases": [],
                "example_sentences": [],
            }

            # Extract example phrases
            phrase_ul = soup.find_all("ul", class_="")[0]
            if phrase_ul:
                phrase_lis = phrase_ul.find_all("li", class_="mcols-layout")
                for li in phrase_lis:
                    index = (
                        li.find("span", class_="grey").text.strip()
                        if li.find("span", class_="grey")
                        else None
                    )
                    col2_element = li.find("div", class_="col2")
                    point_element = col2_element.find("a", class_="point")
                    sen_phrase_element = col2_element.find("p", class_="sen-phrase")
                    english = None
                    chinese = None
                    if point_element and sen_phrase_element:
                        english = point_element.text.strip()
                        chinese = sen_phrase_element.text.strip()
                    else:
                        content = col2_element.text.strip()
                        parts = re.split(r"([;；])", content)
                        parts = [
                            s.strip()
                            for s in parts
                            if s.strip() and s not in [";", "；"]
                        ]
                        if len(parts) > 1:
                            english = parts[0]
                            chinese = "".join(parts[1:])
                        else:
                            english = content

                    result["example_phrases"].append(
                        {
                            "index": index,
                            "english": english,
                            "chinese": chinese,
                        }
                    )

            # Extract example sentences
            sentence_ul = soup.find_all("ul", class_="")[1]
            if sentence_ul:
                sentence_lis = sentence_ul.find_all("li", class_="mcols-layout")
                for li in sentence_lis:
                    index = (
                        li.find("span", class_="grey index").text.strip()
                        if li.find("span", class_="grey index")
                        else None
                    )
                    english_element = li.find("div", class_="sen-eng")
                    chinese_element = li.find("div", class_="sen-ch")
                    source_element = li.find("div", class_="secondary")

                    english = english_element.text.strip() if english_element else None
                    chinese = chinese_element.text.strip() if chinese_element else None
                    source = source_element.text.strip() if source_element else None

                    result["example_sentences"].append(
                        {
                            "index": index,
                            "english": english,
                            "chinese": chinese,
                            "source": source,
                        }
                    )

            return result

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return None
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return None


if __name__ == "__main__":
    scraper = YoudaoScraper()
    result = scraper.get_word_info("variable")
    print(result)
