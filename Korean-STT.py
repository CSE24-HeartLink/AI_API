from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from transformers import WhisperForConditionalGeneration, WhisperTokenizer, WhisperFeatureExtractor
import soundfile as sf
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
    """음성 파일을 텍스트로 변환"""
    try:
        # 임시 파일로 저장
        temp_path = f"temp_{audio_file.filename}"
        with open(temp_path, 'wb') as f:
            content = await audio_file.read()
            f.write(content)
        
        try:
            # 오디오 파일 로드
            audio_array, sampling_rate = sf.read(temp_path)
            
            # feature 추출
            features = feature_extractor(
                audio_array,
                sampling_rate=sampling_rate,
                return_tensors="pt"
            ).input_features
            
            # 음성 인식 수행
            with torch.no_grad():
                predicted_ids = model.generate(features)[0]
            
            # 텍스트 변환
            transcription = tokenizer.decode(predicted_ids, skip_special_tokens=True)
            
            return {"text": transcription}
            
        finally:
            # 임시 파일 삭제
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