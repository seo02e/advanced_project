# A_policy_handover_v2

청년 정책 원천 데이터를 **필터 가능한 표준 정책 테이블**로 정리하는 A 레이어 최종 작업 폴더입니다.

이 폴더는 단순 handover 보조 폴더가 아니라,  
현재 기준으로 **A 레이어 자체를 실행·검증·전달할 수 있는 최종 작업 폴더**를 목표로 정리했습니다.

---

## 1. A 레이어의 역할

A 레이어는 정책 설명문을 적는 역할이 아니라,  
정책 원본을 **검색 전에 빠르게 걸러낼 수 있는 표준 테이블**로 바꾸는 역할입니다.

즉 이 폴더의 결과물은 아래 질문에 답할 수 있어야 합니다.

- 서울 정책인가?
- 경기 정책인가?
- 전국 정책인가?
- 25세가 대상인가?
- 신청 가능한 상태인가?
- 취업 정책인가?
- 주거 정책인가?

---

## 2. 현재 폴더에서 하는 일

이 폴더는 아래 흐름을 담당합니다.

1. 원천 정책 데이터 확보
2. 공통 스키마 기준으로 정책 테이블 변환
3. 질문 기준 필터 테스트
4. 최종 정책 CSV 전달

즉 흐름은 아래와 같습니다.

원천 데이터  
→ 정책 메타데이터 정리  
→ 필터 가능한 최종 CSV 생성  
→ 질문 기준 테스트  
→ 다음 레이어(D) 전달

---

## 3. 포함 파일

### 실행 파일
- `policy_data.py`  
  온통청년 API 기준 원천 정책 수집 스크립트

- `make_policy_table.py`  
  원천 CSV를 공통 스키마 기준 최종 정책 테이블로 변환하는 스크립트

- `test_filter.py`  
  샘플 질문 기준 필터 테스트 스크립트

### 데이터 파일
- `policy_master_20260421.csv`  
  원천 정책 CSV

- `policy_master_final.csv`  
  최종 정책 메타데이터 테이블  
  D 레이어가 바로 읽는 전달본

### 문서 파일
- `policy_metadata.json`  
  컬럼 정의 및 값 의미 설명

- `filter_test_result.md`  
  샘플 질문 3개 기준 필터 결과

- `gap_note.md`  
  현재 한계 및 후속 과제 정리

- `sample_input_output.md`  
  샘플 입력 1개 / 샘플 출력 1개 예시

### 환경/설치 파일
- `.env.sample`  
  API 키 설정 예시

- `requirements.txt`  
  최소 실행 패키지 목록

---

## 4. 최종 policy schema

최종 CSV는 아래 17개 컬럼으로 고정합니다.

1. `policy_id`
2. `policy_name`
3. `category`
4. `subcategory`
5. `region_scope`
6. `age_min`
7. `age_max`
8. `employment_condition`
9. `housing_condition`
10. `income_condition_text`
11. `apply_start_date`
12. `apply_end_date`
13. `apply_status`
14. `source_org`
15. `source_url`
16. `summary`
17. `source_type`

---

## 5. 값 표준화 기준

### category
- `취업`
- `주거`
- `unknown`

### region_scope
- `서울`
- `경기`
- `all`
- `기타`

### apply_status
- `open`
- `closed`
- `always`
- `unknown`

### employment_condition
- `employed`
- `job_seeking`
- `all`
- `unknown`

### housing_condition
- `homeless`
- `living_with_parents`
- `renting`
- `household_head`
- `all`
- `unknown`

---

## 6. 실행 순서

### 경우 1. 이미 원천 CSV가 있을 때
현재 폴더처럼 `policy_master_20260421.csv`가 이미 있으면 아래 순서로 진행합니다.

1. `make_policy_table.py` 실행
2. `policy_master_final.csv` 생성 확인
3. `test_filter.py` 실행
4. `filter_test_result.md`와 결과 비교

예시:

```bash
python make_policy_table.py
python test_filter.py
```

### 경우 2. 원천 수집부터 다시 할 때
원천 수집부터 다시 해야 하면 아래 순서로 진행합니다.

1. `policy_data.py`
2. `make_policy_table.py`
3. `test_filter.py`

예시:

```bash
python policy_data.py
python make_policy_table.py
python test_filter.py
```

---

## 7. 설치

```bash
pip install -r requirements.txt
```

---

## 8. 최종 전달본

다음 레이어(D)에 전달하는 핵심 파일은 아래입니다.

- `policy_master_final.csv`

형식:
- UTF-8 CSV

D 레이어가 우선적으로 사용하는 핵심 컬럼:
- `policy_id`
- `policy_name`
- `category`
- `subcategory`
- `region_scope`
- `age_min`
- `age_max`
- `apply_status`
- `source_url`
- `summary`

---

## 9. 현재 상태

현재 버전은 **취업 정책 중심 버전**입니다.

정리 완료된 항목:
- 공통 스키마 기준 최종 CSV 생성
- 상태값 정규화
- 지역값 정규화
- 질문 3개 기준 필터 테스트
- 메타데이터 설명 문서 작성
- 현재 한계 문서 작성

---

## 10. 현재 한계

- 현재 데이터셋은 **취업 정책 중심**이며 주거 정책은 아직 병합되지 않았습니다.
- `source_url` 빈칸이 일부 존재합니다.
- `employment_condition / housing_condition / subcategory`는 **키워드 기반 1차 태깅** 수준입니다.
- `income_condition_text`는 자유서술 중심이며 정량 필터는 아직 미구현 상태입니다.

---

## 11. 이 폴더를 볼 때의 기준

이 폴더는 “정책을 다 이해시키는 폴더”가 아니라,  
정책 원본을 **다음 레이어가 바로 쓸 수 있는 표준 테이블로 바꿔 두는 폴더**입니다.

즉 가장 중요한 기준은 아래입니다.

- 컬럼명이 고정되어 있는가
- 상태값이 표준화되어 있는가
- 질문 기준 필터가 되는가
- D 레이어가 바로 읽을 수 있는가

---

## 12. 한 줄 요약

이 폴더는 청년 정책 원천 데이터를  
**공통 스키마 기준 최종 정책 테이블로 정리하고, 질문 기준 필터 테스트까지 포함한 A 레이어 최종 작업 폴더**입니다.
