from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import session, chat
from app.api import ask


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","http://192.168.0.45:5173"],  # React 주소
    allow_credentials=True,                   # 쿠키/세션 허용
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(session.router)
app.include_router(chat.router)
app.include_router(ask.router)

@app.get("/")
def root():
    return {"message": "chatbot backend is running"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )