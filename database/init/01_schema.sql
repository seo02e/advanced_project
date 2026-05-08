create table if not exists youth_policy (
	id serial primary key,
	policy_id text not null unique,
	policy_name text not null,
	category text not null,
	subcategory text,
	region_scope text,
	age_min integer,
	age_max integer,
	employment_condition text,
	housing_condition text,
	income_condition_text text,
	apply_start_date timestamp,
	apply_end_date timestamp,
	apply_status text,
	source_org text,
	source_url text,
	summary text,
	source_type text not null,
    source_layer text not null,
	created_at timestamptz default now(),
	updated_at timestamptz
);

commit;

COMMENT ON TABLE youth_policy IS '청년 정책 저장 테이블';
comment on column youth_policy.id is '청년 정책 index id';
comment on column youth_policy.policy_id is '정책 id';
comment on column youth_policy.policy_name is '정책명';
comment on column youth_policy.category is '정책 대분류';
comment on column youth_policy.subcategory is '정책 소분류';
comment on column youth_policy.region_scope is '적용지역';
comment on column youth_policy.age_min is '최소연령';
comment on column youth_policy.age_max is '최대연령';
comment on column youth_policy.employment_condition is '고용조건';
comment on column youth_policy.housing_condition is '주거조건';
comment on column youth_policy.income_condition_text is '소득조건설명';
comment on column youth_policy.apply_start_date is '신청시작일';
comment on column youth_policy.apply_end_date is '신청종료일';
comment on column youth_policy.apply_status is '신청상태';
comment on column youth_policy.source_org is '출처기관';
comment on column youth_policy.source_url is '출처링크';
comment on column youth_policy.summary is '정책요약';
comment on column youth_policy.source_type is '출처유형';
comment on column youth_policy.source_layer is '데이터 계층(A/B/A+B)';
comment on column youth_policy.created_at is '생성일(DB기준)';
comment on column youth_policy.updated_at is '수정일(DB기준)';

commit;

CREATE TABLE IF NOT EXISTS policy_chunks (
    chunk_id text PRIMARY KEY,
    policy_id text NOT NULL REFERENCES youth_policy(policy_id),
    policy_name text,
    issuing_org text,
    source_doc_name text,
    source_url text,
    section_title text,
    chunk_text text NOT NULL,
    chunk_order integer,
    has_table boolean DEFAULT false,
    doc_type text,
    created_from text,
    source_layer text DEFAULT 'B',
    created_at timestamptz DEFAULT now(),
    updated_at timestamptz
);

commit;

COMMENT ON TABLE policy_chunks IS '정책 원문 청크 저장 테이블';
COMMENT ON COLUMN policy_chunks.chunk_id IS '청크 고유 ID';
COMMENT ON COLUMN policy_chunks.policy_id IS '참조 정책 ID';
COMMENT ON COLUMN policy_chunks.policy_name IS '정책명';
COMMENT ON COLUMN policy_chunks.issuing_org IS '발행 기관';
COMMENT ON COLUMN policy_chunks.source_doc_name IS '원본 문서명';
COMMENT ON COLUMN policy_chunks.source_url IS '원본 URL';
COMMENT ON COLUMN policy_chunks.section_title IS '문서 내 섹션 제목';
COMMENT ON COLUMN policy_chunks.chunk_text IS '청크 본문 텍스트';
COMMENT ON COLUMN policy_chunks.chunk_order IS '문서 내 청크 순서';
COMMENT ON COLUMN policy_chunks.has_table IS '표 포함 여부';
COMMENT ON COLUMN policy_chunks.doc_type IS '문서 유형(pdf/web/api 등)';
COMMENT ON COLUMN policy_chunks.created_from IS '생성 방식 또는 생성 출처';
COMMENT ON COLUMN policy_chunks.source_layer IS '데이터 계층(A/B/A+B)';
COMMENT ON COLUMN policy_chunks.created_at IS '생성일시';
COMMENT ON COLUMN policy_chunks.updated_at IS '수정일시';

commit;

CREATE TABLE IF NOT EXISTS batch_history (
    id serial PRIMARY KEY,
    batch_name text,
    batch_yn char(1),
    batch_error text,
    created_at timestamptz DEFAULT now()
);

commit;

COMMENT ON TABLE batch_history IS '배치 실행 이력 테이블';
COMMENT ON COLUMN batch_history.id IS '배치 이력 고유 ID';
COMMENT ON COLUMN batch_history.batch_name IS '배치 이름';
COMMENT ON COLUMN batch_history.batch_yn IS '배치 성공 여부(Y/N)';
COMMENT ON COLUMN batch_history.batch_error IS '배치 실패 시 오류 메시지';
COMMENT ON COLUMN batch_history.created_at IS '배치 실행 시각';

commit;