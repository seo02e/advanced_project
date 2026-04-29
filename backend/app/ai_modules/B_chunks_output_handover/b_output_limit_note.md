# B output handover limit note

## 현재 한계
1. B 원본 chunk에는 LH 홈페이지 메뉴/공통 문구가 일부 섞여 있습니다.
2. 본 변환 스크립트는 정책명/주거 관련 키워드 기준으로 chunk_text를 잘라 검색 품질을 보정합니다.
3. section_title이 `기타`로 들어간 chunk가 많아 문단 제목 품질은 추가 개선 여지가 있습니다.
4. apply_status는 B policy 원본 값을 따르며, 모르는 값은 `unknown`으로 둡니다.
5. 이 파일은 B 원본 산출물이 아니라 D 연결용 변환본입니다.

## 다음 작업
- D에서 A policy master + B housing policy master를 함께 읽도록 수정
- D에서 B housing_chunks_final.jsonl을 검색 대상으로 사용
- 질문 5개로 주거/취업 결과 재검수
