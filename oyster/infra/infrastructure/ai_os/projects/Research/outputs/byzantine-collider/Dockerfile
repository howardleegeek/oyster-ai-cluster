FROM python:3.11-slim

LABEL maintainer="Oyster Labs"
LABEL description="Byzantine Collider - AI-to-AI Product Collision System"

# 环境变量
ENV PYTHONUNBUFFERED=1
ENV PORT=5000

# 工作目录
WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python3", "api.py"]
