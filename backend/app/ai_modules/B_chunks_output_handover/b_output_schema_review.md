# B output schema review

## 확인 결과
- B 원본 output의 `*_policy.json`은 5-1 정책 스키마 key를 대부분 충족합니다.
- B 원본 output의 `*_chunks.json`은 `{"chunks": [...]}` 구조입니다.
- D 연결을 위해 여러 파일을 하나의 CSV/JSONL로 병합했습니다.

## 생성 파일
- `housing_policy_master_from_b.csv`
- `housing_chunks_final.jsonl`

## 생성 개수
- 정책 row: 8
- chunk row: 39

## 원칙
- B 원본 output은 덮어쓰지 않습니다.
- 이 폴더는 D 연결용 변환본입니다.
- 정책과 chunk는 `policy_id`로 연결합니다.
