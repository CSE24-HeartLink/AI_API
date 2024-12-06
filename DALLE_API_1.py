# 필요한 라이브러리 임포트
from fastapi import FastAPI, UploadFile, File  # 웹 프레임워크와 파일 업로드 기능
from openai import OpenAI  # OpenAI API 사용
from dotenv import load_dotenv  # 환경변수 로드
import requests  # HTTP 요청
import os  # 파일 시스템 작업

app = FastAPI()  # FastAPI 앱 생성
load_dotenv()  # .env 파일의 환경변수 로드
client = OpenAI()  # OpenAI 클라이언트 초기화

@app.post("/api/ai/img/generate-image")  # /generate-image POST 엔드포인트
async def generate_image(text_file: UploadFile = File(...)):  # 텍스트 파일 받기
   try:
       content = await text_file.read()  # 파일 내용 읽기
       prompt = content.decode('utf-8')  # 바이트를 문자열로 변환

       # DALL-E로 이미지 생성
       response = client.images.generate(
           model="dall-e-3",  # DALL-E 3 모델 사용
           prompt=prompt,  # 텍스트 프롬프트
           size="1024x1024",  # 이미지 크기
           quality="standard",  # 이미지 품질
           n=1  # 생성할 이미지 수
       )

       image_url = response.data[0].url  # 생성된 이미지 URL
       image_data = requests.get(image_url).content  # URL에서 이미지 다운로드

       # 이미지 로컬 저장
       temp_image_path = f"temp_{text_file.filename}.png"  # 임시 파일명
       with open(temp_image_path, 'wb') as f:  # 파일 쓰기
           f.write(image_data)
           
       return {  # URL과 로컬 경로 반환
           "image_url": image_url,
           "local_path": temp_image_path
       }

   except Exception as e:  # 에러 처리
       return {"error": str(e)}