# TradeBusiness 管理端、客户端与 WebSocket 部署指南

本文说明如何在 Ubuntu 服务器上使用 Nginx 部署：

- 管理端：`tradebusiness-admin`
- 客户端：`tradebusiness-client`
- FastAPI：`tradebusiness-backend`
- 通知 WebSocket：`/api/v1/notifications/ws/{user_id}`

推荐使用两个域名：

```text
管理端：admin.example.com
客户端：client.example.com
```

如果暂时只有服务器 IP，也可以使用：

```text
管理端：http://8.145.59.67/admin/
客户端：http://8.145.59.67/client/
```

域名部署更适合生产环境，因为 Let’s Encrypt 证书通常需要域名，且 HTTPS 下 WebSocket 会自动使用 `wss://`。

## 一、部署架构

```text
浏览器
  │
  ├── https://admin.example.com       ── Nginx ── admin/dist
  ├── https://client.example.com      ── Nginx ── client/dist
  ├── /api/...                        ── Nginx ── 127.0.0.1:8000
  └── /api/v1/notifications/ws/...   ── Nginx ── 127.0.0.1:8000
```

前端生产配置使用同源地址：

```env
VITE_APP_BASE_API=
VITE_APP_WS_URL=
```

留空后，前端会请求当前域名下的 `/api/...`，并根据页面协议自动使用 `ws://` 或 `wss://`。这样浏览器不需要跨域访问 `8000` 端口。

## 二、服务器准备

以下命令适用于 Ubuntu 22.04/24.04：

```bash
sudo apt update
sudo apt install -y nginx git curl ca-certificates
sudo systemctl enable --now nginx
```

开放防火墙端口：

```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable
```

不要将后端 `8000` 端口暴露给公网；后端只监听本机或 Docker 内部网络，由 Nginx 代理访问。

## 三、准备项目目录

示例目录：

```text
/opt/tradebusiness/
├── tradebusiness-admin/
├── tradebusiness-client/
└── tradebusiness-backend/
```

```bash
sudo mkdir -p /opt/tradebusiness
sudo chown -R "$USER":"$USER" /opt/tradebusiness
cd /opt/tradebusiness

git clone <项目仓库地址> .
```

如果项目已经上传到服务器，确认目录存在：

```bash
cd /opt/tradebusiness
test -f tradebusiness-admin/package.json
test -f tradebusiness-client/package.json
test -f tradebusiness-backend/docker-compose.prod.yml
```

## 四、启动后端

### 方式 A：Docker Compose（推荐）

进入后端目录并准备生产环境文件：

```bash
cd /opt/tradebusiness/tradebusiness-backend
cp .env.production.example .env.production
nano .env.production
```

至少配置以下内容：

```env
ENVIRONMENT=production
DEBUG=false

SECRET_KEY=请填写32位以上随机字符串
JWT_SECRET_KEY=请填写另一组32位以上随机字符串

# 使用域名时填写前端域名；同源代理后仍建议保留
CORS_ORIGINS=https://admin.example.com,https://client.example.com
```

生成随机密钥：

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```

启动服务：

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build
docker compose --env-file .env.production -f docker-compose.prod.yml ps
```

确认后端正常：

```bash
curl -i http://127.0.0.1:8000/health
docker compose --env-file .env.production -f docker-compose.prod.yml logs --tail=100 backend
```

WebSocket 依赖已经在 `requirements.txt` 中包含：

```text
uvicorn[standard]
websockets
```

如果日志仍显示 `No supported WebSocket library detected`，重新构建后端镜像：

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml build --no-cache backend
docker compose --env-file .env.production -f docker-compose.prod.yml up -d backend
```

### 方式 B：systemd + Python 虚拟环境

```bash
cd /opt/tradebusiness/tradebusiness-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

创建服务：

```bash
sudo nano /etc/systemd/system/tradebusiness.service
```

内容：

```ini
[Unit]
Description=TradeBusiness FastAPI
After=network.target mysql.service redis-server.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/tradebusiness/tradebusiness-backend
EnvironmentFile=/opt/tradebusiness/tradebusiness-backend/.env
ExecStart=/opt/tradebusiness/tradebusiness-backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo chown -R www-data:www-data /opt/tradebusiness/tradebusiness-backend
sudo systemctl daemon-reload
sudo systemctl enable --now tradebusiness
sudo systemctl status tradebusiness
```

两种方式只能选择一种，不要同时启动两个后端占用同一端口。

## 五、构建管理端和客户端

安装 Node.js 20 LTS 后，在服务器构建：

```bash
cd /opt/tradebusiness/tradebusiness-admin
npm ci
```

确认 `.env.production`：

```env
VITE_APP_TITLE=货运代理业务管理系统
VITE_APP_BASE_API=
VITE_APP_WS_URL=
```

构建管理端：

```bash
npm run type-check
npm run build
```

构建客户端：

```bash
cd /opt/tradebusiness/tradebusiness-client
npm ci
```

确认同样使用：

```env
VITE_APP_BASE_API=
VITE_APP_WS_URL=
```

```bash
npm run build
```

## 六、配置 Nginx（域名部署）

复制模板：

```bash
cd /opt/tradebusiness
sudo cp deploy/nginx/tradebusiness.conf.example \
  /etc/nginx/sites-available/tradebusiness.conf
sudo cp deploy/nginx/proxy_params /etc/nginx/proxy_params
```

编辑配置：

```bash
sudo nano /etc/nginx/sites-available/tradebusiness.conf
```

替换以下内容：

```text
admin.example.com       → 实际管理端域名
client.example.com      → 实际客户端域名
/opt/tradebusiness/...  → 实际项目路径
```

模板已经包含：

