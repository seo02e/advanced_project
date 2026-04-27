# C Profile Parser 샘플 입력/출력 3개

## 이번 제출 목표
사용자 자연어 질문을 D/A 레이어가 사용할 수 있는 profile JSON으로 변환한다.

---

## 샘플 1

### 입력

```json
{
  "raw_text": "서울 사는 27세 무주택 구직자인데 월세 지원 받을 수 있을까?"
}
```

### 예상 출력

```json
{
  "schema_version": "c_profile_v1",
  "raw_text": "서울 사는 27세 무주택 구직자인데 월세 지원 받을 수 있을까?",
  "age": 27,
  "region": "서울",
  "employment_status": "job_seeking",
  "housing_status": "homeless",
  "income_level": "unknown",
  "interest_tags": ["housing", "employment"],
  "unknown_fields": ["income_level", "household_head_status"],
  "condition_flags": {
    "household_head_status": "unknown"
  },
  "result_status": "확인 필요",
  "reason_flags": ["income_missing", "household_head_unknown"],
  "need_more_info": ["소득수준", "세대주 여부"]
}
```

### 해석
나이, 지역, 취업상태, 주거 관심사는 추출된다. 다만 소득수준과 세대주 여부는 질문에 없으므로 확인 필요다.

---

## 샘플 2

### 입력

```json
{
  "raw_text": "경기도 사는 25살 취준생인데 취업지원 정책 알려줘. 소득은 잘 모르겠어."
}
```

### 예상 출력

```json
{
  "schema_version": "c_profile_v1",
  "raw_text": "경기도 사는 25살 취준생인데 취업지원 정책 알려줘. 소득은 잘 모르겠어.",
  "age": 25,
  "region": "경기",
  "employment_status": "job_seeking",
  "housing_status": "unknown",
  "income_level": "unknown",
  "interest_tags": ["employment"],
  "unknown_fields": ["income_level"],
  "condition_flags": {
    "household_head_status": "unknown"
  },
  "result_status": "확인 필요",
  "reason_flags": ["income_missing"],
  "need_more_info": ["소득수준"]
}
```

### 해석
취업 관심 질문이므로 주거상태는 필수 unknown으로 올리지 않는다. 소득은 명시되지 않았으므로 확인 필요다.

---

## 샘플 3

### 입력

```json
{
  "raw_text": "부모님이랑 살고 있고 29세야. 서울 청년 주거 정책 받을 수 있어?"
}
```

### 예상 출력

```json
{
  "schema_version": "c_profile_v1",
  "raw_text": "부모님이랑 살고 있고 29세야. 서울 청년 주거 정책 받을 수 있어?",
  "age": 29,
  "region": "서울",
  "employment_status": "unknown",
  "housing_status": "living_with_parents",
  "income_level": "unknown",
  "interest_tags": ["housing"],
  "unknown_fields": ["employment_status", "income_level", "household_head_status"],
  "condition_flags": {
    "household_head_status": "unknown"
  },
  "result_status": "확인 필요",
  "reason_flags": ["employment_status_missing", "income_missing", "household_head_unknown"],
  "need_more_info": ["취업상태", "소득수준", "세대주 여부"]
}
```

### 해석
주거 관심은 추출되지만, 취업상태·소득·세대주 여부가 없어 확인 필요다.

---

## 다음 레이어 전달 형식

D에 넘길 기본 입력은 아래 profile JSON이다.

```json
{
  "age": 27,
  "region": "서울",
  "employment_status": "job_seeking",
  "housing_status": "homeless",
  "income_level": "unknown",
  "interest_tags": ["housing", "employment"],
  "unknown_fields": ["income_level", "household_head_status"],
  "result_status": "확인 필요",
  "reason_flags": ["income_missing", "household_head_unknown"],
  "need_more_info": ["소득수준", "세대주 여부"],
  "raw_text": "서울 사는 27세 무주택 구직자인데 월세 지원 받을 수 있을까?"
}
```