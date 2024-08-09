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

@router.get("/result/{task_id}")
async def get_result(task_id: str):
    result = r.get(task_id)
    if not result:
        return {"code": -1, "status": "任务ID未找到"}
    if result == "正在处理中":
        return {"code": 1, "status": "正在处理中"}
    elif result == '任务失败':
        return {"code": -1, "status": "任务失败"}
    else:
        result = json.loads(result)
        return {"code": 0, "status": "已完成", "result": result}