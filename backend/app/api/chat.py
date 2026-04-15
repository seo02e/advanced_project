from typing import Optional # 값이 있을 수도 있고 없을 수도 있다
# cookie:요청에 들어온 쿠키 값을 읽기 위해 사용
# header: 요청 헤더에 들어온 값을 읽기 위해 사용
from fastapi import APIRouter, Cookie, Header, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"])
service = ChatService()


@router.post("/", response_model=ChatResponse)
def save_chat(
    request: ChatRequest,
    session_id_cookie: Optional[str] = Cookie(default=None, alias="session_id"),
    session_id_header: Optional[str] = Header(default=None, alias="X-Session-Id")
):
    session_id = session_id_cookie or session_id_header

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id가 필요합니다.")

    return service.save_user_message(session_id, request.message)


@router.get("/history")
def get_history(
    session_id_cookie: Optional[str] = Cookie(default=None, alias="session_id"),
    session_id_header: Optional[str] = Header(default=None, alias="X-Session-Id")
):
    session_id = session_id_cookie or session_id_header

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id가 필요합니다.")

    return {
        "session_id": session_id,
        "messages": service.get_chat_history(session_id)
    }