from uuid import uuid4 # 고유한 세션 id를 만들기 위해 사용
from datetime import datetime, timezone # 시간 기록용 : 세션 생성시간, 마지막 접근 시간을 저장하기 위해 사용
from fastapi import HTTPException
from app.repositories.session_repository import SessionRepository #실제 redis 저장/조회 관련 함수들 있음
from app.core.config import settings # settings.SESSION_TTL_SECONDS : ttl 설정하기 위해 사용

# 세션 생성 규칙 | 세션 조회 시 에러 처리 | 세션 접속 시간 갱신 | 세션 삭제
class SessionService:
    # 서비스 객체가 생성 될때 내부에서 sessionRepository도 같이 준비
    def __init__(self):
        self.repo = SessionRepository()

    # 새 세션을 만드는 핵심함수
    def create_session(self) -> dict:
        # 새로운 세션의 고유 id생성
        session_id = str(uuid4())
        # 생성 시간 utc 기준으로 가져온 뒤 문자열로 반환
        now = datetime.now(timezone.utc).isoformat()

        # 기본 정보 만들기
        session_data = {
            "session_id": session_id,
            "created_at": now,
            "last_accessed_at": now
        }

        # 기본 정보 저장 이 함수는 session_repository여기에 있음
        self.repo.create_session(session_id, session_data)

        # 이것은 ai에서 받는 것이기 때문에 수정 할 수 있음
        initial_state = {
            "age": None,
            "region": None,
            "employment_status": None,
            "housing_status": None,
            "income_level": None,
            "interest_tags": [],
            "unknown_fields": [],
            "raw_text": ""
        }
        # 일단 형식상 저장만 해놓기
        self.repo.save_state(session_id, initial_state)

        return {
            "session_id": session_id,
            "expires_in": settings.SESSION_TTL_SECONDS,
            "message": "세션이 생성되었습니다."
        }

    # 세션 조회 + 유효성 검사 같이하는 함수
    def get_session(self, session_id: str) -> dict:
        session = self.repo.get_session(session_id)
        if not session: # 세션정보 없으면 예외 처리
            raise HTTPException(status_code=404, detail="유효하지 않거나 만료된 세션입니다.")
        return session

    # 보통 접근 시각을 갱신.
    # 세션 존재 확인 후 ttl 연장하기 위함
    def touch_session(self, session_id: str) -> dict:
        session = self.get_session(session_id)
        session["last_accessed_at"] = datetime.now(timezone.utc).isoformat() #utc 시간을 다시 넣음
        self.repo.create_session(session_id, session) # 다시 저장 / redis의 set은 없으면 생성 있으면 덮기
        self.repo.refresh_session_ttl(session_id)  # ttl 다시 리셋
        return session

    def delete_session(self, session_id: str) -> None:
        self.repo.delete_session(session_id)