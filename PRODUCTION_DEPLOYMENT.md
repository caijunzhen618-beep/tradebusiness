# 货运代理业务管理系统生产部署操作手册

本文档说明如何把本项目部署到生产环境，并说明如何安装/更新依赖模块、配置参数、构建前端、启动后端和日常更新。

## 1. 项目组成

项目包含三个主要模块：

- `tradebusiness-backend/`：FastAPI 后端服务，连接 MySQL、Redis、SMTP。
- `tradebusiness-admin/`：管理端 Vue/Vite 前端。
- `tradebusiness-client/`：客户端 Vue/Vite 前端。

推荐生产部署方式：

- 后端、MySQL、Redis 使用 Docker Compose。
- 两个前端执行 `npm run build` 后，将 `dist/` 静态文件部署到 Nginx。
- Nginx 负责 HTTPS、静态文件、反向代理 `/api/` 和 WebSocket。

## 2. 服务器基础要求

推荐配置：

- 操作系统：Ubuntu 22.04 LTS 或更新版本
- CPU：2 核以上
- 内存：4 GB 以上
- 磁盘：40 GB 以上 SSD
- 域名：至少准备管理端域名和客户端域名，例如：
  - `admin.example.com`
  - `client.example.com`
  - `api.example.com` 可选，如果不单独使用 API 域名，也可以同域反向代理 `/api/`

必须安装：

```bash
sudo apt update
sudo apt install -y git curl ca-certificates nginx
```

安装 Docker：

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
```

安装 Docker Compose 插件：

```bash
sudo apt install -y docker-compose-plugin
docker compose version
```

安装 Node.js 20 LTS：

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
node -v
npm -v
```

如果不用 Docker 运行后端，还需要 Python 3.11+：

```bash
sudo apt install -y python3 python3-venv python3-pip
python3 --version
```

## 3. 获取项目代码

首次部署：

```bash
cd /opt
sudo mkdir -p tradebusiness
sudo chown -R $USER:$USER /opt/tradebusiness
git clone <你的代码仓库地址> /opt/tradebusiness
cd /opt/tradebusiness
```

如果不是 Git 仓库，可以把当前项目目录上传到服务器 `/opt/tradebusiness`。

## 4. 后端生产环境参数

生产环境不要使用 `tradebusiness-backend/.env` 中的开发参数。

复制生产模板：

```bash
cd /opt/tradebusiness/tradebusiness-backend
cp .env.production.example .env.production
```

编辑参数：

```bash
nano .env.production
```

配置完成后执行上线前预检（不会输出密钥内容）：

```powershell
.\scripts\verify_production_env.ps1
```

完整发布检查（后端测试/规范、Compose、两端类型检查和构建）：

```powershell
.\release-check.ps1
```

必须修改以下值：

```env
ENVIRONMENT=production
DEBUG=false

MYSQL_ROOT_PASSWORD=替换为强密码
MYSQL_DATABASE=tradebusiness
MYSQL_USER=tradebusiness
MYSQL_PASSWORD=替换为强密码

SECRET_KEY=至少32位随机字符串
JWT_SECRET_KEY=另一个至少32位随机字符串
JWT_ALGORITHM=HS256

CORS_ORIGINS=https://admin.example.com,https://client.example.com

SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=你的SMTP账号
SMTP_PASSWORD=你的SMTP授权码或密码
SMTP_FROM=no-reply@example.com
SMTP_FROM_NAME=TradeBusiness
```

生成随机密钥示例：

```bash
openssl rand -hex 32
openssl rand -base64 48
```

注意：

- `ENVIRONMENT=production` 时，后端会拒绝默认密钥、短密钥、`DEBUG=true`、以及包含 `localhost` 的 `CORS_ORIGINS`。
- `SECRET_KEY` 和 `JWT_SECRET_KEY` 必须不同。
- SMTP 密码不要提交到代码仓库。

## 5. 安装和更新后端模块

### 5.1 Docker 部署推荐方式

Docker 镜像构建时会安装 `requirements.txt` 中的依赖。

首次构建：

```bash
cd /opt/tradebusiness/tradebusiness-backend
docker compose --env-file .env.production -f docker-compose.prod.yml build
```

