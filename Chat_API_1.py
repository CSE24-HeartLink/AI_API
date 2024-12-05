from fastapi import FastAPI
from openai import OpenAI
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
import os

app = FastAPI()
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API 키가 설정되지 않았습니다")

client = OpenAI(api_key=api_key)

# 메시지 모델
class Message(BaseModel):
   role: str  # system/user/assistant
   content: str

# 채팅 요청 모델
class ChatRequest(BaseModel):
   messages: List[Message]
   stream: bool = False  # 스트리밍 옵션

@app.post("/chat")
async def chat_with_ai(request: ChatRequest):
   try:
       # 메시지 변환
       messages = [{"role": m.role, "content": m.content} for m in request.messages]
       
       # OpenAI API 호출
       if request.stream:
           # 스트리밍 응답
           completion = client.chat.completions.create(
               model="gpt-3.5-turbo",
               messages=messages,
               stream=True
           )
           
           async def generate():
               response_text = []
               async for chunk in completion:
                   if chunk.choices[0].delta.content:
                       chunk_content = chunk.choices[0].delta.content
                       response_text.append(chunk_content)
                       yield chunk_content
           return generate()
           
       else:
           # 일반 응답
           completion = client.chat.completions.create(
               model="gpt-3.5-turbo",
               messages=messages
           )
           
           return {
               "response": completion.choices[0].message.content,
               "role": "assistant"
           }
           
   except Exception as e:
       return {"error": str(e)}