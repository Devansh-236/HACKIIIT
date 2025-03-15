import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    AZURE_OPENAI_API_BASE = os.getenv("AZURE_OPENAI_API_BASE", "https://aoi-iiit-hack-2.openai.azure.com")
    AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")

    @staticmethod
    def validate():
        if not Settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is missing. Please set it in the environment variables.")

Settings.validate()