依赖更新后重新构建：

```bash
cd /opt/tradebusiness/tradebusiness-backend
docker compose --env-file .env.production -f docker-compose.prod.yml build --no-cache backend celery-worker
```

### 5.2 非 Docker 本地虚拟环境方式

仅在你不用 Docker 跑后端时使用：

```bash
cd /opt/tradebusiness/tradebusiness-backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install black==26.5.1 isort pytest pytest-cov
```

更新依赖：

```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

## 6. 安装和更新前端模块

管理端：

```bash
cd /opt/tradebusiness/tradebusiness-admin
npm ci
```

客户端：

```bash
cd /opt/tradebusiness/tradebusiness-client
npm ci
```

更新前端模块：

```bash
cd /opt/tradebusiness/tradebusiness-admin
npm ci
npm outdated
npm update

cd /opt/tradebusiness/tradebusiness-client
npm ci
npm outdated
npm update
```

说明：

- 生产构建优先使用 `npm ci`，它会严格按照 `package-lock.json` 安装。
- 如果你修改了依赖版本，先在开发环境测试，再提交新的 `package-lock.json`。

## 7. 前端生产参数

两个前端都有 `.env.production`。

管理端：

```bash
cd /opt/tradebusiness/tradebusiness-admin
nano .env.production
```

客户端：

```bash
cd /opt/tradebusiness/tradebusiness-client
nano .env.production
```

推荐同域反向代理配置：

```env
VITE_APP_TITLE=货运代理业务管理系统
VITE_APP_BASE_API=
VITE_APP_WS_URL=
```

含义：

- `VITE_APP_BASE_API=` 为空时，前端请求 `/api/...`，由 Nginx 反向代理到后端。
- `VITE_APP_WS_URL=` 为空时，前端自动使用当前域名生成 `ws://` 或 `wss://`。

如果 API 使用独立域名，可设置：

```env
VITE_APP_BASE_API=https://api.example.com
VITE_APP_WS_URL=wss://api.example.com
```

同时后端 `CORS_ORIGINS` 必须包含前端域名。

## 8. 构建前端

管理端：

```bash
cd /opt/tradebusiness/tradebusiness-admin
npm ci
npm run type-check
npm run build
```

客户端：

```bash
cd /opt/tradebusiness/tradebusiness-client
npm ci
npm run type-check
npm run build
```

构建完成后会生成：

- `tradebusiness-admin/dist/`
- `tradebusiness-client/dist/`

## 9. 启动后端服务

使用生产 Docker Compose：

```bash
cd /opt/tradebusiness/tradebusiness-backend
docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build
```

查看状态：

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml ps
```

查看日志：

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml logs -f backend
docker compose --env-file .env.production -f docker-compose.prod.yml logs -f celery-worker
```

停止服务：

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml down
```

重启服务：

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml restart backend celery-worker
```

## 10. 配置 Nginx

项目已提供可复制的配置模板：

完整 HTTPS 执行步骤见 `deploy/nginx/README.md`。

```bash
sudo mkdir -p /etc/nginx/sites-available
sudo cp /opt/tradebusiness/deploy/nginx/tradebusiness.conf.example \
  /etc/nginx/sites-available/tradebusiness.conf
```

复制前可执行模板预检：

```powershell
.\scripts\verify_nginx_template.ps1
```

请先替换域名、静态文件路径和证书路径，再执行下列配置步骤。

创建管理端站点：

```bash
sudo nano /etc/nginx/sites-available/tradebusiness-admin.conf
```

示例：

```nginx
server {
    listen 80;
    server_name admin.example.com;

    root /opt/tradebusiness/tradebusiness-admin/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /uploads/ {
        proxy_pass http://127.0.0.1:8000/uploads/;
        proxy_set_header Host $host;
    }
}
```

创建客户端站点：

```bash
sudo nano /etc/nginx/sites-available/tradebusiness-client.conf
```

示例：

