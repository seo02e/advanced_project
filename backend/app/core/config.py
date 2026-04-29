# BaseSettings는 환경벼수를 기반으로 설정 값을 관리할 수 있게 해주는 클래스.
# .env 파일이나 시스템 환경 변수에 정의된 값을 자도응로 읽어와서 애플리케이션 설정에 반영


from pydantic_settings import BaseSettings

# .env 파일에 REDIS_HOST가 정의되어 있으면 그 값 우선
# 없으면 기본값 localhost 사용

class Settings(BaseSettings):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379 #redis 서버의 포트 번호
    REDIS_DB: int = 0 # 하나의 서버에서 여러 개 논리적 db사용 가능한데 기본값이 0이라는 뜻
    SESSION_TTL_SECONDS: int = 1800 #세션 만료 시간을 의미. (초 단위) : setex() 또는  expire()로 TTL 설정시 사용


    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-5.4-mini"
    ENABLE_LLM_API: int = 0
    ENABLE_PROFILE_LLM_API: int = 0
    YOUTH_API_KEY: str = ""
    
    class Config:
        env_file = ".env" # .env파일을 읽어서 환경 변수를 로드하도록 지정하는 설정
        extra = "ignore"


settings = Settings() # 다른 파일에서 호출 할 수 있도록 인스턴스 생성