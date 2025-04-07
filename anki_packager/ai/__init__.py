from anki_packager.ai.gpt import ChatGPT
from anki_packager.ai.gemini import Gemini
from anki_packager.ai.siliconflow import SiliconFlow

MODEL_DICT = {
    "gpt-4o": ChatGPT,
    "deepseek-ai/DeepSeek-V2.5": SiliconFlow,
    "deepseek-ai/DeepSeek-V3": SiliconFlow,
    "gemini-2.0-flash": Gemini,
}
