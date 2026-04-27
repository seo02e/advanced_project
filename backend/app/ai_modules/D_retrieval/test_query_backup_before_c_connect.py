from rag_pipeline import generate_response
import json

query = "서울에서 취업 준비중인데 지원 받을 수 있을까?"

mock_profile = {
    "age": 26,
    "region": "서울",
    "employment_status": "job_seeking",
    "housing_status": "unknown",
    "income_level": "unknown",
    "interest_tags": ["취업"],
    "unknown_fields": ["income_level"]
}

result = generate_response(query, mock_profile)

print(json.dumps(result, ensure_ascii=False, indent=2))