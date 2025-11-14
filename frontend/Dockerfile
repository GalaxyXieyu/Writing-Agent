# 全局可用的构建参数（需放在文件最上方，便于在 FROM 中使用）
ARG NODE_IMAGE=node:18-alpine
ARG NGINX_IMAGE=nginx:alpine

# 第一阶段：构建阶段
FROM ${NODE_IMAGE} AS builder
WORKDIR /build

# 接收 Vite 环境变量（在构建阶段注入）
ARG VITE_AI_BASE_URL
ARG VITE_AI_API_KEY
ARG VITE_AI_MODEL
ARG VITE_AI_PROVIDER_TYPE
ENV VITE_AI_BASE_URL=${VITE_AI_BASE_URL} \
    VITE_AI_API_KEY=${VITE_AI_API_KEY} \
    VITE_AI_MODEL=${VITE_AI_MODEL} \
    VITE_AI_PROVIDER_TYPE=${VITE_AI_PROVIDER_TYPE}

# 复制 package 文件
COPY package*.json ./

# 使用镜像源并安装依赖
RUN npm config set registry https://registry.npmmirror.com \
    && npm install --legacy-peer-deps

# 复制所有源代码
COPY . .

# 构建静态文件（Vite 生产构建）
RUN npm run build

# 第二阶段：Nginx 服务阶段
FROM ${NGINX_IMAGE}

# 复制自定义 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 从构建阶段复制构建产物到 nginx 静态资源目录
COPY --from=builder /build/dist /usr/share/nginx/html

# 暴露 80 端口
EXPOSE 80

# 启动 nginx（前台模式）
CMD ["nginx", "-g", "daemon off;"]
