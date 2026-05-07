import logging
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.policy_from_api_service import policy_from_api

logger = logging.getLogger(__name__)


# 서울 시간 기준으로 실행하기 위한 백그라운드 스케줄러 객체 생성
scheduler = BackgroundScheduler(timezone="Asia/Seoul")


# 스케줄러에 실행할 로직
def youth_policy_api_batch():
    logger.info("youth_policy_api_batch start")
    policy_from_api()
    logger.info("youth_policy_api_batch end")
    
    
# 스케줄러 실행시 수행할 job 등록
def youth_policy_api_batch_job():
    logger.info("youth_policy_api_batch_job start")
    youth_policy_api_batch()
    logger.info("youth_policy_api_batch_job end")
    

# 서버 실행시 수행할 스케줄러 등록
def start_scheduler():
    scheduler.add_job(
        youth_policy_api_batch_job,
        trigger="cron",
        hour="00",
        minute="00",
        id="youth_policy_api_batch_job",
        replace_existing=True,  # id가 겹칠시 덮어쓰기 할 지 여부 설정
        max_instances=1,        # 하나의 job 이 동시에 몇 개까지 실행될 수 있는지 설정
        coalesce=True,          # 밀린 실행들을 각각 실행할지(False), 하나로 합쳐 실행할지(True) 설정
        misfire_grace_time=1200,  # 스케줄 시간이 초과했을 때, 늦게 실행을 허용해주는 시간 설정
    )
    
    if not scheduler.running:    
        scheduler.start()
    

# 서버 중지시 수행할 스케줄러 등록
def end_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        