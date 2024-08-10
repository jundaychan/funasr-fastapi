# 使用官方Python镜像作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /asr

COPY . .

# 复制requirements.txt文件到工作目录
COPY requirements.txt .

# 安装Python依赖
RUN pip install --upgrade pip -i https://mirrors.tencent.com/pypi/simple \
    && pip install -r requirements.txt -i https://mirrors.tencent.com/pypi/simple

# 复制当前目录的内容到工作目录

# 暴露应用的端口
EXPOSE 8000

# 运行应用程序
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
