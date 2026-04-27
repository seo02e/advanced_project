## docker를 통한 PostgreSQL 서버 실행 방법

1. cmd 창 열기
2. 현재 프로젝트 경로로 이동
3. env.sample 파일 복사 후, 복사된 파일 .env로 변경(**env.sample 원본은 추후 환경설정을 위해 유지 필요!!**)
4. docker-compose up -d 명령어 입력
5. docker ps 명령어 실행 후 adv_3team_db 이름의 container 가 Up 상태인지 확인
   ![alt text](docker_image1.png)
6. 정상적으로 Up 확인 이후, DB툴 통해서 접속
7. 접속의 필요한 정보는 복사된 .env 파일 참조
