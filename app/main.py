
from fastapi import FastAPI
from app.api import router

app = FastAPI(
    title="asr服务",
    version="0.0.1"
)


app.include_router(router)



# 在主模块保护下初始化全局变量和启动应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
