import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self):
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")

        # 🔥 Separate models
        self.GEN_MODEL = "llama-3.1-8b-instant"
        self.EVAL_MODEL = "llama-3.1-8b-instant"

        if not self.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found")

settings = Settings()