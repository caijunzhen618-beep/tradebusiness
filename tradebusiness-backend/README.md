# 货运代理业务管理系统 - 后端

基于 FastAPI 的货运代理业务管理系统后端服务。

## 技术栈

- **框架**: FastAPI 0.104+
- **Python**: 3.11+
- **数据库**: MySQL 8.0+ (async)
- **缓存**: Redis 7+
- **任务队列**: Celery 5+
- **ORM**: SQLAlchemy 2.0 (async)
- **数据验证**: Pydantic v2
- **认证**: JWT

## 快速开始

### 1. 安装依赖

```bash
# 使用 poetry
poetry install

# 或使用 pip
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库和其他服务
```

### 3. 初始化数据库

```bash
# 运行迁移
alembic upgrade head

# 或使用脚本初始化
python scripts/init_db.py
```

### 4. 启动服务

```bash
# 开发模式（自动重载）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 或使用 make
make dev
```

### 5. 启动 Celery Worker

```bash
# 终端1: Celery Worker
celery -A app.tasks.celery_app worker --loglevel=info

# 终端2: Celery Beat (定时任务)
celery -A app.tasks.celery_app beat --loglevel=info
```

### 6. 访问 API 文档

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
app/
├── api/              # API 路由层
├── core/             # 核心配置和工具
├── models/           # 数据库模型（ORM）
├── schemas/          # Pydantic 模式（请求/响应验证）
├── services/         # 业务逻辑层
├── repositories/     # 数据访问层
├── tasks/            # Celery 异步任务
├── scrapers/         # 爬虫模块
├── utils/            # 工具函数
└── db/               # 数据库配置和迁移
```

## 开发指南

### 代码规范

本项目遵循以下规范：

- **PEP 8**: Python 代码风格
- **Black**: 代码格式化
- **isort**: 导入排序
- **mypy**: 类型检查
- **pylint**: 代码质量检查

详细规范请参考 `CLAUDE.md` 文件。

### 代码格式化

```bash
# 格式化代码
black app/ tests/
isort app/ tests/

# 类型检查
mypy app/

# 代码检查
pylint app/
flake8 app/
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integration/

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

## API 概览

### 认证相关
- `POST /api/v1/auth/register` - 用户注册
- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/refresh` - 刷新 Token

### 用户管理
- `GET /api/v1/users` - 用户列表
- `GET /api/v1/users/{id}` - 用户详情
- `POST /api/v1/users` - 创建用户
- `PUT /api/v1/users/{id}` - 更新用户

### 客户管理
- `GET /api/v1/customers` - 客户列表
- `GET /api/v1/customers/{id}` - 客户详情
- `POST /api/v1/customers` - 创建客户
- `PUT /api/v1/customers/{id}` - 更新客户
- `POST /api/v1/customers/batch` - 批量导入

### 邮件管理
- `POST /api/v1/emails/send` - 发送邮件
- `POST /api/v1/emails/batch-send` - 批量发送
- `GET /api/v1/emails` - 邮件列表

### 数据采集
- `POST /api/v1/scraping/tasks` - 创建采集任务
- `GET /api/v1/scraping/tasks` - 任务列表
- `POST /api/v1/scraping/tasks/{id}/start` - 启动任务

## 部署

### Docker 部署

```bash
# 构建镜像
docker build -t tradebusiness-backend .

# 运行容器
docker run -p 8000:8000 --env-file .env tradebusiness-backend
```

### Docker Compose

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

## 生产环境检查清单

- [ ] 修改 `SECRET_KEY` 和 `JWT_SECRET_KEY`
- [ ] 设置 `DEBUG=false`
- [ ] 配置生产数据库
- [ ] 配置 HTTPS
- [ ] 配置邮件服务
- [ ] 配置文件存储（MinIO 或 OSS）
- [ ] 配置反向代理（Nginx）
- [ ] 配置日志收集
- [ ] 配置监控和告警
- [ ] 定期数据库备份

## 许可证

MIT License

## 联系方式

- 项目主页: [GitHub](https://github.com/yourorg/tradebusiness)
- 问题反馈: [Issues](https://github.com/yourorg/tradebusiness/issues)
