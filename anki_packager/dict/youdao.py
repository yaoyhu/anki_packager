import asyncio
import os
import re
import shutil
import tempfile
import aiohttp
from gtts import gTTS
from bs4 import BeautifulSoup
from typing import Dict, Optional
from anki_packager.logger import logger


class YoudaoScraper:
    def __init__(self):
        self.base_url = "https://m.youdao.com/result"
        self.tmp = tempfile.mkdtemp()

    async def __aenter__(self):
        """进入 async with 时被调用"""
        self._session = aiohttp.ClientSession(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
            }
        )
        return self  # 返回实例本身

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """离开 async with 时被调用，确保 Session 被关闭"""
        await self._session.close()
        try:
            self._clean_temp_dir()
        except Exception as e:
            logger.error(f"Error cleaning up audio files: {e}")

    async def _get_audio(self, word: str):
        """return the filename of the audio and the temp directory that needs to be cleaned up"""
        filename = os.path.join(self.tmp, f"{word}.mp3")
        loop = asyncio.get_running_loop()

        def generate_and_save_audio():
            """A wrapper function for the blocking gTTS calls."""
            tts = gTTS(text=word, lang="en")
            tts.save(filename)

        await loop.run_in_executor(None, generate_and_save_audio)

        return filename

    def _clean_temp_dir(self):
        """Clean up a temporary directory and its contents."""
        try:
            if os.path.exists(self.tmp):
                shutil.rmtree(self.tmp)
                logger.info(f"音频临时文件夹已清理: {self.tmp}")
        except Exception as e:
            logger.error(f"音频临时文件夹 {self.tmp} 清理失败: {e}")

    async def get_word_info(self, word: str) -> Optional[Dict]:
        try:
            params = {"word": word, "lang": "en"}

            async with self._session.get(self.base_url, params=params) as response:
                response.raise_for_status()
                r_text = await response.text()
                soup = BeautifulSoup(r_text, "html.parser")

            result = {
                "word": word,
                "example_phrases": [],
                "example_sentences": [],
            }


            all_uls = soup.find_all("ul", class_="")
            # Extract example phrases
            if len(all_uls) > 0:
                phrase_ul = all_uls[0]
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
            if len(all_uls) > 1:
                sentence_ul = all_uls[1]
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

        except aiohttp.ClientError as e:
            logger.error(f"Request error: {e}")
            return None
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return None


if __name__ == "__main__":
    async def main():
        async with YoudaoScraper() as youdao:
            result = asyncio.run(youdao.get_word_info("variable"))
            print(result)
    asyncio.run(main())
