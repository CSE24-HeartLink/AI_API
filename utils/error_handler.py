import logging
import os
from functools import wraps
import sys

# 상위 디렉토리 경로를 추가하여 config.py import
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

# config와 logger import
from config import ERROR_MESSAGES, UPLOAD_CONFIG
from logger import setup_logger  # 상대 경로 대신 절대 경로 사용

# logger 초기화
logger = setup_logger(__name__)

class ErrorHandler:
    @staticmethod
    def handle_api_error(func):
        """API 에러 처리 데코레이터"""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                error_type = func.__name__
                error_message = ERROR_MESSAGES.get(
                    f"{error_type}_error",
                    "알 수 없는 오류가 발생했습니다."
                )
                logger.error(f"{error_type}: {str(e)}")
                return {"error": error_message, "detail": str(e)}
        return wrapper

    @staticmethod
    def validate_file_type(file, allowed_types):
        """파일 타입 검증"""
        if file.content_type not in allowed_types:
            raise ValueError(ERROR_MESSAGES["invalid_file_type"])

    @staticmethod
    def validate_file_size(file):
        """파일 크기 검증"""
        if file.size > UPLOAD_CONFIG["max_file_size"]:
            raise ValueError(ERROR_MESSAGES["file_too_large"])