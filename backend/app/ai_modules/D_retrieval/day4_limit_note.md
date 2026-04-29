# Youth-Sync Day4 현재 한계 문서

## 1. 현재 완성 범위

Youth-Sync Day4 기준으로 A~D 서비스 코어의 1~5단계가 연결되었다.

| 단계 | 구현 상태 | 주요 산출물 |
|---|---|---|
| 입력 | 완료 | 사용자 자연어 질문 |
| 1단계 사용자 프로필 추출 | 완료 | profile_used |
| 2단계 정책 메타데이터 필터링 | 완료 | recommended_policies |
| 3단계 문서 검색 | 완료 | BM25 + Dense hybrid retrieved_chunks |
| 4단계 자격 대조 | 완료 | eligibility_result, eligibility_status, missing_requirements |
| 5단계 LLM 응답 생성 | 완료 | answer_blocks, answer_text, llm_answer_generation |
| 6단계 프론트 표시 | 후속 연결 필요 | 결과 카드, 상세 보기, 출처 링크, 보완 정보 입력 유도 |

## 2. 현재 기준 파일

| 파일 | 역할 |
|---|---|
| C_profile/profile_parser_final.py | 사용자 자연어 질문에서 프로필 추출 |
| D_retrieval/rag_pipeline.py | A/B/C/D 연결 및 최종 응답 생성 |
| D_retrieval/retriever_final.py | BM25 + Dense hybrid 문서 검색 |
| D_retrieval/dense_retriever_final.py | sentence-transformers 기반 Dense score 계산 |
| D_retrieval/llm_answer_generator.py | OpenAI API 기반 LLM 응답 생성 |
| D_retrieval/run_day4_tests.py | 질문 5개 자동 테스트 |
| D_retrieval/day4_test_outputs.json | 질문 5개 전체 결과 |
| D_retrieval/day4_test_summary.txt | 질문 5개 요약 결과 |

## 3. 현재 검색 구조

문서 검색은 다음 구조로 작동한다.

```text
사용자 질문 + profile 정보
→ BM25 keyword score
→ Dense semantic score
→ candidate policy boost
→ important section boost
→ hybrid_score
→ 상위 chunk 반환