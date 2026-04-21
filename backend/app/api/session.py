from typing import Optional
from fastapi import APIRouter, Response, Cookie, HTTPException
from app.services.session_service import SessionService

router = APIRouter(prefix="/session", tags=["session"]) #tags=["session"]는 문서 docs에서 session 그룹으로 묶어 표시
service = SessionService()


@router.post("/")
def create_session(response: Response):
    result = service.create_session()

    response.set_cookie(
        key="session_id",
        value=result["session_id"],
        httponly=True,
        secure=False, # https면 ture
        samesite="lax",
        max_age=result["expires_in"],
        path="/"
    )
    return result

# 현재 세션 확인 / 갱신
@router.get("/me")
def get_current_session(session_id: Optional[str] = Cookie(default=None)):
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id 쿠키가 없습니다.")
    return service.touch_session(session_id)

# 세션 삭제하기
@router.delete("/")
def delete_current_session(session_id: Optional[str] = Cookie(default=None)):
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id 쿠키가 없습니다.")
    service.delete_session(session_id)
    return {"message": "세션이 삭제되었습니다."}