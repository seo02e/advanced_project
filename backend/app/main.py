from fastapi import FastAPI
from app.api import session, chat

app = FastAPI()

app.include_router(session.router)
app.include_router(chat.router)


@app.get("/")
def root():
    return {"message": "chatbot backend is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",  # 모듈 경로
        host="0.0.0.0",  # 외부 접속 허용
        port=8000,
        reload=True     # 코드 변경 시 자동 재시작 (개발 환경)
    )