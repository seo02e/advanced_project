from pydantic import BaseModel
from datetime import date

class PolicyAPI(BaseModel):
    policy_id : str                                 # 정책 고유 id
    policy_name : str                               # 정책명
    category : str                                  # 정책 대분류
    subcategory : str | None = None                 # 정책 중분류
    region_scope : str | None = None                # 적용 지역
    age_min : int | None = None                     # 최소 연령
    age_max : int | None = None                     # 최대 연령
    employment_condition : str | None = None        # 취업/재직 조건
    housing_condition : str | None = None           # 무주택/세대주 등 주거 조건
    income_condition_text : str | None = None       # 소득 조건 원문
    apply_start_date : date | None = None           # 신청 시작일
    apply_end_date : date | None = None             # 신청 종료일
    apply_status : str | None = None                # 신청 가능 유무(가능/마감/확인필요/unknown)
    source_org : str | None = None                  # 출처 기관
    source_url : str | None = None                  # 출처 링크
    summary : str | None = None                     # 요약
    source_type : str                               # 추출 경로
    source_layer : str = "A"                        # 추출 layer
    
class PolicyCrawling(BaseModel):
    chunk_id: str                                   # 청크 고유 id
    policy_id: str | None = None                    # 정책 id
    policy_name: str | None = None                  # 정책명
    issuing_org: str | None = None                  # 발급/운영 기관명
    source_doc_name: str | None = None              # 원본 문서명
    source_url: str | None = None                   # 원본 링크
    section_title: str | None = None                # 문단 제목
    chunk_text: str                                 # 청크 본문 내용
    chunk_order: int | None = None                  # 문서 내 순서
    has_table: bool = False                         # 표 포함 여부
    doc_type: str | None = None                     # 문서 유형(web_page/pdf/html 등)
    created_from: str | None = None                 # 생성 방식(section_chunking 등)
    source_layer: str = "B"                         # 추출 layer