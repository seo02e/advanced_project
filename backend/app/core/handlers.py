from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.core.exceptions import AppException
# from sqlalchemy.exc import SQLAlchemyError

def register_exception_handlers(app):
    
    # 전역 핸들러 등록
    @app.exception_handler(AppException)
    async def app_exception_handler(req: Request, exc:AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "message": exc.message
            }
        )
        
    # @app.exception_handler(SQLAlchemyError)
    # async def sqlalchemy_exception_handler(req: Request, exc: SQLAlchemyError):
    #     return JSONResponse(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         content={
    #             "message" : "DB 처리 중 오류가 발생했습니다."
    #         }
    #     )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(req: Request, exc: Exception):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "message" : "서버 내부 오류가 발생했습니다."
            }
        )