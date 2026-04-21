import axios from "axios";
// axios 라이브러리를 가져온다.
// axios는 프론트에서 백엔드 api로 http 요청을 보낼 때 사용하는 도구

export const api = axios.create({
  // axios 인스턴스 생성
  // 따로 인스턴스를 만드는 이유는 여러 api 요청에서 공통으로 사용할 설정
  // baseURL, 쿠키 포함 여부 등을 한번에 관리하기 위함

  baseURL: import.meta.env.VITE_API_BASE_URL,
  // 모든 요청 앞에 공통으로 붙는 기본주소 (하드코딩 된 경우 숨기기)

  withCredentials: true,
  //요청을 보낼때 쿠키, 인증 정보 같은 자격 증명을 함께 포함하겠다는 의미.
  // 필요한 이유 : 현재 세션 기반 인증 방식을 사용하고 있기 때문
  // 백엔드에서 set-cookie로 session_id를 내려주면
  // 이후 프론트가 요청 시 그 쿠키를 자동으로 같이 보내야
  // 같은 사용자임을 서버가 인식할 수 있음
});
