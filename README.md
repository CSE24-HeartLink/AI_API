# AI API

AI 기반 대화, 이미지 생성, 음성 인식을 제공하는 API 서비스입니다.

## Features
- ChatGPT API: 텍스트 기반 대화
- DALL-E API: 텍스트 프롬프트 기반 이미지 생성
- Whisper API: 한국어 최적화 음성-텍스트 변환

## Requirements
```
fastapi==0.100.0
openai==1.3.0
pydantic==2.0.2
python-dotenv==1.0.0
requests==2.31.0
transformers==4.35.2
soundfile==0.12.1
torch==2.1.1
huggingface-hub==0.19.4
python-multipart==0.0.6
```

## Environment Setup
1. `.env` 파일 생성
```
OPENAI_API_KEY=your_openai_key
HF_TOKEN=your_huggingface_token
```

## API Endpoints

### ChatGPT (`/chat`)
- POST 요청
- 스트리밍/일반 응답 모드 지원
- GPT-3.5-turbo 모델 사용

### DALL-E (`/generate-image`)
- POST 요청
- 1024x1024 해상도 이미지 생성
- DALL-E 3 모델 사용

### Whisper (`/transcribe`)
- POST 요청 
- 한국어 음성인식 최적화
- 파인튜닝된 Whisper 모델 사용

## Usage
```bash
python3 -m uvicorn main:app --reload
```

## API Documentation
FastAPI 자동 문서: `http://localhost:8000/docs`