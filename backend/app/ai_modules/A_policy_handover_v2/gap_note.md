# A 현재 한계

1. 현재 policy_master_final.csv는 취업 정책 기준으로 정리되어 있습니다.
- 주거 정책은 아직 병합되지 않았습니다.

2. region_scope는 1차 정규화 규칙을 적용했습니다.
- 중앙부처/전국성 기관은 all로 처리했습니다.
- 서울/경기 외 지역은 현재 기타로 두었습니다.

3. employment_condition / housing_condition / subcategory는 키워드 기반 1차 태깅입니다.
- 일부 정책은 사람이 한 번 더 확인해야 정확합니다.

4. income_condition_text는 자유서술 기반입니다.
- 정량 필터는 아직 미구현입니다.