# run_day4_tests.py
# Youth-Sync Day4 test runner
# 목적:
# - 질문 5개를 rag_pipeline_final.py로 실행
# - 전체 결과는 JSON 파일로 저장
# - 콘솔에는 짧은 요약만 출력

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from rag_pipeline import answer_question


CURRENT_DIR = Path(__file__).resolve().parent

OUTPUT_JSON_PATH = CURRENT_DIR / "day4_test_outputs.json"
OUTPUT_SUMMARY_PATH = CURRENT_DIR / "day4_test_summary.txt"


TEST_QUESTIONS = [
    "서울 사는 27세 무주택 구직자인데 월세 지원 받을 수 있을까?",
    "경기도 거주 25세 중소기업 재직자인데 취업 지원 정책이 있을까?",
    "서울 거주 31세 직장인인데 청년 정책 대상이 아직 되나",
    "올해 퇴사한 28세 자취생인데 월세가 부담돼",
    "무주택인데 세대주는 아니야. 주거 지원이 가능해?",
]


def clean_value(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip()


def summarize_result(index: int, question: str, result: Dict[str, Any]) -> Dict[str, Any]:
    recommended_policies = result.get("recommended_policies", [])
    retrieved_chunks = result.get("retrieved_chunks", [])
    debug = result.get("debug", {})

    # LLM 결과 위치 보정
    # 정상 위치: result["llm_answer_generation"]
    # 혹시 debug에만 들어간 경우도 대비
    llm_info = result.get("llm_answer_generation", {}) or {}
    llm_generation_status = clean_value(
        llm_info.get("llm_generation_status", "")
        or debug.get("llm_generation_status", "")
    )
    llm_model_name = clean_value(
        llm_info.get("llm_model_name", "")
        or debug.get("llm_model_name", "")
    )

    policy_summary = []

    for policy in recommended_policies[:3]:
        policy_summary.append(
            {
                "policy_name": clean_value(policy.get("policy_name", "")),
                "source_layer": clean_value(policy.get("source_layer", "")),
                "eligibility_status": clean_value(policy.get("eligibility_status", "")),
                "missing_requirements": policy.get("missing_requirements", []),
            }
        )

    return {
        "case_no": index,
        "question": question,
        "result_status": clean_value(result.get("result_status", "")),
        "primary_interest": clean_value(debug.get("primary_interest", "")),
        "recommended_policy_count": len(recommended_policies),
        "retrieved_chunk_count": len(retrieved_chunks),
        "retrieval_method": clean_value(debug.get("retrieval_method", "")),
        "dense_status": clean_value(debug.get("dense_status", "")),
        "dense_model_name": clean_value(debug.get("dense_model_name", "")),
        "llm_generation_status": llm_generation_status,
        "llm_model_name": llm_model_name,
        "need_more_info": result.get("need_more_info", []),
        "top_policies": policy_summary,
    }


def build_summary_text(summaries: List[Dict[str, Any]]) -> str:
    lines: List[str] = []

    lines.append("# Youth-Sync Day4 Test Summary")
    lines.append("")
    lines.append("목적: A~D 서비스 코어 기준 1~5단계 동작 확인")
    lines.append("")

    for item in summaries:
        lines.append("=" * 80)
        lines.append(f"CASE {item['case_no']}")
        lines.append(f"질문: {item['question']}")
        lines.append(f"결과상태: {item['result_status']}")
        lines.append(f"관심분야: {item['primary_interest']}")
        lines.append(f"추천정책 수: {item['recommended_policy_count']}")
        lines.append(f"검색 chunk 수: {item['retrieved_chunk_count']}")
        lines.append(f"검색방식: {item['retrieval_method']}")
        lines.append(f"Dense 상태: {item['dense_status']}")
        lines.append(f"Dense 모델: {item['dense_model_name'] if item['dense_model_name'] else '없음'}")
        lines.append(f"LLM 상태: {item['llm_generation_status'] if item['llm_generation_status'] else '없음'}")
        lines.append(f"LLM 모델: {item['llm_model_name'] if item['llm_model_name'] else '없음'}")
        lines.append(f"추가확인: {', '.join(item['need_more_info']) if item['need_more_info'] else '없음'}")
        
        lines.append("상위 정책:")
        if item["top_policies"]:
            for policy in item["top_policies"]:
                missing = policy.get("missing_requirements", [])
                missing_text = ", ".join(missing) if missing else "없음"

                lines.append(
                    f"- {policy['policy_name']} "
                    f"/ source={policy['source_layer']} "
                    f"/ eligibility={policy['eligibility_status']} "
                    f"/ missing={missing_text}"
                )
        else:
            lines.append("- 없음")

        lines.append("")

    return "\n".join(lines)


def main() -> None:
    full_outputs: List[Dict[str, Any]] = []
    summaries: List[Dict[str, Any]] = []

    for index, question in enumerate(TEST_QUESTIONS, start=1):
        result = answer_question(question)

        full_outputs.append(
            {
                "case_no": index,
                "question": question,
                "result": result,
            }
        )

        summaries.append(summarize_result(index, question, result))

    with OUTPUT_JSON_PATH.open("w", encoding="utf-8") as f:
        json.dump(full_outputs, f, ensure_ascii=False, indent=2)

    summary_text = build_summary_text(summaries)

    with OUTPUT_SUMMARY_PATH.open("w", encoding="utf-8") as f:
        f.write(summary_text)

    print(summary_text)
    print("=" * 80)
    print(f"전체 JSON 저장 완료: {OUTPUT_JSON_PATH}")
    print(f"요약 TXT 저장 완료: {OUTPUT_SUMMARY_PATH}")


if __name__ == "__main__":
    main()