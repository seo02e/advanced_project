## 📂 src 구조

```plaintext
src/
├─ api/ # 백엔드 API 통신
│ ├─ axios.ts # axios 인스턴스 설정
│ ├─ sessionApi.ts # 세션 관련 API
│ └─ chatApi.ts # 채팅 관련 API
│
├─ components/ # UI 컴포넌트
│ └─ chat/
│ ├─ ChatMessage.tsx # 메시지 말풍선
│ ├─ ChatInput.tsx # 입력창
│ └─ ChatWindow.tsx # 채팅창
│
├─ hooks/ # 상태 관리 (커스텀 훅)
│ ├─ useSession.ts # 세션 관리
│ └─ useChat.ts # 채팅 상태 관리
│
├─ pages/ # 페이지 단위 컴포넌트
│ └─ ChatPage.tsx # 메인 채팅 페이지
│
├─ types/ # 타입 정의
│ ├─ session.ts
│ └─ chat.ts
│
├─ App.tsx # 루트 컴포넌트
├─ main.tsx # 앱 진입점
└─ index.css # 전역 스타일
```
