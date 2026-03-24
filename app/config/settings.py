import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    def __init__(self):
        self.GROQ_API_KEY = os.getenv("GROQ_API_KEY")
        self.MODEL_NAME = "llama-3.1-8b-instant"  # free + stable

        # Safety check
        if not self.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not found in .env")

# Create a reusable instance
settings = Settings()