ARG BASE_IMAGE=python:3.10-slim-bookworm
ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
FROM ${BASE_IMAGE}

# 重新声明 ARG，以便在 FROM 之后使用
ARG PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# 将 ARG 转换为 ENV，确保在 RUN 命令中可用
ENV PIP_INDEX_URL=${PIP_INDEX_URL} \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 系统依赖（构建与运行必需）
# 使用清华镜像（bookworm），并仅安装必要包，降低依赖冲突概率
RUN set -eux; \
    rm -rf /etc/apt/sources.list.d/* || true; \
    printf 'deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm main contrib non-free non-free-firmware\n' > /etc/apt/sources.list; \
    printf 'deb https://mirrors.tuna.tsinghua.edu.cn/debian/ bookworm-updates main contrib non-free non-free-firmware\n' >> /etc/apt/sources.list; \
    printf 'deb https://mirrors.tuna.tsinghua.edu.cn/debian-security bookworm-security main contrib non-free non-free-firmware\n' >> /etc/apt/sources.list; \
    apt-get update -o Acquire::Retries=3; \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    ca-certificates \
    gcc \
    g++ \
    make \
    pkg-config \
    libcairo2-dev \
    libffi-dev \
    libssl-dev \
    curl \
    ffmpeg \
    git \
    libreoffice-writer-nogui; \
    rm -rf /var/lib/apt/lists/*

COPY requirements-prod.txt ./

# 使用 ARG 值安装依赖，ARG 已在 FROM 后重新声明且有默认值
RUN python -m pip install --upgrade pip setuptools wheel -i "${PIP_INDEX_URL}" && \
    python -m pip install -r requirements-prod.txt -i "${PIP_INDEX_URL}"

# 将应用源码在运行时通过挂载卷提供（compose 中有 volumes）
# 这里保持容器常驻，由具体服务在 docker-compose 中覆盖 command
CMD ["tail", "-f", "/dev/null"]