- 管理端静态文件和 Vue history fallback
- 客户端静态文件和 Vue history fallback
- `/api/` 反向代理
- `/uploads/` 反向代理
- WebSocket Upgrade 头
- 长连接超时

确认两个前端目录存在：

```bash
test -f /opt/tradebusiness/tradebusiness-admin/dist/index.html
test -f /opt/tradebusiness/tradebusiness-client/dist/index.html
```

启用站点：

```bash
sudo ln -sf /etc/nginx/sites-available/tradebusiness.conf \
  /etc/nginx/sites-enabled/tradebusiness.conf
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

## 七、申请 HTTPS 证书

确保 DNS 已将两个域名解析到服务器 IP，并确认 80 端口可访问：

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx \
  -d admin.example.com \
  -d client.example.com
```

测试自动续期：

```bash
sudo certbot renew --dry-run
```

HTTPS 启用后，前端 WebSocket 地址应为：

```text
wss://admin.example.com/api/v1/notifications/ws/<user_id>
wss://client.example.com/api/v1/notifications/ws/<user_id>
```

不要在 HTTPS 页面中使用 `ws://`，浏览器会阻止混合内容。

## 八、只有 IP 时的临时部署

没有域名时，可以先使用 HTTP 和不同路径：

```nginx
server {
    listen 80;
    server_name 8.145.59.67;

    root /opt/tradebusiness;

    location /admin/ {
        alias /opt/tradebusiness/tradebusiness-admin/dist/;
        try_files $uri $uri/ /admin/index.html;
    }

    location /client/ {
        alias /opt/tradebusiness/tradebusiness-client/dist/;
        try_files $uri $uri/ /client/index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        include proxy_params;
    }

    location /uploads/ {
        proxy_pass http://127.0.0.1:8000;
        include proxy_params;
    }
}
```

但当前前端默认使用当前 `host`，如果通过 `/admin/` 或 `/client/` 访问，前端路由基础路径还需要在 Vite 配置中设置对应 `base`，因此生产环境优先使用两个域名。

## 九、验证清单

### 1. 静态页面

```bash
curl -I https://admin.example.com/
curl -I https://client.example.com/
```

### 2. API 代理

```bash
curl -i https://admin.example.com/health
curl -i https://admin.example.com/api/v1/users?skip=0\&limit=20
```

如果 `/health` 没有通过 `/api` 前缀暴露，可直接检查：

```bash
curl -i http://127.0.0.1:8000/health
```

### 3. WebSocket

浏览器开发者工具中应看到：

```text
Status Code: 101 Switching Protocols
```

服务器日志应包含类似：

```text
WebSocket connected
```

也可以使用 `websocat`：

```bash
sudo apt install -y websocat
websocat wss://admin.example.com/api/v1/notifications/ws/<user_id>
```

### 4. Nginx 日志

```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 十、常见问题

### 页面访问正常，但 API 404

确认前端生产配置中的 `VITE_APP_BASE_API` 是空值，并重新构建。请求应为：

```text
/api/v1/...
```

不要把旧的：

```text
http://8.145.59.67:8000/api/...
```

写入生产构建。

### 浏览器仍然报 CORS

说明前端仍然直接访问 `:8000`，或者使用了旧的 `dist` 文件。检查：

```bash
grep -R "8000" /opt/tradebusiness/tradebusiness-admin/dist \
  /opt/tradebusiness/tradebusiness-client/dist
```

重新构建并清空 Nginx 静态目录后，使用 `Ctrl+F5` 强制刷新。

### WebSocket 报 Unsupported upgrade request

依次检查：

```bash
pip show websockets
docker compose ps
sudo nginx -t
```

确认 `deploy/nginx/proxy_params` 中包含：

```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection $connection_upgrade;
proxy_read_timeout 60s;
```

并确认 Nginx 配置中存在：

```nginx
map $http_upgrade $connection_upgrade {
    default upgrade;
    '' close;
}
```

### API 返回 422

这是请求参数校验失败，不是 Nginx 错误。查看浏览器 Network 的响应体 `errors`，检查 `status`、`skip`、`limit` 等参数。客户状态只能使用：

```text
potential, contacting, cooperating, paused, lost
```

### API 返回 502 Bad Gateway

说明 Nginx 无法连接后端：

```bash
curl -i http://127.0.0.1:8000/health
docker compose logs --tail=100 backend
sudo ss -lntp | grep 8000
```

### 修改前端后页面没有变化

```bash
rm -rf tradebusiness-admin/dist tradebusiness-client/dist
cd tradebusiness-admin && npm run build
cd ../tradebusiness-client && npm run build
sudo systemctl reload nginx
```

然后清理浏览器缓存并强制刷新。

## 十一、发布更新流程

```bash
cd /opt/tradebusiness
git pull

cd tradebusiness-backend
docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build backend celery-worker celery-beat

cd ../tradebusiness-admin
npm ci
npm run type-check
npm run build

cd ../tradebusiness-client
npm ci
npm run build

sudo nginx -t
sudo systemctl reload nginx
```

数据库结构变更必须先执行对应迁移，再重启后端；不要只重新构建镜像。生产环境至少备份数据库：

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml exec -T mysql \
  sh -c 'mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" "$MYSQL_DATABASE"' \
  > /opt/tradebusiness/backup-$(date +%F-%H%M%S).sql
```

## 十二、安全要求

- 生产环境使用 HTTPS。
- 不要将 `8000`、MySQL `3306`、Redis `6379` 暴露到公网。
- 不要在前端 `.env.production` 中写入数据库密码、JWT 密钥或其他服务端密钥。
- `CORS_ORIGINS` 使用完整来源，不要使用 `*` 配合 `allow_credentials=true`。
- 修改 Nginx 后始终先执行 `nginx -t`，通过后再 reload。
- 定期执行数据库备份和 `certbot renew --dry-run`。
