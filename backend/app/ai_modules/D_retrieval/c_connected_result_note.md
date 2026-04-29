# C-D-A-B 연결 결과 정리

## 1. 현재 연결 상태

- C profile parser 결과를 D에서 정상 사용한다.
- A 정책 데이터는 `A_policy_handover_v2/policy_master_final.csv`를 사용한다.
- B 주거 데이터는 `B_chunks_output_handover/housing_policy_master_from_b.csv`와 `housing_chunks_final.jsonl`을 사용한다.
- D는 사용자 질문의 관심사를 기준으로 A/B 데이터를 선택적으로 조회한다.

## 2. 연결 결과

### 취업 질문
- A 기반 온통청년 정책 후보가 정상 출력된다.
- B 주거 chunk는 조회하지 않는다.

### 주거 질문
- A 정책 후보와 B 주거 정책 후보를 함께 조회한다.
- B 기반 LH 주거 정책 chunk가 근거로 출력된다.
- 소득수준, 세대주 여부 등 부족한 조건은 `need_more_info`로 남긴다.

### 관심사 불명확 질문
- 정책을 넓게 추천하지 않는다.
- 관심 분야 선택이 필요하다는 fallback으로 처리한다.

## 3. 테스트 질문 결과

| 질문 | 결과 |
|---|---|
| 서울 사는 27세 무주택 구직자인데 월세 지원 받을 수 있을까? | B 주거 정책 후보 및 근거 출력 |
| 경기도 거주 25세 중소기업 재직자인데 취업 지원 정책이 있을까? | A 취업 정책 후보 출력 |
| 서울 거주 31세 직장인인데 청년 정책 대상이 아직 되나 | 정책 넓은 추천 차단 |
| 올해 퇴사한 28세 자취생인데 월세가 부담돼 | 주거 근거 출력, 추가 정보 요청 |
| 무주택인데 세대주는 아니야. 주거 지원이 가능해? | 세대주 여부 중복 질문 없이 추가 조건 요청 |

## 4. 현재 한계

- 화면에서는 아직 `recommended_policies` 전체가 “온통청년 기반 정책 후보”로 표시된다.
- 최종 UI에서는 `recommended_policies_a`, `recommended_policies_b`, `retrieved_chunks`를 분리 표시해야 한다.
- B output은 LH 홈페이지 기반으로 변환했지만, 완전한 eligibility 판정은 아직 아니다.
- 최종 자격 판단은 소득, 자산, 세대주 여부, 모집공고 세부 조건 확인이 필요하다.

## 5. 다음 작업

- 백/프론트 최종 표시 수정 요청
- `recommended_policies_a` / `recommended_policies_b` 분리 표시
- `next_action` 표시
- `debug` 화면 노출 금지
- 최종 시연 질문 5개 화면 캡처 정리