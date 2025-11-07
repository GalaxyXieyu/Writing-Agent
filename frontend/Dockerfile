# 第一阶段：构建阶段
ARG NODE_IMAGE=docker.m.daocloud.io/library/node:18-alpine
FROM ${NODE_IMAGE} AS builder

WORKDIR /build

# 复制 package 文件
COPY package*.json ./

# 使用镜像源并安装依赖
RUN npm config set registry https://registry.npmmirror.com \
    && npm install --legacy-peer-deps

# 复制所有源代码
COPY . .

# 构建静态文件（H5）
RUN npm run build:h5

# 第二阶段：Nginx 服务阶段
FROM docker.m.daocloud.io/library/nginx:alpine

# 复制自定义 nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 从构建阶段复制构建产物到 nginx 静态资源目录
COPY --from=builder /build/dist/build/h5 /usr/share/nginx/html

# 暴露 80 端口
EXPOSE 80

# 启动 nginx（前台模式）
CMD ["nginx", "-g", "daemon off;"]
