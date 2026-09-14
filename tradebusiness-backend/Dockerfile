# 多阶段构建 Dockerfile
# Stage 1: 构建
FROM python:3.11-slim as builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖到临时目录
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: 运行
FROM python:3.11-slim

WORKDIR /app

# 安装运行时依赖
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 从 builder 复制安装的包
COPY --from=builder /root/.local /root/.local

# 确保脚本在 PATH 中
ENV PATH=/root/.local/bin:$PATH

# 复制应用代码
COPY . .

# 创建日志和上传目录
RUN mkdir -p logs uploads

# 暴露端口
EXPOSE 8000

# 默认命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
