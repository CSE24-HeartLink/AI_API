from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

# API Keys & Credentials
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# ChatGPT Configuration
CHAT_CONFIG = {
    "model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 150,
    "presence_penalty": 0.6,
    "frequency_penalty": 0.0,
    "stream_chunk_size": 1024,
    "timeout": 30
}

# DALLE Configuration
DALLE_CONFIG = {
    "model": "dall-e-3",
    "image_size": "1024x1024",
    "quality": "standard",
    "n": 1,  # number of images to generate
    "output_format": "png",
    "temp_image_dir": "temp_images/"  # 임시 이미지 저장 디렉토리
}

# STT Configuration (향후 구현될 STT 모델을 위한 설정)
STT_CONFIG = {
    "model_path": "models/stt_model.pt",
    "sample_rate": 16000,
    "language": "ko",
    "chunk_size": 1024,
    "audio_format": "wav"
}

# Server Configuration
SERVER_CONFIG = {
    "host": "0.0.0.0",
    "port": int(os.getenv("PORT", 8000)),
    "debug": bool(os.getenv("DEBUG", True))
}

# File Upload Configuration
UPLOAD_CONFIG = {
    "max_file_size": 10 * 1024 * 1024,  # 10MB
    "allowed_audio_types": ["audio/wav", "audio/mp3"],
    "allowed_text_types": ["text/plain"],
    "temp_upload_dir": "temp_uploads/"
}

# Error Messages
ERROR_MESSAGES = {
    "chat_error": "챗봇 응답 생성 중 오류가 발생했습니다.",
    "dalle_error": "이미지 생성 중 오류가 발생했습니다.",
    "stt_error": "음성 인식 처리 중 오류가 발생했습니다.",
    "file_upload_error": "파일 업로드 중 오류가 발생했습니다.",
    "invalid_file_type": "지원하지 않는 파일 형식입니다.",
    "file_too_large": "파일 크기가 너무 큽니다."
}

# Logging Configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.FileHandler",
            "filename": "ai_module.log",
            "mode": "a"
        }
    },
    "loggers": {
        "": {  # root logger
            "handlers": ["default", "file"],
            "level": "INFO",
            "propagate": True
        }
    }
}

# Create necessary directories
os.makedirs(DALLE_CONFIG["temp_image_dir"], exist_ok=True)
os.makedirs(UPLOAD_CONFIG["temp_upload_dir"], exist_ok=True)