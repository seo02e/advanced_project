# D_retrieval

A의 `policy_master_final.csv`를 읽어 사용자 profile 기준으로 정책 후보를 필터링하고, 추천 응답 JSON을 생성하는 D 레이어입니다.

## 현재 상태
- C parser 없이 mock profile 기준으로 동작
- A 정책 테이블 필터링 가능
- 추천 정책 / 추천 이유 / 추가 필요 정보 / caution / citations 반환 가능

## 실행
```bash
python test_query.py