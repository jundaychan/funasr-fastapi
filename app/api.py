import json

from fastapi import APIRouter
import uuid

from pydantic import BaseModel
from app.celery_config import celery_app
from app.config import REDIS_CLIENT as r

router = APIRouter(prefix="/asr",tags=["asr转写文字服务"])
class AudioRequest(BaseModel):
    audio_url: str
@router.post("/start")
async def start_asr_process(request: AudioRequest):
    task_id = str(uuid.uuid4())
    r.set(task_id, "正在处理中")  # 设置任务状态
    data = {"task_id": task_id, "audio_url": request.audio_url}
    celery_app.send_task('app.asr_client.voice2text', args=[task_id, request.audio_url])
    return data
# 任务状态，waiting：任务等待，doing：任务执行中，success：任务成功，failed：任务失败。
# 示例值：waiting
# 任务状态码，0：任务等待，1：任务执行中，2：任务成功，3：任务失败。
# 示例值：0
@router.get("/result/{task_id}")
async def get_result(task_id: str):
    try:
        result = r.get(task_id)
    except:
        result = None
    if not result:
        return {"code": 200, "status": 3,"status_str":"can not find"}
    if result == "正在处理中":
        return {"code": 200, "status": 1,"status_str":"doing"}
    elif result == '任务失败':
        return {"code": 200, "status": 3,"status_str":"failed"}
    else:
        result = json.loads(result)
        return {"code": 200, "status": 2, "result": result,"status_str":"failed"}