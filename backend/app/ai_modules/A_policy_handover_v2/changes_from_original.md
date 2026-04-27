
# A 레이어 변경사항 정리

이 문서는 기존 A 담당자가 GitHub의 `A_policy` 폴더에 올려둔 버전과,  
이번에 추가로 정리한 `A_policy_handover_v2` 버전의 차이를 정리한 문서입니다.

---

## 1. 기존 A 담당자 버전에서 이미 되어 있던 것

기존 `A_policy` 폴더 기준으로 이미 존재하던 요소는 아래와 같습니다.

- 온통청년 API 수집 코드 존재 (`policy_data.py`)
- 1차 전처리 코드 존재 (`make_policy_table.py`)
- 원천 CSV 존재 (`policy_master_20260421.csv`)
- 1차 전처리 JSON 존재 (`policy_master_preprocessed_20260421.json`)
- 기본 필터 테스트 코드 존재 (`test_filter.py`)
- README 존재

즉 기존 A 담당자 버전은 **원천 수집 + 1차 전처리 + 기본 필터 실험**까지는 진행된 상태였습니다.

---

## 2. 기존 버전의 한계

기존 버전은 아래 한계를 가지고 있었습니다.

### 2-1. 공통 스키마 기준 미정렬
기존 버전은 아래와 같은 초기 구조 중심이었습니다.

- `institution`
- `region`
- 구버전 상태 표현
- 공통 17개 컬럼 미완성

즉 팀 공통 스키마에 맞는 **최종 전달본 형태**라고 보기 어려웠습니다.

### 2-2. 상태값 표현 불일치
기존 상태 표현은 `진행중`, `예정`, `마감`, `상시모집` 등 혼합 상태였고,  
팀 공통 기준인 아래 값으로 통일되지 않은 상태였습니다.

- `open`
- `closed`
- `always`
- `unknown`

### 2-3. 필터 전달용 최종 CSV 부재
기존 버전은 D 레이어가 바로 읽는 최종 전달용 CSV가 아니라,  
1차 가공 결과 중심 구조에 가까웠습니다.

---

## 3. 이번 handoff 버전에서 추가/변경한 것

### 3-1. 공통 스키마 기준으로 재정리
최종 CSV를 아래 17개 컬럼 기준으로 다시 정리했습니다.

- `policy_id`
- `policy_name`
- `category`
- `subcategory`
- `region_scope`
- `age_min`
- `age_max`
- `employment_condition`
- `housing_condition`
- `income_condition_text`
- `apply_start_date`
- `apply_end_date`
- `apply_status`
- `source_org`
- `source_url`
- `summary`
- `source_type`

### 3-2. 상태값 표준화
상태값을 아래 4개로 통일했습니다.

- `open`
- `closed`
- `always`
- `unknown`

### 3-3. 지역값 정규화
지역 표현을 아래 기준으로 정리했습니다.

- `서울`
- `경기`
- `all`
- `기타`

특히 중앙부처/전국성 기관은 `all`로 처리하도록 보강했습니다.

### 3-4. 최종 전달본 생성
- `policy_master_final.csv` 생성
- D 레이어가 별도 전처리 없이 바로 읽을 수 있는 최종본 확보

### 3-5. v2 변환/테스트 코드 추가
아래 파일을 새로 추가했습니다.

- `make_policy_table.py`
- `test_filter.py`

### 3-6. 검증/설명 문서 추가
아래 문서를 추가했습니다.

- `policy_metadata.json`
- `filter_test_result.md`
- `gap_note.md`
- `sample_input_output.md`
- `changes_from_original.md`

---

## 4. 이번 변경으로 좋아진 점

### 4-1. D 레이어 연결성이 좋아짐
이제 D는 `policy_master_final.csv`를 바로 읽어서  
정책 후보를 1차 압축할 수 있습니다.

### 4-2. 필터 테스트 결과를 증거로 제시 가능
샘플 질문 3개 기준 필터 결과를 문서로 남겼기 때문에,  
“이 CSV가 실제로 필터에 쓰일 수 있는가?”를 바로 확인할 수 있습니다.

### 4-3. 현재 한계가 문서화됨
무엇이 아직 안 되는지 숨기지 않고 `gap_note.md`에 명시했습니다.

### 4-4. handoff 품질이 올라감
샘플 입력/출력, 메타데이터 설명, 변경사항 문서까지 포함되어 있어서  
다른 팀원이 이어받을 때 이해 비용이 줄어듭니다.

---

## 5. 아직 남아 있는 한계

이번 handoff 버전도 아직 아래 한계는 남아 있습니다.

- 현재 데이터셋은 **취업 정책 중심**이며 주거 정책은 아직 병합되지 않음
- `source_url` 빈칸이 일부 존재함
- `employment_condition / housing_condition / subcategory`는 **키워드 기반 1차 태깅** 수준임
- 소득 조건은 자유서술 중심이라 정량 필터는 아직 미구현 상태임

---

## 6. 한 줄 요약

기존 A 담당자 버전이  
**“원천 수집 + 1차 전처리”** 단계였다면,

이번 `A_policy_handover_v2` 버전은  
**“공통 스키마 기준 최종 전달본 + 검증 문서 포함”** 단계까지 정리한 버전입니다.