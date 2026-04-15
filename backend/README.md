## 📁 Project Structure

```plaintext
backend/
│
├── app/
│   ├── main.py                     # FastAPI 애플리케이션 진입점
│   │
│   ├── api/                        # 라우터 정의 (요청을 받고 서비스 호출)
│   │   ├── session.py
│   │   └── chat.py
│   │
│   ├── services/                   # 백엔드 비즈니스 로직 및 흐름 제어
│   │   ├── chat_service.py
│   │   ├── session_service.py
│   │   ├── policy_service.py
│   │   └── response_service.py
│   │
│   ├── ai_modules/                 # AI 팀 산출물 연동 모듈
│   │   ├── parser_module.py        # (1) 사용자 입력 파싱
│   │   ├── eligibility_module.py   # (4) 자격 요건 판단
│   │   ├── retriever_module.py     # (5) 정책 검색
│   │   └── rag_module.py           # (3-2) RAG 기반 응답 생성
│   │
│   ├── data/                       # AI 팀 산출물 데이터
│   │   ├── policy_master_final.csv
│   │   ├── policy_metadata.json
│   │   └── housing_chunks_final.json
│   │
│   ├── repositories/               # 데이터 저장소 접근 계층
│   │   └── session_repository.py   # Redis와 직접 통신
│   │
│   ├── schemas/                    # Request / Response Pydantic 모델
│   │   ├── chat.py
│   │   └── session.py
│   │
│   ├── core/                       # 공통 설정 및 인프라 구성
│   │   ├── config.py               # 환경 변수 및 애플리케이션 설정
│   │   └── redis.py                # Redis 연결 설정
│   │
│   └── utils/
│       └── logger.py               # 로깅 설정
│
├── Dockerfile                      # Docker 이미지 빌드 설정
├── docker-compose.yml              # 서비스 오케스트레이션
└── requirements.txt                # Python 의존성 목록
```
