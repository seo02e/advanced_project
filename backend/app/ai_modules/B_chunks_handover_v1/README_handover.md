# B housing handover v1

## 목적
이 폴더는 기존 B 담당자의 `B_chunks/` 산출물을 수정하거나 대체하기 위한 폴더가 아니다.

Day4 통합 테스트를 위해, D가 바로 읽을 수 있는 독립형 주거 chunk 전달본을 만든 폴더다.

## 원칙
- 기존 `B_chunks/` 원본은 건드리지 않는다.
- 기존 B 산출물에서 자동 변환하지 않는다.
- 이 폴더는 A의 `A_policy_handover_v2`처럼 통합용 전달본이다.
- 실제 공고문 기반 최종 chunk가 들어오면 `B_housing_handover_v2`로 새로 만든다.

## 최종 전달 파일
- `housing_chunks_final.jsonl`

## D 연결 방식
D는 주거 질문일 때 이 파일을 읽어 `retrieved_chunks`에 주거 관련 근거 chunk를 붙인다.

## 현재 한계
- 이 데이터는 실제 공고문 최종 파싱 결과가 아니라 Day4 연결 검증용 최소 데이터다.
- source_url은 아직 비워둔다.
- 최종 신청 가능 여부는 확인 필요로 처리한다.