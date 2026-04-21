from typing import Optional # 값이 있을 수도 있고 없을 수도 있다
# cookie:요청에 들어온 쿠키 값을 읽기 위해 사용
# header: 요청 헤더에 들어온 값을 읽기 위해 사용
from fastapi import APIRouter, Cookie, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["chat"]) #tags=["chat"]는 문서 docs에서 chat 그룹으로 묶어 표시
service = ChatService()

# 메세지 저장 api
@router.post("/", response_model=ChatResponse)
def save_chat(
    request: ChatRequest,
    session_id: Optional[str] = Cookie(default=None, alias="session_id"),
):
    if not session_id:
        raise HTTPException(status_code=401, detail="유효한 세션이 없습니다.")

    return service.save_user_message(session_id, request.message)

# 채팅 기록 조회 api
@router.get("/history")
def get_history(
    session_id: Optional[str] = Cookie(default=None, alias="session_id"),
):
    if not session_id:
        raise HTTPException(status_code=401, detail="유효한 세션이 없습니다.")

    return {
        "session_id": session_id,
        "messages": service.get_chat_history(session_id)
    }