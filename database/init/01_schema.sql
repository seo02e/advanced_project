create table if not exists youth_policy (
	id serial primary key,
	policy_id text not null unique,
	policy_name text not null,
	category text not null,
	subcategory text,
	region_scope text not null,
	age_min integer,
	age_max integer,
	employment_condition text,
	housing_condition text,
	income_condition_text text,
	apply_start_date timestamp,
	apply_end_date timestamp,
	apply_status text not null,
	source_org text,
	source_url text,
	summary text,
	source_type text not null,
	created_at timestamptz default now(),
	updated_at timestamptz
);

commit;

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
comment on column youth_policy.created_at is '생성일(DB기준)';
comment on column youth_policy.updated_at is '수정일(DB기준)';

commit;

SELECT * FROM 
