import json
import uuid

from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel

from app.asr_client import voice2text
from app.config import REDIS_CLIENT as r

app = FastAPI()


class AudioRequest(BaseModel):
    audio_url: str


@app.post("/asr/start")
async def start_asr_process(request: AudioRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    r.set(task_id, "正在处理中")  # 设置任务状态
    data = {"task_id": task_id, "audio_url": request.audio_url}
    background_tasks.add_task(voice2text,  task_id=task_id,wav=request.audio_url)
    return data

@app.get("/result/{task_id}")
async def get_result(task_id: str):
    result = r.get(task_id)
    if not result:
        return {"code": "-1", "status": "任务ID未找到"}
    if result != "正在处理中":
        result = json.loads(result)
        return {"code": "0", "status": "已完成", "result": result}
    else:
        return {"code": "-1", "status": "正在处理中"}


# 在主模块保护下初始化全局变量和启动应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
