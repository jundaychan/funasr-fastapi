import os

from celery import Celery
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()
# 从环境变量中获取配置
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = int(os.getenv('REDIS_PORT'))
CELERY_DB = int(os.getenv('CELERY_DB'))


# 初始化 Celery 实例
celery_app = Celery(
    'tasks',
    broker=f'redis://{REDIS_HOST}:{REDIS_PORT}/{CELERY_DB}',  # Redis 作为消息代理
    backend=f'redis://{REDIS_HOST}:{REDIS_PORT}/{CELERY_DB}',  # Redis 作为结果存储
    include=['app.asr_client']  # 包含任务模块
)

celery_app.conf.task_default_expires = timedelta(hours=1)  # 例如，设置1小时后过期
celery_app.conf.update(
    task_routes={
        'app.asr_client.voice2text': {'queue': 'asr_queue'},  # 定义任务路由
    },
    task_default_expires = timedelta(hours=1),
    # 日志配置
    worker_hijack_root_logger = False,
    worker_log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    worker_task_log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    worker_redirect_stdouts = True,
    worker_redirect_stdouts_level = 'INFO',
)

