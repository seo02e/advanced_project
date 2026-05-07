from pydantic import BaseModel
from datetime import date

class PolicyAPI(BaseModel):
    policy_id : str                                 # 정책 고유 id
    policy_name : str                               # 정책명
    category : str                                  # 정책 대분류
    subcategory : str | None = None                 # 정책 중분류
    region_scope : str                              # 적용 지역
    age_min : int | None = None                     # 최소 연령
    age_max : int | None = None                     # 최대 연령
    employment_condition : str | None = None        # 취업/재직 조건
    housing_condition : str | None = None           # 무주택/세대주 등 주거 조건
    income_condition_text : str | None = None       # 소득 조건 원문
    apply_start_date : date | None = None           # 신청 시작일
    apply_end_date : date | None = None             # 신청 종료일
    apply_status : str                              # 신청 가능 유무(가능/마감/확인필요/unknown)
    source_org : str | None = None                  # 출처 기관
    source_url : str | None = None                  # 출처 링크
    summary : str | None = None                     # 요약
    source_type : str                               # 추출 경로
    source_layer : str | None = None                # 추출 layer
    
# class PolicyCrawling(BaseModel):