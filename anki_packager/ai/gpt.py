from typing import Dict
import openai
import json


class ChatGPT:
    def __init__(self, model: str, api_key: str, api_base: str):
        self.model = model
        self.client = openai.OpenAI(api_key=api_key, base_url=api_base)

    def explain(self, word: str) -> Dict[str, any]:
        prompt = """You are a mnemonic word assistant. 
                Each time I give you a word, you must strictly return a JSON response 
                in the following format without any additional explanations or comments:
                {
                    "word": "<word>",
                    "ai": {
                        "etymology": "<A brief description of the word's origin, including its linguistic roots and historical evolution>",
                        "mnemonic": "<A vivid association or memory trick to help remember the word's meaning>"
                    }, 
                    "synonyms": "<Chinese (English), Chinese (English), Chinese (English), ...>",
                    "antonyms": "<Chinese (English), Chinese (English), Chinese (English), ...>"
                }"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": word},
                ],
                temperature=0.7,
                max_tokens=500,
            )
            result = response.choices[0].message.content
            return json.loads(result)
        except Exception as e:
            return {"error": str(e)}