```nginx
server {
    listen 80;
    server_name client.example.com;

    root /opt/tradebusiness/tradebusiness-client/dist;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/v1/notifications/ws/ {
        proxy_pass http://127.0.0.1:8000/api/v1/notifications/ws/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 3600s;
    }

    location /uploads/ {
        proxy_pass http://127.0.0.1:8000/uploads/;
        proxy_set_header Host $host;
    }
}
```

启用站点：

```bash
sudo ln -s /etc/nginx/sites-available/tradebusiness-admin.conf /etc/nginx/sites-enabled/
sudo ln -s /etc/nginx/sites-available/tradebusiness-client.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 11. 配置 HTTPS

安装 Certbot：

```bash
sudo apt install -y certbot python3-certbot-nginx
```

申请证书：

```bash
sudo certbot --nginx -d admin.example.com -d client.example.com
```

检查自动续期：

```bash
sudo certbot renew --dry-run
```

## 12. 数据库初始化和迁移

当前项目没有标准 Alembic migration 目录时，可以使用项目脚本初始化表结构。先确认脚本内容和目标数据库，再执行：

```bash
cd /opt/tradebusiness/tradebusiness-backend
docker compose --env-file .env.production -f docker-compose.prod.yml exec backend python scripts/init_db.py
```

如果后续引入 Alembic，建议改为：

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml exec backend alembic upgrade head
```

## 13. 上线前检查

后端检查：

```bash
cd /opt/tradebusiness/tradebusiness-backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install black==26.5.1 isort pytest pytest-cov
pytest
black --check app tests
isort --check-only app tests
```

前端检查：

```bash
cd /opt/tradebusiness/tradebusiness-admin
npm ci
npm run type-check
npm run build

cd /opt/tradebusiness/tradebusiness-client
npm ci
npm run type-check
npm run build
```

生产环境检查：

```bash
curl -i https://admin.example.com/
curl -i https://client.example.com/
curl -i https://admin.example.com/api/health
```

浏览器检查：

- 能打开管理端登录页。
- 能打开客户端登录页。
- 登录接口不报 CORS 错误。
- WebSocket 通知连接状态正常。
- 上传文件路径 `/uploads/` 可访问受控资源。

## 14. 日常更新发布流程

进入项目目录：

```bash
cd /opt/tradebusiness
```

拉取最新代码：

```bash
git pull
```

更新后端依赖并重建：

```bash
cd /opt/tradebusiness/tradebusiness-backend
docker compose --env-file .env.production -f docker-compose.prod.yml build backend celery-worker
docker compose --env-file .env.production -f docker-compose.prod.yml up -d backend celery-worker
```

更新前端依赖并重新构建：

```bash
cd /opt/tradebusiness/tradebusiness-admin
npm ci
npm run build

cd /opt/tradebusiness/tradebusiness-client
npm ci
npm run build

sudo nginx -t
sudo systemctl reload nginx
```

检查日志：

```bash
cd /opt/tradebusiness/tradebusiness-backend
docker compose --env-file .env.production -f docker-compose.prod.yml logs --tail=100 backend
```

## 15. 回滚流程

如果使用 Git：

```bash
cd /opt/tradebusiness
git log --oneline -5
git checkout <上一个稳定commit>
```

重新构建并启动：

```bash
cd /opt/tradebusiness/tradebusiness-backend
docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build

cd /opt/tradebusiness/tradebusiness-admin
npm ci
npm run build

cd /opt/tradebusiness/tradebusiness-client
npm ci
npm run build

sudo systemctl reload nginx
```

数据库变更回滚需要单独评估，不要直接删除生产数据。

## 16. 常见问题

### 后端启动时报 SECRET_KEY 错误

说明生产环境仍在使用默认密钥或密钥太短。修改 `.env.production`：

```env
SECRET_KEY=至少32位随机字符串
JWT_SECRET_KEY=另一个至少32位随机字符串
```

### 浏览器报 CORS 错误

检查后端 `.env.production`：

```env
CORS_ORIGINS=https://admin.example.com,https://client.example.com
```

修改后重启后端：

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml restart backend
```

### WebSocket 连接失败

确认 Nginx 有 WebSocket 代理配置：

```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

### 前端请求打到错误地址

如果使用同域反代，`.env.production` 保持：

