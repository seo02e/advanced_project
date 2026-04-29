## docker를 통한 PostgreSQL 서버 실행 방법

1. cmd 창 열기
2. 현재 프로젝트 경로로 이동
3. env.sample 파일 복사 후, 복사된 파일 .env로 변경(**env.sample 원본은 추후 환경설정을 위해 유지 필요!!**)
4. docker-compose up -d 명령어 입력
5. docker ps 명령어 실행 후 adv_3team_db 이름의 container 가 Up 상태인지 확인
   ![alt text](docker_image1.png)
6. 정상적으로 Up 확인 이후, DB툴 통해서 접속
7. 접속의 필요한 정보는 복사된 .env 파일 참조

## 📌 프로젝트 개요

청년 정책 추천 챗봇 (RAG + LLM 기반)

## 🧠 핵심 기능

- 자연어 → 프로필 파싱
- 정책 DB 기반 필터링
- BM25 기반 문서 검색
- LLM 기반 응답 생성
- 세션 기반 채팅

## 🏗️ 아키텍처

Frontend (React)
→ Backend (FastAPI)
→ Redis (Session)
→ RAG Pipeline (Policy + Chunk 검색)
→ OpenAI (LLM 응답)

## ⚙️ 실행 방법

### Backend

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

### Frontend

npm run dev

## 🔐 환경 변수 (.env)

OPENAI_API_KEY=\*\*\*
ENABLE_LLM_API=2
OPENAI_MODEL=gpt-5.4-mini
