import os
import numpy as np
from pydub import AudioSegment
from sys import path
path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import STT_CONFIG

class AudioProcessor:
    def __init__(self):
        self.sample_rate = STT_CONFIG["sample_rate"]
        self.supported_formats = STT_CONFIG["audio_format"]

    def load_audio(self, file_path):
        """오디오 파일 로드 및 전처리"""
        try:
            audio = AudioSegment.from_file(file_path)
            audio = audio.set_frame_rate(self.sample_rate)
            audio = audio.set_channels(1)  # mono
            return np.array(audio.get_array_of_samples())
        except Exception as e:
            raise ValueError(f"Audio processing error: {str(e)}")

    def normalize_audio(self, audio_array):
        """오디오 정규화"""
        return audio_array / np.max(np.abs(audio_array))

    def split_audio(self, audio_array, chunk_size=STT_CONFIG["chunk_size"]):
        """오디오를 청크로 분할"""
        return [audio_array[i:i + chunk_size] 
                for i in range(0, len(audio_array), chunk_size)]