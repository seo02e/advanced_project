# B housing handover v1 현재 한계

## 현재 상태
- 독립형 주거 chunk handover 생성 완료
- 최종 파일: `B_housing_handover_v1/housing_chunks_final.jsonl`
- 기존 B 담당자 원본 폴더는 수정하지 않음

## 현재 한계

| 한계 | 이유 | 처리 |
|---|---|---|
| 실제 공고문 기반 최종 chunk가 아님 | Day4 통합 테스트용 최소 데이터 | `handover_stub`로 명시 |
| source_url 없음 | 원문 공고 확정 전 | citations에는 포함하지 않음 |
| A policy_id와 연결되지 않음 | 독립 handover 목적 | D의 `retrieved_chunks` 근거로만 사용 |
| 최종 자격 판정 불가 | 소득, 자산, 세대주, 공고별 조건 필요 | `확인 필요` 유지 |

## 다음 단계
- 실제 B 원본 또는 주거 공고문이 정리되면 `B_housing_handover_v2` 생성
- 그때 source_url, policy_id, section_title을 실제 공고 기준으로 보강