from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HF_TOKEN = os.getenv("HF_TOKEN")

CHAT_CONFIG = {
    "model": "gpt-3.5-turbo"
}

DALLE_CONFIG = {
    "model": "dall-e-3",
    "image_size": "1024x1024",
    "quality": "standard",
    "n": 1
}

WHISPER_CONFIG = {
    "model_id": "jyering/whisper-ko-finetuned"
}