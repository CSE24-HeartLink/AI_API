from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import WhisperForConditionalGeneration, WhisperTokenizer, WhisperFeatureExtractor
import soundfile as sf
from pydub import AudioSegment
import io
from contextlib import asynccontextmanager
import logging
from datetime import datetime
import os
import torch
from huggingface_hub import login
from dotenv import load_dotenv
load_dotenv()

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('asr_api.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 전역 변수 선언
model = None
tokenizer = None
feature_extractor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, tokenizer, feature_extractor
    
    MODEL_ID = "jyering/whisper-ko-finetuned"
    HF_TOKEN = os.getenv("HF_TOKEN")
    if not HF_TOKEN:
        raise ValueError("HuggingFace token not found in environment variables")

    login(token=HF_TOKEN)
    
    try:
        logger.info(f"Authenticating with HuggingFace Hub")
        login(token=HF_TOKEN)
        
        logger.info(f"Loading model from HuggingFace Hub: {MODEL_ID}")
        model = WhisperForConditionalGeneration.from_pretrained(MODEL_ID)
        tokenizer = WhisperTokenizer.from_pretrained(MODEL_ID)
        feature_extractor = WhisperFeatureExtractor.from_pretrained(MODEL_ID)
        
        model.eval()
        
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise
    
    yield
    
    logger.info("Cleaning up resources...")
    model = None
    tokenizer = None
    feature_extractor = None

app = FastAPI(
    title="Speech Recognition API",
    description="한국어 음성 데이터로 fine-tuning한 Whisper 모델을 사용한 음성 인식 API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/ai/stt/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """음성 파일을 텍스트로 변환 - 큰 파일은 청크 단위로 처리"""
    
    # 지원하는 파일 형식 체크
    supported_formats = ['.m4a', '.wav', '.mp3']
    file_ext = os.path.splitext(audio_file.filename)[1].lower()
    if file_ext not in supported_formats:
        return {"error": f"Unsupported file format: {file_ext}"}

    try:
        # 임시 파일로 저장
        temp_path = f"temp_{audio_file.filename}"
        
        with open(temp_path, 'wb') as f:
            content = await audio_file.read()
            f.write(content)
        
        try:
            # 파일 크기 확인 (25MB)
            if os.path.getsize(temp_path) < 25 * 1024 * 1024:
                # 작은 파일 처리
                try:
                    audio = AudioSegment.from_file(temp_path)
                    audio = audio.set_frame_rate(16000).set_channels(1)
                    wav_path = f"temp_wav_{audio_file.filename.split('.')[0]}.wav"
                    audio.export(wav_path, format="wav")
                    
                    audio_array, sampling_rate = sf.read(wav_path)
                    features = feature_extractor(
                        audio_array,
                        sampling_rate=sampling_rate,
                        return_tensors="pt"
                    ).input_features
                    
                    with torch.no_grad():
                        predicted_ids = model.generate(features)[0]
                    
                    transcription = tokenizer.decode(predicted_ids, skip_special_tokens=True)
                    
                    # 임시 파일 삭제
                    os.remove(wav_path)
                    
                    return {"text": transcription}
                    
                except Exception as e:
                    logger.error(f"Error processing small file: {str(e)}")
                    return {"error": f"Failed to process audio file: {str(e)}"}
            
            else:
                # 큰 파일 청크 단위 처리
                try:
                    audio = AudioSegment.from_file(temp_path)
                    audio = audio.set_frame_rate(16000).set_channels(1)
                    chunk_length = 30 * 1000  # 30초
                    transcripts = []
                    
                    # 오디오 분할 및 처리
                    for i in range(0, len(audio), chunk_length):
                        chunk = audio[i:i + chunk_length]
                        chunk_path = f"chunk_{i}.wav"
                        chunk.export(chunk_path, format="wav")
                        
                        try:
                            audio_array, sampling_rate = sf.read(chunk_path)
                            features = feature_extractor(
                                audio_array,
                                sampling_rate=sampling_rate,
                                return_tensors="pt"
                            ).input_features
                            
                            with torch.no_grad():
                                predicted_ids = model.generate(features)[0]
                            
                            chunk_transcription = tokenizer.decode(predicted_ids, skip_special_tokens=True)
                            transcripts.append(chunk_transcription)
                            
                        finally:
                            # 청크 파일 삭제
                            if os.path.exists(chunk_path):
                                os.remove(chunk_path)
                    
                    # 전체 텍스트 결합
                    final_transcription = ' '.join(transcripts)
                    
                    return {"text": final_transcription}
                    
                except Exception as e:
                    logger.error(f"Error processing large file in chunks: {str(e)}")
                    return {"error": f"Failed to process large audio file: {str(e)}"}
                    
        finally:
            # 원본 임시 파일 삭제
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    except Exception as e:
        logger.error(f"Error in transcribe_audio: {str(e)}")
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    """API 헬스 체크"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)