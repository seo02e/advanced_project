# test_query.py
# Youth-Sync D Layer test
# 목적: 사용자 질문 -> C profile parser -> D rag pipeline 응답 생성 연결 테스트

from __future__ import annotations

import json
import sys
from pathlib import Path


CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent

C_PROFILE_DIR = PROJECT_ROOT / "C_profile"

if str(C_PROFILE_DIR) not in sys.path:
    sys.path.append(str(C_PROFILE_DIR))

from profile_parser_final import parse_profile  # noqa: E402


def load_rag_pipeline():
    """
    기존 D 파일 구조가 사람마다 조금 다를 수 있으므로,
    rag_pipeline.py 안의 함수 이름에 맞춰 최소 연결한다.
    """
    try:
        import rag_pipeline
        return rag_pipeline
    except Exception as e:
        raise RuntimeError(f"rag_pipeline.py import 실패: {e}")


def run_one_question(raw_text: str) -> dict:
    profile = parse_profile(raw_text)

    rag_pipeline = load_rag_pipeline()

    # 1순위: generate_answer(profile) 함수가 있는 경우
    if hasattr(rag_pipeline, "generate_answer"):
        answer = rag_pipeline.generate_answer(profile)

    # 2순위: run_pipeline(profile) 함수가 있는 경우
    elif hasattr(rag_pipeline, "run_pipeline"):
        answer = rag_pipeline.run_pipeline(profile)

    # 3순위: answer_question(raw_text, profile) 함수가 있는 경우
    elif hasattr(rag_pipeline, "answer_question"):
        answer = rag_pipeline.answer_question(raw_text, profile)

    else:
        raise AttributeError(
            "rag_pipeline.py 안에서 generate_answer(profile), "
            "run_pipeline(profile), answer_question(raw_text, profile) 중 하나가 필요합니다."
        )

    return {
        "raw_text": raw_text,
        "parsed_profile": profile,
        "answer": answer
    }


if __name__ == "__main__":
    test_questions = [
        "서울 사는 27세 무주택 구직자인데 월세 지원 받을 수 있을까?",
        "경기도 거주 25세 중소기업 재직자인데 취업 지원 정책이 있을까?",
        "부모님 집에 사는 29세 취준생인데 주거 지원이 있을까?",
        "지방에서 서울로 취업 준비 중인 24세인데 주거랑 취업 둘 다 보고 싶어",
        "올해 퇴사한 28세 자취생인데 월세가 부담돼",
        "서울 거주 31세 직장인인데 청년 정책 대상이 아직 되나",
        "무주택인데 세대주는 아니야. 주거 지원이 가능해?",
        "취업 준비 중인데 소득이 거의 없고 부모님과 같이 살아",
        "신청 마감 안 된 정책만 보고 싶어. 서울 거주 26세야",
        "정규직 재직 중인데 이직 준비 중이야. 취업 지원 대상이 되나"
    ]

    results = []

    for question in test_questions:
        result = run_one_question(question)
        results.append(result)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("-" * 100)

    output_path = CURRENT_DIR / "c_connected_query_results.json"
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"저장 완료: {output_path}")