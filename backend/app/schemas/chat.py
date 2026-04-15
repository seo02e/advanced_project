from pydantic import BaseModel
from typing import Optional, List, Literal
# pydantic으로 사용자 입력 관련 스키마 작성 ( 자료형 제한 / 검증 과정)

# 실제 메세지 내용 자연어 데이터
# 입력용
class ChatRequest(BaseModel):
    message: str

# Optional[str] = None 은 문자열이 들어와도 되고, 안들어오면 none이여도 됨.
# 해당 클래스는 parser.py를 거쳐서 나오는 데이터로 넣기
class ParsedUserInput(BaseModel):
    age: Optional[str] = None
    region: Optional[str] = None
    employment_status: Optional[str] = None
    housing_status: Optional[str] = None
    income_level: Optional[str] = None
    interest_tags: List[str] = []
    unknown_fields: List[str] = []
    raw_text: str

# 하나의 채팅 창에 저장되는 데이터
# 저장용
class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    raw_text: str

# 한 세션에 저장되는 데이터
class ChatResponse(BaseModel):
    session_id: str # 채팅 세션 (대화방) 고유 식별자
    saved_message: ChatMessage # 방금 저장된 메세지
    total_messages: int # 저장된 총 메시지 개수