```env
VITE_APP_BASE_API=
VITE_APP_WS_URL=
```

如果使用独立 API 域名，填写完整地址并重新构建前端。

### 修改环境变量后没有生效

后端需要重启：

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml restart backend celery-worker
```

前端环境变量在构建时写入，修改后必须重新构建：

```bash
npm run build
```

## 17. 清理和维护

清理 Docker 构建缓存：

```bash
docker builder prune
```

清理未使用镜像：

```bash
docker image prune
```

备份数据库：

```bash
docker exec tradebusiness-mysql-prod mysqldump -u root -p tradebusiness > tradebusiness-$(date +%F).sql
```

恢复数据库前请先停写入服务并确认备份文件正确。

## 18. Celery 异步任务检查

生产环境必须同时运行 `celery-worker` 和 `celery-beat`。worker 负责执行获客、邮件和跟进任务，beat 负责定时投递任务。

启动或更新服务：

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml up -d --build backend celery-worker celery-beat
```

检查容器状态：

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml ps
docker compose --env-file .env.production -f docker-compose.prod.yml logs --tail=100 celery-worker
docker compose --env-file .env.production -f docker-compose.prod.yml logs --tail=100 celery-beat
```

日志中应能看到 worker 注册 `run-lead-search`、`send-due-lead-followups` 等任务。若出现 `Received unregistered task`，确认 worker 使用的启动命令为：

```bash
celery -A app.tasks.automation_tasks:celery_app worker --loglevel=info
```

## 19. Stripe Webhook 检查

Stripe Dashboard 中将 Webhook 地址配置为：

```text
https://你的 API 域名/api/v1/billing/webhooks/stripe
```

至少订阅 `checkout.session.completed` 事件，并将签名密钥写入生产环境：

```env
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...
STRIPE_SUCCESS_URL=https://admin.example.com/settings/plans?success=1
STRIPE_CANCEL_URL=https://admin.example.com/settings/plans?cancelled=1
STRIPE_CURRENCY=usd
```

修改后重启后端：

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml restart backend
```

不要使用开发环境的 `/api/v1/billing/orders/{order_id}/callback` 作为生产支付回调；生产环境该接口会主动返回 `410`。

## 20. AI Provider 配置

### Redis 与 Celery 生产参数

在 `.env.production` 中至少配置：

```env
REDIS_PASSWORD=请替换为随机长密码
CELERY_CONCURRENCY=4
```

生产 Compose 会自动将 Redis 密码注入 Redis 服务、后端和 Celery Worker/Beat，Worker 使用 `CELERY_CONCURRENCY` 限制并发数。

系统默认使用本地规则版生成，适合开发和无外部 API Key 的环境：

```env
AI_PROVIDER=rules
```

生产环境启用 OpenAI-compatible Provider：

```env
AI_PROVIDER=openai_compatible
AI_API_KEY=你的模型 API Key
AI_BASE_URL=https://api.openai.com/v1
AI_MODEL=gpt-4o-mini
AI_TIMEOUT_SECONDS=45
AI_MAX_RETRIES=2
AI_RETRY_BACKOFF_SECONDS=0.5
```

AI 请求失败、超时或返回格式不正确时，系统会自动回退到规则版，不会让获客任务直接失败。API Key 只能放在后端环境变量中，不能写入管理端或客户端代码，也不要记录到日志。
## 数据库备份

在后端目录执行以下命令创建 SQL 备份，并自动清理 14 天前的备份：

```powershell
.\scripts\backup_database.ps1
```

自定义备份目录和保留天数：

```powershell
.\scripts\backup_database.ps1 -OutputDirectory .\backups -KeepDays 30
```

备份文件应复制到独立的对象存储或异机磁盘，不能只保存在 Docker 主机上。

## 日志与审计

系统会对通用日志中的 `password`、`api_key`、`access_token`、`refresh_token` 和 `Authorization` 字段自动脱敏。认证、获客触达、退订变更、支付订单和 Stripe 回调等关键操作会写入审计日志；审计日志只保留操作类型、用户、资源和非敏感元数据，不记录密码、Token、密钥或邮件正文。
