from typing import Optional
from fastapi import APIRouter, Response, Cookie, HTTPException
from app.services.session_service import SessionService

router = APIRouter(prefix="/session", tags=["session"])
service = SessionService()


@router.post("/")
def create_session(response: Response):
    result = service.create_session()

    response.set_cookie(
        key="session_id",
        value=result["session_id"],
        httponly=True,
        samesite="lax",
        max_age=result["expires_in"]
    )
    return result


@router.get("/me")
def get_current_session(session_id: Optional[str] = Cookie(default=None)):
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id 쿠키가 없습니다.")
    return service.touch_session(session_id)


@router.delete("/")
def delete_current_session(session_id: Optional[str] = Cookie(default=None)):
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id 쿠키가 없습니다.")
    service.delete_session(session_id)
    return {"message": "세션이 삭제되었습니다."}