from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from dotenv import load_dotenv
from pydub import AudioSegment
import os
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 환경변수 로드
load_dotenv()

# FastAPI 앱 생성
app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI 클라이언트 초기화
client = OpenAI()

@app.post("/api/ai/stt/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    temp_path = f"temp_{audio_file.filename}"
    chunk_paths = []
    
    try:
        logger.info(f"Received file: {audio_file.filename}, Content-Type: {audio_file.content_type}")
        
        # 업로드된 파일을 임시 저장
        content = await audio_file.read()
        with open(temp_path, 'wb') as f:
            f.write(content)
        
        file_size = os.path.getsize(temp_path)
        logger.info(f"File size: {file_size / (1024*1024):.2f} MB")

        # 25MB 미만 파일은 직접 처리
        if file_size < 25 * 1024 * 1024:
            logger.info("Processing small file directly")
            with open(temp_path, 'rb') as f:
                transcript = client.audio.transcriptions.create(
                    file=f,
                    model="whisper-1",
                    language="ko",
                    response_format="text"
                )
            return {"text": transcript}
        
        # 큰 파일 청크 처리
        logger.info("Processing large file in chunks")
        audio = AudioSegment.from_file(temp_path)
        chunk_length = 30 * 1000  # 30초
        
        # 오디오 분할
        transcripts = []
        for i in range(0, len(audio), chunk_length):
            chunk = audio[i:i + chunk_length]
            chunk_path = f"chunk_{i}.wav"
            chunk_paths.append(chunk_path)
            chunk.export(chunk_path, format="wav")
            
            # 각 청크 처리
            with open(chunk_path, 'rb') as f:
                transcript = client.audio.transcriptions.create(
                    file=f,
                    model="whisper-1",
                    language="ko",
                    response_format="text"
                )
                transcripts.append(transcript)
        
        return {"text": " ".join(transcripts)}
        
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}", exc_info=True)
        return {"error": str(e)}
    
    finally:
        # 임시 파일 정리
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
            for chunk_path in chunk_paths:
                if os.path.exists(chunk_path):
                    os.remove(chunk_path)
        except Exception as e:
            logger.error(f"Error cleaning up temporary files: {str(e)}")