# 여기는 세션 데이터를 redis에 저장하고 꺼내는 전담 클래스

import json #파이썬 dict을 Json으로 바꿔서 저장하기 위해 호출
from typing import Optional, List
from app.core.redis import redis_client
from app.core.config import settings

# 세션 하나에 대해 3종류의 데이터를 관리
# _seesion_key:세션 기본 정보 | _messages_key: 채팅 메시지 목록 | _state_key: 대화 상태
class SessionRepository:
    def _session_key(self, session_id: str) -> str:
        return f"session:{session_id}"

    def _messages_key(self, session_id: str) -> str:
        return f"session:{session_id}:messages"

    def _state_key(self, session_id: str) -> str:
        return f"session:{session_id}:state"

    #세션 기본 정보를 redis에 저장하면서 ttl 설정하는 메서드
    def create_session(self, session_id: str, session_data: dict) -> None:
        redis_client.set(
            self._session_key(session_id),
            # dict를 json으로 바꿈
            json.dumps(session_data, ensure_ascii=False),
            # ttl 설정
            ex=settings.SESSION_TTL_SECONDS
        )

    # 세션 기본 정보를 redis에서 꺼내는 함수
    def get_session(self, session_id: str) -> Optional[dict]:
        # redis에서 값 조회
        data = redis_client.get(self._session_key(session_id))
        # 세션이 없거나 만료 시, None반환
        if not data:
            return None
        # 데이터가 있으면 반대로 파이썬 dict로 반환
        return json.loads(data)


    # 세션 관련 key들의 만료 시간을 연장하는 함수
    # 있는 이유 : 프로그램을 안쓰고 1800초 지나면 세션 만료인데,
    # 사용자가 프로그램을 사용하면 다시 ttl 재설정해서  1800초 주기.
    # 이런것을 흔히 슬라이딩 세션 느낌으로 운영할 수 있음.
    def refresh_session_ttl(self, session_id: str) -> None:
        redis_client.expire(self._session_key(session_id), settings.SESSION_TTL_SECONDS)
        redis_client.expire(self._messages_key(session_id), settings.SESSION_TTL_SECONDS)
        redis_client.expire(self._state_key(session_id), settings.SESSION_TTL_SECONDS)

    # 세션 삭제 메소드
    # 대화방을 완전히 끝내고 싶을 때 사용.
    def delete_session(self, session_id: str) -> None:
        redis_client.delete(self._session_key(session_id))
        redis_client.delete(self._messages_key(session_id))
        redis_client.delete(self._state_key(session_id))

    # 채팅 메시지 하나를 해당 세션의 메시지 리스트 뒤에 추가.
    def append_message(self, session_id: str, message: dict) -> None:
        redis_client.rpush( #rpush로 맨뒤에 순차 저장
            self._messages_key(session_id),
            json.dumps(message, ensure_ascii=False) # db저장시 json으로 변환
        )
        #다시 메시지 ttl 1800초
        redis_client.expire(self._session_key(session_id), settings.SESSION_TTL_SECONDS)
        redis_client.expire(self._messages_key(session_id), settings.SESSION_TTL_SECONDS)
        redis_client.expire(self._state_key(session_id), settings.SESSION_TTL_SECONDS)

    # 해당 세션의 전체 메시지 목록을 가져오는 함수
    def get_messages(self, session_id: str) -> List[dict]: #dict형식으로 여러개를 가져오니, list
        # 해당 세션의 전체 메시지 목록을 가져오는 함수
        # (self._messages_key(session_id), 0, -1) 는 리스트의 처음부터 끝까지 전부 가져오라는 뜻
        items = redis_client.lrange(self._messages_key(session_id), 0, -1)
        return [json.loads(item) for item in items]


# ai 부분
    # 세션 상태 정보를 저장하는 함수
    # parser로 추출한 정보
    def save_state(self, session_id: str, state: dict) -> None:
        redis_client.set(
            self._state_key(session_id),
            # json으로 변환해서 저장
            json.dumps(state, ensure_ascii=False),
            ex=settings.SESSION_TTL_SECONDS
        )

    # 저장된 state를 조회하는 함수
    def get_state(self, session_id: str) -> dict:
        data = redis_client.get(self._state_key(session_id))
        if not data:
            return {}
        return json.loads(data)