from fastapi import FastAPI, UploadFile, File  # FastAPI 웹 프레임워크와 파일 업로드 기능
from openai import OpenAI  # OpenAI API 사용
from dotenv import load_dotenv  # 환경변수 로드
from pydub import AudioSegment
import os  # 파일/디렉토리 작업

app = FastAPI()  # FastAPI 인스턴스 생성
client = OpenAI()

@app.post("/transcribe")  # POST /transcribe 엔드포인트 생성
async def transcribe_audio(audio_file: UploadFile = File(...)):  # 음성 파일 받기
   try:
       # 업로드된 파일을 임시 저장
       temp_path = f"temp_{audio_file.filename}"
       with open(temp_path, 'wb') as f:
           content = await audio_file.read()
           f.write(content)
       
       # Whisper API로 음성->텍스트 변환

       # 파일 크기 확인 (25MB)
       if os.path.getsize(temp_path) < 25 * 1024 * 1024:
           # 작은 파일은 바로 처리
           with open(temp_path, 'rb') as f:
               transcript = client.audio.transcriptions.create(
                   file=f,
                   model="whisper-1",
                   language="ko",
                   response_format="text"
               )
           os.remove(temp_path)
           return {"text": transcript}
        
        # 큰 파일 분할 처리
       audio = AudioSegment.from_file(temp_path)
       chunk_length = 30 * 1000  # 30초
       chunks = []
       
       # 오디오 분할
       for i in range(0, len(audio), chunk_length):
           chunk = audio[i:i + chunk_length]
           chunk_path = f"chunk_{i}.wav"
           chunk.export(chunk_path, format="wav")
           chunks.append(chunk_path)

       # 각 청크 처리
       transcripts = []
       for chunk_path in chunks:
           with open(chunk_path, 'rb') as f:
               transcript = client.audio.transcriptions.create(
                   file=f,
                   model="whisper-1",
                   language="ko",
                   response_format="text"
               )
               transcripts.append(transcript)
           os.remove(chunk_path)

       os.remove(temp_path)
       return {"text": " ".join(transcripts)}
       
   except Exception as e:
       return {"error": str(e)}  # 에러 처리