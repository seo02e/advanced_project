# A 샘플 입력 / 샘플 출력

이 문서는 A 레이어가 **원천 정책 1건을 공통 스키마 기준 최종 row 1건으로 어떻게 바꾸는지** 보여주기 위한 예시입니다.

---

## 1. 샘플 입력

- 입력 유형: 온통청년 API 원천 정책 1건
- 원천 식별값:
  - `policy_id(plcyNo)`: `20260417005400112767`
  - `policy_name(plcyNm)`: `참 괜찮은 강소기업 선정 및 취업연계`
  - `source_org(원천 기준)`: `중소벤처기업부`

### 입력 설명
이 단계의 입력은 정책 원본입니다.  
즉 아직 필터 가능한 표준 테이블이 아니라,  
온통청년 API에서 가져온 원천 정책 row 1건입니다.

---

## 2. 샘플 출력

아래는 위 원천 정책 1건을 공통 policy schema 기준으로 정제한 결과 row 예시입니다.

```json
{
  "policy_id": "20260417005400112767",
  "policy_name": "참 괜찮은 강소기업 선정 및 취업연계",
  "category": "취업",
  "subcategory": "취업지원",
  "region_scope": "all",
  "age_min": 0,
  "age_max": 0,
  "employment_condition": "job_seeking",
  "housing_condition": "unknown",
  "income_condition_text": null,
  "apply_start_date": null,
  "apply_end_date": null,
  "apply_status": "always",
  "source_org": "중소벤처기업부",
  "source_url": "https://www.smes.go.kr/gsmb/main",
  "summary": "구직자들이 선호할만한 우수 중소기업을 발굴하고 채용 정보 제공 및 매칭 지원을 통해 중소기업 일자리 미스매치 완화",
  "source_type": "api"
}