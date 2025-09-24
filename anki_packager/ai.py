from typing import Dict
from litellm import Choices, Message
from litellm.router import Router
from litellm.files.main import ModelResponse
import json
from anki_packager.prompt import PROMPT

from pydantic import BaseModel, Field, ValidationError


class Mnemonic(BaseModel):
    """助记法模型"""

    associative: str = Field(..., description="联想记忆法")
    homophone: str = Field(..., description="谐音记忆法")


class Origin(BaseModel):
    """词源和助记模型"""

    etymology: str = Field(..., description="词源和文化内涵")
    mnemonic: Mnemonic


class Story(BaseModel):
    """场景故事模型"""

    english: str = Field(..., description="英文场景故事")
    chinese: str = Field(..., description="故事的中文翻译")


# 最终的、最顶层的完整数据模型
class WordExplanation(BaseModel):
    """完整的单词解析数据模型"""

    word: str = Field(..., description="用户提供的单词")
    origin: Origin
    tenses: str = Field(..., description="单词的词形变化")
    story: Story





class llm:
    def __init__(self, model_param: list):
        model_list = [
            {
                "model_name": "a",  # 为所有模型统一使用别名 "a"
                "litellm_params": param,
            }
            for param in model_param
        ]
        self.router = Router(model_list)

    async def explain(self, word: str) -> Dict:
        try:
            response = await self.router.acompletion(
                model="a",
                messages=[
                    {"role": "system", "content": PROMPT},
                    {"role": "user", "content": word},
                ],
                temperature=0.3,
                max_tokens=500,
                response_format={"type": "json_object"},
            )
            if isinstance(response, ModelResponse):
                if isinstance(response.choices, list) and response.choices:
                    first_choice = response.choices[0]
                    if (
                        isinstance(first_choice, Choices)
                        and isinstance(first_choice.message, Message)
                        and isinstance(first_choice.message.content, str)
                    ):
                        result_str = first_choice.message.content

            if result_str.startswith("```json"):
                result_str = result_str.strip("```json\n").strip("```")

            # 1. 将字符串解析为 Python 字典
            data = json.loads(result_str)

            # 2. 使用 WordExplanation 模型进行验证和解析
            validated_data = WordExplanation.model_validate(data)

            return validated_data.model_dump()

        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Failed to parse JSON for '{word}': {e}. Raw response: '{result_str[:150]}...'",
                result_str,
                e.pos,
            )
        except ValidationError as e:
            raise ValidationError(f"JSON structure validation failed for '{word}': {e}")
        except Exception as e:
            raise Exception(f"An unexpected error occurred for '{word}': {e}")
