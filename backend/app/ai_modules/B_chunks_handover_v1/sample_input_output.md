# B housing handover v1 샘플 입력/출력

## 이번 제출 목표
주거 질문이 들어왔을 때 D가 읽을 수 있는 최소 chunk set을 제공한다.

## 입력
사용자 질문 예시:

```txt
서울 사는 27세 무주택 구직자인데 월세 지원 받을 수 있을까?
```

## D에서 기대하는 출력 일부

```json
{
  "retrieved_chunks": [
    {
      "chunk_id": "BH001_02",
      "policy_name": "청년 주거지원 공통 확인사항",
      "section_title": "월세 지원 확인사항",
      "chunk_text": "[청년 주거지원 공통 확인사항 | 월세 지원 확인사항] 월세 지원 여부를 판단하려면 실제 월세 거주 여부, 임대차계약 상태, 보증금 또는 월세 금액, 소득수준, 무주택 여부 확인이 필요합니다."
    }
  ]
}
```

## 다음 레이어 전달 형식

```json
{
  "chunk_id": "BH001_02",
  "policy_id": "BH001",
  "policy_name": "청년 주거지원 공통 확인사항",
  "issuing_org": "Youth-Sync handover",
  "source_doc_name": "B_housing_handover_v1",
  "source_url": "",
  "section_title": "월세 지원 확인사항",
  "chunk_text": "...",
  "chunk_order": 2,
  "has_table": false,
  "doc_type": "handover_stub",
  "created_from": "B_housing_handover_v1"
}
```