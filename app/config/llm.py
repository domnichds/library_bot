import os
from dotenv import load_dotenv

load_dotenv()

LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_FOLDER_ID = os.getenv("LLM_FOLDER_ID")
LLM_URL = os.getenv(
    "LLM_URL",
    "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
)

