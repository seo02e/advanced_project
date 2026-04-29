# dense_retriever_final.py
# Youth-Sync D Layer - Dense Retriever
# 목적:
# 1) 한국어 특화 Dense retrieval 우선 시도
# 2) 실패 시 다국어 MiniLM fallback
# 3) 그래도 실패하면 BM25 파이프라인이 깨지지 않도록 dense_status만 반환
#
# 기본 우선순위:
# - 1순위: nlpai-lab/KURE-v1
# - 2순위: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2

from __future__ import annotations

import os
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple


KOREAN_DENSE_MODEL_NAME = "nlpai-lab/KURE-v1"
FALLBACK_DENSE_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# 환경변수로 모델명을 바꿀 수 있게 둔다.
# CMD 예시:
# set DENSE_MODEL_NAME=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
# set DENSE_MODEL_NAME=nlpai-lab/KURE-v1
ENV_DENSE_MODEL_NAME = "DENSE_MODEL_NAME"


def clean_value(value: Any) -> str:
    if value is None:
        return ""

    text = str(value).strip()

    if text.lower() in ["nan", "none", "null"]:
        return ""

    return text


def build_chunk_document_text(chunk: Dict[str, Any]) -> str:
    policy_name = clean_value(chunk.get("policy_name", ""))
    source_doc_name = clean_value(chunk.get("source_doc_name", ""))
    section_title = clean_value(chunk.get("section_title", ""))
    chunk_text = clean_value(chunk.get("chunk_text", ""))

    return " ".join(
        [
            policy_name,
            source_doc_name,
            section_title,
            chunk_text,
        ]
    ).strip()


def get_dense_model_candidates() -> List[str]:
    """
    Dense 모델 후보 우선순위.
    환경변수 DENSE_MODEL_NAME이 있으면 그 모델을 최우선으로 시도한다.
    """
    candidates: List[str] = []

    env_model = clean_value(os.getenv(ENV_DENSE_MODEL_NAME, ""))

    if env_model:
        candidates.append(env_model)

    candidates.extend(
        [
            KOREAN_DENSE_MODEL_NAME,
            FALLBACK_DENSE_MODEL_NAME,
        ]
    )

    # 중복 제거
    return list(dict.fromkeys(candidates))


@lru_cache(maxsize=2)
def load_sentence_transformer(model_name: str):
    """
    모델 로딩은 무겁기 때문에 캐시한다.
    같은 실행 안에서는 한 번만 로딩된다.
    """
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(model_name)


def try_load_dense_model() -> Tuple[Optional[Any], str, str]:
    """
    반환:
    - model
    - dense_status
    - model_name
    """
    try:
        import sentence_transformers  # noqa: F401
    except Exception as e:
        return None, f"dense_unavailable_import_error: {type(e).__name__}", ""

    last_error = ""

    for model_name in get_dense_model_candidates():
        try:
            model = load_sentence_transformer(model_name)
            return model, "implemented_sentence_transformer", model_name
        except Exception as e:
            last_error = f"{model_name} failed: {type(e).__name__}"

    return None, f"dense_unavailable_model_load_error: {last_error}", ""


def normalize_dense_score(raw_score: float) -> float:
    """
    cosine similarity는 대략 -1~1 범위가 나올 수 있다.
    hybrid 결합을 쉽게 하기 위해 0~1 범위로 보정한다.
    """
    normalized = (raw_score + 1.0) / 2.0

    if normalized < 0:
        return 0.0

    if normalized > 1:
        return 1.0

    return normalized


def retrieve_dense_scores(
    query: str,
    chunks: List[Dict[str, Any]],
) -> Tuple[Dict[str, float], str, str]:
    """
    chunk_id별 dense_score를 반환한다.

    반환:
    - dense_scores: {"chunk_id": score}
    - dense_status: implemented_sentence_transformer / 오류 상태
    - dense_model_name: 실제 사용된 모델명
    """
    if not chunks:
        return {}, "not_applicable_no_chunks", ""

    model, dense_status, dense_model_name = try_load_dense_model()

    if model is None:
        return {}, dense_status, dense_model_name

    documents = [build_chunk_document_text(chunk) for chunk in chunks]

    try:
        query_embedding = model.encode(
            query,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        doc_embeddings = model.encode(
            documents,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

    except Exception as e:
        return {}, f"dense_unavailable_encode_error: {type(e).__name__}", dense_model_name

    dense_scores: Dict[str, float] = {}

    for chunk, doc_embedding in zip(chunks, doc_embeddings):
        chunk_id = clean_value(chunk.get("chunk_id", ""))

        if not chunk_id:
            continue

        # normalize_embeddings=True라서 dot product가 cosine similarity 역할을 한다.
        raw_score = float(query_embedding @ doc_embedding)
        dense_scores[chunk_id] = round(normalize_dense_score(raw_score), 4)

    return dense_scores, dense_status, dense_model_name


if __name__ == "__main__":
    sample_query = "서울 사는 27세 무주택 구직자인데 월세 지원 받을 수 있을까?"

    sample_chunks = [
        {
            "chunk_id": "sample_1",
            "policy_name": "청년매입임대주택",
            "source_doc_name": "청년매입임대주택",
            "section_title": "입주대상",
            "chunk_text": "무주택 요건 및 소득·자산 기준을 충족하는 만 19세 이상 만 39세 이하 청년",
        },
        {
            "chunk_id": "sample_2",
            "policy_name": "청년 전세임대주택",
            "source_doc_name": "청년 전세임대주택",
            "section_title": "입주대상",
            "chunk_text": "무주택요건 및 소득·자산기준을 충족하는 대학생, 취업준비생, 19세~39세",
        },
    ]

    scores, status, model_name = retrieve_dense_scores(sample_query, sample_chunks)

    print("dense_status:", status)
    print("dense_model_name:", model_name)
    print("dense_scores:", scores)