backend/
│
├── app/
│ ├── main.py # FastAPI 애플리케이션 진입점
│ ├── api/ # 라우터 정의 / #요청 받고 서비스 호출
│ │ ├── session.py
│ │ └── chat.py
│ │
│ ├── services/ # 백엔드 흐름 제어 / #세션의 동작 규칙 처리
│ │ ├── chat_service.py
│ │ ├── session_service.py
│ │ ├── policy_service.py
│ │ └── response_service.py
│ │
│ ├── ai_modules/ # A/B/C/D 산출물 연결 (AI 팀)
│ │ ├── parser_module.py 1번
│ │ ├── eligibility_module.py 4번
│ │ ├── retriever_module.py 5번
│ │ └── rag_module.py 3-2번
│ │
│ ├── data/ # A/B 산출물 저장 (AI 팀)
│ │ ├── policy_master_final.csv 2번
│ │ ├── policy_metadata.json 2번
│ │ └── housing_chunks_final.json 3-1번
│ │
│ ├── repositories/ # 세션/저장소 접근
│ │ └── session_repository.py #redis랑 직접 대화
│ │
│ ├── schemas/ # request / response 모델
│ │ ├── chat.py
│ │ └── session.py
│ │
│ ├── core/ # 공통 설정
│ │ ├── config.py
│ │ └── redis.py
│ │
│ └── utils/
│ └── logger.py
│
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
