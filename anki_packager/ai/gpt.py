from typing import Dict
import openai
import json
from anki_packager.prompt import prompts


class ChatGPT:
    def __init__(self, model: str, api_key: str, api_base: str):
        self.model = model
        self.client = openai.OpenAI(api_key=api_key, base_url=api_base)

    def explain(self, word: str) -> Dict[str, any]:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompts["openai"]},
                    {"role": "user", "content": word},
                ],
                temperature=0.7,
                max_tokens=500,
            )
            result = response.choices[0].message.content
            if result.startswith("```json"):
                result = result.replace("```json", "").replace("```", "")
            return json.loads(result)
        except Exception as e:
            return {"error": str(e)}
