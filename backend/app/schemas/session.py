from pydantic import BaseModel
# pydantic으로 세션 관련 스키마 작성 ( 자료형 제한 / 검증 과정)


# 새로운 세션이 생성되었을 때 클라이언트에게 반환되는 응답 모델
class SessionCreateResponse(BaseModel):
    session_id: str #생성된 세션 고유 식별자
    expires_in: int # 세션이 만료되기까지 남은 시간
    message: str # 세션 생성 상태를 설명하는 사용자 친화적인 메시지

# 이미 생성된 세션의 상태 정보를 조회할 때 반환되는 응답 모델
class SessionInfoResponse(BaseModel):
    session_id: str
    created_at: str # 처음 생성된 시간
    last_accessed_at: str # 세션이 마지막으로 사용된 시간