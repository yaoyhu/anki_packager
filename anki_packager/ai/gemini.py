import json
from google import genai
from google.genai import types
from anki_packager.prompt import prompts


class Gemini:
    def __init__(self, model: str, api_key: str, api_base: str = None):
        self.model = model
        self.client = genai.Client(api_key=api_key)

    def explain(self, word: str):
        try:
            # https://github.com/googleapis/python-genai#system-instructions-and-other-configs
            response = self.client.models.generate_content(
                model=self.model,
                contents=word,
                config=types.GenerateContentConfig(
                    system_instruction=prompts["gemini"],
                    temperature=0.3,
                ),
            )
            result = response.candidates[0].content.parts[0].text
            ## remove ```json and ``` for `json.eoads`
            result = result.replace("```json", "").replace("\n```", "").strip()
            return json.loads(result)
        except Exception as e:
            return {"error": str(e)}
