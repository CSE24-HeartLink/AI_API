import logging
from sys import path
import os
path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import LOGGING_CONFIG

def setup_logger(name):
    """로거 설정"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        formatter = logging.Formatter(
            LOGGING_CONFIG["formatters"]["standard"]["format"]
        )
        
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File Handler
        file_handler = logging.FileHandler("ai_module.log")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        logger.setLevel(logging.INFO)
    
    return logger