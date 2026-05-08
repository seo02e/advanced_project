import logging
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# backend/.env 파일을 앱 시작 시 환경변수로 로드
BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")

from app.api import session, chat
from app.core.logger import setup_logging
from app.core.exception_handlers import register_exception_handlers
from app.infra.scheduler import start_scheduler, end_scheduler
from app.services.policy_from_api_service import policy_from_api
from app.services.policy_from_crawling_service import save_policy_crawling_chunks


################## 초기 세팅 ######################
## 로거 기본 세팅
setup_logging()

"""
    __name__ : 현재 모듈 경로 가져옴
    
    예시)
    app/
    ├─ main.py
    └─ db/
        └─ config.py
    
    # main.py 에서 실행
    logger = logging.getLogger(__name__)
    print(__name__)
    -> app.main
    
    # config.py 에서 실행
    logger = logging.getLogger(__name__)
    print(__name__)
    -> app.db.config 
    
    ** 모듈 경로에 따라 logger 찍는게 정석 **
    - 각 파일에서 logger 를 사용시
    logger = logging.getLogger(__name__) 코드 작성
    
    ** 로거 메소드 **
    ## 로거 레벨
    # 레벨	        숫자값	        의미
    # CRITICAL	    50	        시스템이 거의 죽은 수준 (즉시 대응 필요)
    # ERROR	        40	        기능 실패 (예외 발생)
    # WARNING	    30	        문제 가능성 있음 (경고)
    # INFO	        20	        정상 동작 정보
    # DEBUG	        10	        디버깅용 상세 정보
    # NOTSET	    0	        설정 없음 (상위 logger 따름)
    
    ** 사용법 **
    - 위 로거 레벨 용도에 맞춰서 사용
    ex)
    logger.info("표출할 내용")
    logger.error("표출할 내용")
"""

logger = logging.getLogger(__name__)


## 스케줄러 설정
# 시작과 종료의 로직을 하나의 함수로 관리하게 해줌
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("lifespan start")
    logger.info("scheduler start")
    
    start_scheduler()
    
    yield # yield 기준 위로 서버 실행시 작동 / 아래로 서버 종료시 작동
    
    end_scheduler()
    
    logger.info("scheduler end")
    logger.info("lifespan end")


app = FastAPI(lifespan=lifespan)


logger.info("chatbot backend is running")


## 전역 예외처리 세팅
register_exception_handlers(app)


## CORS 세팅
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://192.168.0.45:5173",
        "http://192.168.0.65:5173",
        "http://192.168.45.167:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
##################################################

# 수동 api 배치
@app.get("/youth-policy-api-batch")
def get_data_from_api():
    policy_from_api()

# 수동 crawling 배치
@app.get("/youth-policy-crawling-batch")
def get_data_from_crawling():
    save_policy_crawling_chunks()
    

app.include_router(session.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {"message": "chatbot backend is running"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )