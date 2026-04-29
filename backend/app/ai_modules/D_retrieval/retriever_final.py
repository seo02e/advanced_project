# retriever_final.py
# Youth-Sync D Layer - Day4 Hybrid Retriever
# 목적:
# 1) BM25 baseline 검색
# 2) Dense retrieval 점수 추가
# 3) BM25 + Dense + 정책 후보 boost를 결합한 hybrid_score 생성
# 4) Dense 실패 시 BM25만으로 fallback

from __future__ import annotations

import math
import re
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple


try:
    from dense_retriever_final import retrieve_dense_scores
except Exception:
    retrieve_dense_scores = None


IMPORTANT_SECTION_TITLES = [
    "입주대상",
    "입주자격",
    "신청자격",
    "지원대상",
    "소득 자산 기준",
    "소득·자산 기준",
    "임대조건",
    "신청방법",
    "공급대상",
]

NOISE_KEYWORDS = [
    "통합검색",
    "새소식",
    "공지사항",
    "정보공개",
    "고객의소리",
    "부패ㆍ부조리신고",
    "공공데이터",
    "사업실명제",
    "뉴스룸",
    "ESG경영",
    "공사소개",
    "콘텐츠 만족도 조사",
    "퀵메뉴",
    "개인정보처리방침",
    "이메일무단수집거부",
    "COPYRIGHT",
]

EMPLOYMENT_STATUS_TO_QUERY = {
    "job_seeking": "구직 취업준비 미취업 취업지원 일자리",
    "employed": "재직 근로 직장인 중소기업 청년",
    "student": "대학생 학생 재학생 청년",
    "unemployed": "퇴사 실직 무직 미취업 구직",
}

HOUSING_STATUS_TO_QUERY = {
    "homeless": "무주택 주거 월세 전세 임대 청년주택",
    "renting": "자취 월세 전세 임차 주거지원",
    "living_with_parents": "부모님 본가 가구 세대 주거지원",
    "homeowner": "자가 주택소유",
}

INTEREST_TO_QUERY = {
    "housing": "주거 월세 전세 임대 무주택 청년주택 신청자격 지원대상 소득 기준 세대주",
    "employment": "취업 구직 일자리 면접 교육 훈련 청년수당 취업지원",
}


def clean_value(value: Any) -> str:
    if value is None:
        return ""

    text = str(value).strip()

    if text.lower() in ["nan", "none", "null"]:
        return ""

    return text


def normalize_text(text: Any) -> str:
    value = clean_value(text).lower()
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def tokenize(text: Any) -> List[str]:
    normalized = normalize_text(text)
    words = re.findall(r"[가-힣a-zA-Z0-9]+", normalized)

    tokens: List[str] = []

    for word in words:
        if not word:
            continue

        tokens.append(word)

        if len(word) >= 2:
            tokens.extend(word[i:i + 2] for i in range(len(word) - 1))

        if len(word) >= 3:
            tokens.extend(word[i:i + 3] for i in range(len(word) - 2))

    return tokens


def is_noisy_chunk(chunk: Dict[str, Any]) -> bool:
    section_title = clean_value(chunk.get("section_title", ""))
    chunk_text = clean_value(chunk.get("chunk_text", ""))

    noise_count = sum(1 for keyword in NOISE_KEYWORDS if keyword in chunk_text)

    if section_title == "기타" and noise_count >= 2:
        return True

    if noise_count >= 4:
        return True

    return False


def get_display_policy_name(policy_name: Any) -> str:
    text = clean_value(policy_name)

    if "|" in text:
        return text.split("|")[0].strip()

    return text


def build_chunk_document_text(chunk: Dict[str, Any]) -> str:
    policy_name = clean_value(chunk.get("policy_name", ""))
    source_doc_name = clean_value(chunk.get("source_doc_name", ""))
    section_title = clean_value(chunk.get("section_title", ""))
    chunk_text = clean_value(chunk.get("chunk_text", ""))

    section_boost_text = section_title if section_title in IMPORTANT_SECTION_TITLES else ""

    return " ".join(
        [
            policy_name,
            source_doc_name,
            section_title,
            section_boost_text,
            chunk_text,
        ]
    )


def build_query_from_profile(profile: Dict[str, Any]) -> str:
    raw_text = clean_value(profile.get("raw_text", ""))
    query_parts: List[str] = [raw_text]

    age = profile.get("age")
    region = clean_value(profile.get("region", "unknown"))
    employment_status = clean_value(profile.get("employment_status", "unknown"))
    housing_status = clean_value(profile.get("housing_status", "unknown"))
    income_level = clean_value(profile.get("income_level", "unknown"))
    interest_tags = profile.get("interest_tags", [])
    need_more_info = profile.get("need_more_info", [])

    if age is not None:
        query_parts.append(f"{age}세 청년")

    if region and region != "unknown":
        query_parts.append(region)

    if employment_status in EMPLOYMENT_STATUS_TO_QUERY:
        query_parts.append(EMPLOYMENT_STATUS_TO_QUERY[employment_status])

    if housing_status in HOUSING_STATUS_TO_QUERY:
        query_parts.append(HOUSING_STATUS_TO_QUERY[housing_status])

    if income_level != "unknown":
        query_parts.append(f"{income_level} 소득 소득기준")

    for tag in interest_tags:
        if tag in INTEREST_TO_QUERY:
            query_parts.append(INTEREST_TO_QUERY[tag])

    for item in need_more_info:
        query_parts.append(clean_value(item))

    return " ".join(part for part in query_parts if part)


class BM25Index:
    def __init__(self, documents: List[str], k1: float = 1.5, b: float = 0.75):
        self.documents = documents
        self.k1 = k1
        self.b = b

        self.tokenized_docs = [tokenize(doc) for doc in documents]
        self.doc_lengths = [len(tokens) for tokens in self.tokenized_docs]
        self.avg_doc_length = (
            sum(self.doc_lengths) / len(self.doc_lengths)
            if self.doc_lengths
            else 0.0
        )

        self.term_freqs = [Counter(tokens) for tokens in self.tokenized_docs]
        self.idf = self._build_idf()

    def _build_idf(self) -> Dict[str, float]:
        doc_count = len(self.tokenized_docs)
        doc_freq: Counter[str] = Counter()

        for tokens in self.tokenized_docs:
            for token in set(tokens):
                doc_freq[token] += 1

        idf: Dict[str, float] = {}

        for token, freq in doc_freq.items():
            idf[token] = math.log(1 + (doc_count - freq + 0.5) / (freq + 0.5))

        return idf

    def score(self, query: str, doc_index: int) -> float:
        query_tokens = tokenize(query)

        if not query_tokens:
            return 0.0

        score = 0.0
        term_freq = self.term_freqs[doc_index]
        doc_length = self.doc_lengths[doc_index]

        if doc_length == 0 or self.avg_doc_length == 0:
            return 0.0

        for token in query_tokens:
            if token not in term_freq:
                continue

            tf = term_freq[token]
            idf = self.idf.get(token, 0.0)

            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * doc_length / self.avg_doc_length)

            score += idf * numerator / denominator

        return score

    def scores(self, query: str) -> List[float]:
        return [self.score(query, idx) for idx in range(len(self.documents))]


def normalize_bm25_scores(scores: List[float]) -> List[float]:
    if not scores:
        return []

    max_score = max(scores)

    if max_score <= 0:
        return [0.0 for _ in scores]

    return [round(score / max_score, 4) for score in scores]


def build_match_basis(
    chunk: Dict[str, Any],
    candidate_policy_ids: set[str],
    bm25_score: float,
    dense_score: Optional[float],
    section_boost: float,
    candidate_boost: float,
) -> List[str]:
    basis: List[str] = []

    if bm25_score > 0:
        basis.append("BM25 query-text match")

    if dense_score is not None:
        basis.append("Dense semantic match")

    if clean_value(chunk.get("policy_id", "")) in candidate_policy_ids:
        basis.append("policy candidate id boost")

    if section_boost > 0:
        basis.append("important eligibility section boost")

    if "청년" in clean_value(chunk.get("chunk_text", "")):
        basis.append("youth keyword present")

    return basis


def retrieve_relevant_chunks_bm25(
    profile: Dict[str, Any],
    chunks: List[Dict[str, Any]],
    limit: int = 5,
    candidate_policy_ids: Optional[List[str]] = None,
) -> List[Dict[str, Any]]:
    """
    기존 rag_pipeline.py 호환을 위해 함수명은 유지한다.
    내부는 BM25 + Dense hybrid 검색이다.
    """
    usable_chunks = [chunk for chunk in chunks if not is_noisy_chunk(chunk)]

    if not usable_chunks:
        return []

    candidate_ids = {
        clean_value(policy_id)
        for policy_id in (candidate_policy_ids or [])
        if clean_value(policy_id)
    }

    candidate_chunks = [
        chunk for chunk in usable_chunks
        if clean_value(chunk.get("policy_id", "")) in candidate_ids
    ]

    search_chunks = candidate_chunks if candidate_chunks else usable_chunks

    documents = [build_chunk_document_text(chunk) for chunk in search_chunks]
    query = build_query_from_profile(profile)

    bm25 = BM25Index(documents)
    bm25_raw_scores = bm25.scores(query)
    bm25_norm_scores = normalize_bm25_scores(bm25_raw_scores)

    dense_scores: Dict[str, float] = {}
    dense_status = "not_implemented_day4"
    dense_model_name = ""

    if retrieve_dense_scores is not None:
        dense_scores, dense_status, dense_model_name = retrieve_dense_scores(
            query=query,
            chunks=search_chunks,
        )
    else:
        dense_status = "dense_unavailable_import_error"

    dense_available = bool(dense_scores)

    scored: List[Tuple[float, Dict[str, Any]]] = []

    for idx, chunk in enumerate(search_chunks):
        policy_id = clean_value(chunk.get("policy_id", ""))
        chunk_id = clean_value(chunk.get("chunk_id", ""))
        section_title = clean_value(chunk.get("section_title", ""))
        chunk_text = clean_value(chunk.get("chunk_text", ""))

        bm25_raw_score = bm25_raw_scores[idx]
        bm25_norm_score = bm25_norm_scores[idx]

        dense_score = dense_scores.get(chunk_id) if dense_available else None

        candidate_boost = 0.15 if policy_id in candidate_ids else 0.0
        section_boost = 0.15 if section_title in IMPORTANT_SECTION_TITLES else 0.0
        youth_boost = 0.03 if "청년" in chunk_text else 0.0

        if dense_score is not None:
            hybrid_score = (
                0.55 * bm25_norm_score
                + 0.45 * dense_score
                + candidate_boost
                + section_boost
                + youth_boost
            )
            retrieval_method = "hybrid_bm25_dense"
        else:
            hybrid_score = (
                bm25_norm_score
                + candidate_boost
                + section_boost
                + youth_boost
            )
            retrieval_method = "bm25_baseline"

        if hybrid_score <= 0:
            continue

        cleaned_chunk = dict(chunk)
        cleaned_chunk["policy_name"] = get_display_policy_name(cleaned_chunk.get("policy_name", ""))
        cleaned_chunk["source_doc_name"] = get_display_policy_name(cleaned_chunk.get("source_doc_name", ""))

        cleaned_chunk["retrieval_method"] = retrieval_method
        cleaned_chunk["bm25_score"] = round(bm25_raw_score, 4)
        cleaned_chunk["bm25_norm_score"] = round(bm25_norm_score, 4)
        cleaned_chunk["dense_score"] = round(dense_score, 4) if dense_score is not None else None
        cleaned_chunk["hybrid_score"] = round(hybrid_score, 4)
        cleaned_chunk["dense_status"] = dense_status
        cleaned_chunk["dense_model_name"] = dense_model_name
        cleaned_chunk["retrieval_query"] = query
        cleaned_chunk["match_basis"] = build_match_basis(
            chunk=chunk,
            candidate_policy_ids=candidate_ids,
            bm25_score=bm25_raw_score,
            dense_score=dense_score,
            section_boost=section_boost,
            candidate_boost=candidate_boost,
        )

        scored.append((hybrid_score, cleaned_chunk))

    scored.sort(key=lambda item: item[0], reverse=True)

    return [chunk for _, chunk in scored[:limit]]