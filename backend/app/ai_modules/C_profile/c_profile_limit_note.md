# C Profile Parser 현재 한계

## 이번 제출 목표
사용자 자연어 질문을 Youth-Sync A/D 레이어가 사용할 수 있는 profile JSON으로 변환한다.

## 변경 파일
- profile_parser_final.py
- eligibility_rules_final.json
- sample_input_output_3.md
- c_profile_limit_note.md

## 현재 한계

| 한계 | 이유 | Day4 처리 방식 |
|---|---|---|
| 복잡한 자연어 전체 이해는 안 됨 | 현재는 LLM이 아니라 규칙 기반 parser | 모르는 값은 unknown 처리 |
| 소득 구간을 정확히 계산하지 않음 | 사용자의 실제 소득·가구원수·중위소득 기준표가 없음 | income_level=unknown 후 추가 확인 |
| 세대주/무주택/부모동거 같은 주거 세부조건은 일부만 처리 | 정책별 요구조건이 다름 | condition_flags와 unknown_fields로 D에 전달 |
| 정책별 eligible/not eligible 최종판정은 아직 하지 않음 | C 단독으로는 A policy row와 비교하지 않음 | D 연결 단계에서 A row와 비교 |
| 지역은 대표 시도 단위만 정규화 | 시군구/동 단위는 Day4 범위 밖 | region=unknown 또는 시도 단위만 사용 |

## 다음 레이어 전달 형식

D는 `parse_profile(raw_text)` 결과 중 아래 키를 우선 사용한다.

```json
{
  "age": 27,
  "region": "서울",
  "employment_status": "job_seeking",
  "housing_status": "homeless",
  "income_level": "unknown",
  "interest_tags": ["housing"],
  "unknown_fields": ["income_level", "household_head_status"],
  "result_status": "확인 필요",
  "reason_flags": ["income_missing", "household_head_unknown"],
  "need_more_info": ["소득수준", "세대주 여부"],
  "raw_text": "서울 사는 27세 무주택 구직자인데 월세 지원 받을 수 있을까?"
}