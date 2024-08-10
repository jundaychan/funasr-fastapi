# 加载 .env 文件中的环境变量
import os

import redis
from dotenv import load_dotenv

load_dotenv()

# 从环境变量中获取配置
ASR_HOST = os.getenv('ASR_HOST')
ASR_PORT = int(os.getenv('ASR_PORT'))
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = int(os.getenv('REDIS_PORT'))
REDIS_DB = int(os.getenv('REDIS_DB'))

REDIS_CLIENT = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)
