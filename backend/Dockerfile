ARG BASE_IMAGE=python:3.10-slim
FROM ${BASE_IMAGE}

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 系统依赖（常见构建工具与运行库）
# 切换 Debian 源为国内镜像（bookworm），避免官方源网络不稳
RUN set -eux; \
    rm -f /etc/apt/sources.list.d/debian.sources || true; \
    echo 'deb https://mirrors.aliyun.com/debian/ bookworm main contrib non-free non-free-firmware' > /etc/apt/sources.list; \
    echo 'deb https://mirrors.aliyun.com/debian/ bookworm-updates main contrib non-free non-free-firmware' >> /etc/apt/sources.list; \
    echo 'deb https://mirrors.aliyun.com/debian-security bookworm-security main contrib non-free non-free-firmware' >> /etc/apt/sources.list; \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    pkg-config \
    libcairo2-dev \
    rustc \
    cargo \
    libffi-dev \
    libssl-dev \
    curl \
    ffmpeg \
    git \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./

RUN python -m pip install --upgrade pip setuptools wheel \
 && python -m pip install -r requirements.txt -i https://pypi.org/simple

# 将应用源码在运行时通过挂载卷提供（compose 中有 volumes）
# 这里保持容器常驻，由具体服务在 docker-compose 中覆盖 command
CMD ["tail", "-f", "/dev/null"]