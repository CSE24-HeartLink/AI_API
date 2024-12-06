from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import StreamingResponse
from openai import OpenAI, APIError
from pydantic import BaseModel, Field, validator
from typing import List, Optional, AsyncGenerator
from fastapi.middleware.cors import CORSMiddleware
import logging
from dotenv import load_dotenv
import os
from functools import lru_cache

# 환경변수 로드
load_dotenv(override=True)

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 운영환경에서는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

    @validator('role')
    def validate_role(cls, v):
        if v not in ['system', 'user', 'assistant']:
            raise ValueError('역할은 system, user, assistant 중 하나여야 합니다')
        return v

class ChatRequest(BaseModel):
    messages: List[Message]
    stream: bool = Field(default=False)
    temperature: Optional[float] = Field(default=0.7, ge=0, le=2)
    max_tokens: Optional[int] = Field(default=1000, gt=0)

def validate_api_key(api_key: str) -> bool:
    return bool(api_key and api_key.startswith("sk-"))

@lru_cache()
def get_settings():
    api_key = os.getenv('OPENAI_API_KEY')
    if not validate_api_key(api_key):
        raise ValueError("잘못된 API 키 형식입니다. API 키를 확인해주세요.")
    return {"api_key": api_key}

async def get_openai_client():
    try:
        settings = get_settings()
        client = OpenAI(api_key=settings["api_key"])
        return client
    except ValueError as e:
        logger.error(f"API 키 검증 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="API 키 설정 오류")
    except Exception as e:
        logger.error(f"OpenAI 클라이언트 초기화 실패: {str(e)}")
        raise HTTPException(status_code=500, detail="API 클라이언트 초기화 실패")

async def stream_response(response) -> AsyncGenerator[str, None]:
    try:
        for chunk in response:
            if chunk and chunk.choices and chunk.choices[0].delta.content:
                yield f"data: {chunk.choices[0].delta.content}\n\n"
    except Exception as e:
        logger.error(f"스트리밍 처리 오류: {str(e)}")
        yield f"data: {str(e)}\n\n"
    finally:
        yield "data: [DONE]\n\n"

@app.post("/api/ai/chatbot/chat")
async def chat_with_ai(request: ChatRequest, client: OpenAI = Depends(get_openai_client)):
    try:
        logger.info(f"채팅 요청 수신: {len(request.messages)} 메시지")
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream
        )

        if request.stream:
            return StreamingResponse(
                stream_response(response),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                }
            )
        
        return response.choices[0].message

    except APIError as e:
        logger.error(f"OpenAI API 오류: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"서버 오류: {str(e)}")
        raise HTTPException(status_code=500, detail="내부 서버 오류")

@app.get("/api/ai/chatbot/health")
async def health_check():
    try:
        settings = get_settings()  # API 키 검증 포함
        return {"status": "healthy", "api_key_valid": True}
    except ValueError:
        return {"status": "unhealthy", "api_key_valid": False}


# from fastapi import FastAPI, HTTPException, Depends
# from fastapi.responses import StreamingResponse
# from openai import OpenAI, APIError
# from pydantic import BaseModel, Field, validator
# from typing import List, Optional, AsyncGenerator
# from fastapi.middleware.cors import CORSMiddleware
# import logging
# from dotenv import load_dotenv
# import os
# from functools import lru_cache

# # 환경변수 로드
# load_dotenv()

# # 로깅 설정
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = FastAPI()

# # CORS 설정
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # 실제 운영환경에서는 특정 도메인으로 제한
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class Message(BaseModel):
#     role: str
#     content: str

#     @validator('role')
#     def validate_role(cls, v):
#         if v not in ['system', 'user', 'assistant']:
#             raise ValueError('역할은 system, user, assistant 중 하나여야 합니다')
#         return v

# class ChatRequest(BaseModel):
#     messages: List[Message]
#     stream: bool = Field(default=False)
#     temperature: Optional[float] = Field(default=0.7, ge=0, le=2)
#     max_tokens: Optional[int] = Field(default=1000, gt=0)

# def validate_api_key(api_key: str) -> bool:
#     return bool(api_key and api_key.startswith("sk-"))

# @lru_cache()
# def get_settings():
#     api_key = os.getenv('OPENAI_API_KEY')
#     if not validate_api_key(api_key):
#         raise ValueError("잘못된 API 키 형식입니다. API 키를 확인해주세요.")
#     return {"api_key": api_key}

# async def get_openai_client():
#     try:
#         settings = get_settings()
#         client = OpenAI(api_key=settings["api_key"])
#         return client
#     except ValueError as e:
#         logger.error(f"API 키 검증 실패: {str(e)}")
#         raise HTTPException(status_code=500, detail="API 키 설정 오류")
#     except Exception as e:
#         logger.error(f"OpenAI 클라이언트 초기화 실패: {str(e)}")
#         raise HTTPException(status_code=500, detail="API 클라이언트 초기화 실패")

# async def stream_response(response) -> AsyncGenerator[str, None]:
#     try:
#         for chunk in response:
#             if chunk and chunk.choices and chunk.choices[0].delta.content:
#                 yield f"data: {chunk.choices[0].delta.content}\n\n"
#     except Exception as e:
#         logger.error(f"스트리밍 처리 오류: {str(e)}")
#         yield f"data: {str(e)}\n\n"
#     finally:
#         yield "data: [DONE]\n\n"

# @app.post("/api/ai/chatbot/chat")
# async def chat_with_ai(request: ChatRequest, client: OpenAI = Depends(get_openai_client)):
#     try:
#         logger.info(f"채팅 요청 수신: {len(request.messages)} 메시지")
#         messages = [{"role": m.role, "content": m.content} for m in request.messages]
        
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=messages,
#             temperature=request.temperature,
#             max_tokens=request.max_tokens,
#             stream=request.stream
#         )

#         if request.stream:
#             return StreamingResponse(
#                 stream_response(response),
#                 media_type="text/event-stream",
#                 headers={
#                     "Cache-Control": "no-cache",
#                     "Connection": "keep-alive",
#                 }
#             )
        
#         return response.choices[0].message

#     except APIError as e:
#         logger.error(f"OpenAI API 오류: {str(e)}")
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         logger.error(f"서버 오류: {str(e)}")
#         raise HTTPException(status_code=500, detail="내부 서버 오류")

# @app.get("/api/ai/chatbot/health")
# async def health_check():
#     try:
#         settings = get_settings()  # API 키 검증 포함
#         return {"status": "healthy", "api_key_valid": True}
#     except ValueError:
#         return {"status": "unhealthy", "api_key_valid": False}