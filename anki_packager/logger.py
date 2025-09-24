import logging

# ANSI escape codes for bold blue
BOLD_BLUE = "\033[1;34m"
RESET = "\033[0m"

logging.basicConfig(
    level=logging.INFO,
    format=f"{BOLD_BLUE}[%(filename)s:%(lineno)d:%(funcName)s]{RESET} %(message)s",
    handlers=[logging.FileHandler("anki_packager.log"), logging.StreamHandler()],
)

litellm_logger = logging.getLogger("LiteLLM")
litellm_logger.setLevel(logging.ERROR)
litellm_logger = logging.getLogger("LiteLLM Router")
litellm_logger.setLevel(logging.ERROR)

logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)
