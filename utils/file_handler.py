import os
import shutil
from datetime import datetime
from sys import path
path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import UPLOAD_CONFIG, DALLE_CONFIG

class FileHandler:
    def __init__(self):
        self.upload_dir = UPLOAD_CONFIG["temp_upload_dir"]
        self.image_dir = DALLE_CONFIG["temp_image_dir"]

    async def save_upload_file(self, file, prefix="upload"):
        """업로드된 파일 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}_{file.filename}"
        file_path = os.path.join(self.upload_dir, filename)
        
        try:
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            return file_path
        except Exception as e:
            raise IOError(f"File save error: {str(e)}")

    def save_image(self, image_data, filename):
        """이미지 데이터 저장"""
        file_path = os.path.join(self.image_dir, filename)
        try:
            with open(file_path, "wb") as f:
                f.write(image_data)
            return file_path
        except Exception as e:
            raise IOError(f"Image save error: {str(e)}")

    def cleanup_old_files(self, directory, max_age_hours=24):
        """오래된 임시 파일 정리"""
        try:
            current_time = datetime.now()
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                file_age = current_time - datetime.fromtimestamp(
                    os.path.getctime(file_path))
                if file_age.total_seconds() > max_age_hours * 3600:
                    os.remove(file_path)
        except Exception as e:
            raise IOError(f"Cleanup error: {str(e)}")