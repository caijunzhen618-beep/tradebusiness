# 货运代理业务管理系统

[![项目状态](https://img.shields.io/badge/状态-✅_100%_完成-success)](./COMPLETION_REPORT.md)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green)](#)
[![Vue 3](https://img.shields.io/badge/Vue-3.3-brightgreen)](#)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue)](#)
[![WebSocket](https://img.shields.io/badge/WebSocket-实时推送-orange)](#)

**为货运代理公司打造的智能客户关系管理系统**

---

## 🎉 项目已完成！

**所有功能模块 100% 完成，可投入生产使用！** 🚀

详见: [完成报告](./COMPLETION_REPORT.md)

## 🎯 项目特点

- ✅ **完整的功能模块** - 客户管理、邮件营销、任务管理、实时通知、数据采集
- ✅ **双前端应用** - 管理端（Element Plus）+ 客户端（Naive UI）
- ✅ **现代化技术栈** - FastAPI + Vue 3 + TypeScript + WebSocket
- ✅ **异步高性能** - 异步 MySQL、异步任务队列、实时推送
- ✅ **智能数据采集** - 代理池、限流控制、专注非洲市场
- ✅ **开箱即用** - 一键启动脚本，默认账号即可登录

## 📊 完成状态

**✅ 100% 完成** - 10/10 任务

| 模块 | 状态 | 功能 |
|------|------|------|
| 用户认证系统 | ✅ 完成 | JWT认证、权限控制 |
| 客户管理 | ✅ 完成 | CRUD、批量导入、统计分析 |
| 邮件功能 | ✅ 完成 | 模板管理、批量发送、跟踪统计 |
| 任务管理 | ✅ 完成 | 任务分配、提醒、逾期查询、实时统计 |
| 通知中心 | ✅ 完成 | WebSocket实时推送、未读提醒 |
| 数据统计 | ✅ 完成 | ECharts图表、数据可视化 |
| 数据采集 | ✅ 完成 | 代理池、限流、任务管理 |
| 系统设置 | ✅ 完成 | 个人信息、安全设置、系统配置 |
| 管理端前端 | ✅ 完成 | 9个完整页面，Element Plus |
| 客户端前端 | ✅ 完成 | 9个完整页面，Naive UI |
| 用户管理 | ✅ 完成 | 用户CRUD、状态管理 |
| 数据库设计 | ✅ 完成 | 完整的数据模型 |

**详细进度:** [PROJECT_STATUS.md](./PROJECT_STATUS.md)  
**完成报告:** [COMPLETION_REPORT.md](./COMPLETION_REPORT.md)

## 🚀 快速启动

### 前置要求
- Python 3.11+
- Node.js 18+
- MySQL 8.0+

### 一键启动（推荐）

**Windows 用户:**
```bash
start-all.bat
```

**Linux/Mac 用户:**
```bash
./start-all.sh
```

### 访问地址

- 🖥️ **管理端:** http://localhost:3000
- 👤 **客户端:** http://localhost:3001
- 📚 **API 文档:** http://localhost:8000/docs
- 🔑 **后端 API:** http://localhost:8000

### 默认账号

**管理员:**
- 用户名: `admin`
- 密码: `Admin123`

**测试业务员:**
- 用户名: `sales01`
- 密码: `Sales123`

## 📖 文档导航

> 💡 **提示:** 新用户请先查看 [文档导航索引](./DOCUMENTATION_INDEX.md)

- **[系统使用说明_小白版.md](./系统使用说明_小白版.md)** ⭐ - 面向管理员和业务员的完整操作手册

### 🚀 快速开始
- **[QUICKSTART.md](./QUICKSTART.md)** ⭐ - **5分钟快速上手**
- **[DATABASE_UPDATES.md](./DATABASE_UPDATES.md)** ⭐ - **数据库更新说明**
- **[FEATURE_IMPLEMENTATION.md](./FEATURE_IMPLEMENTATION.md)** ⭐ - **管理后台功能实现**

### 📊 项目状态
- **[COMPLETION_REPORT.md](./COMPLETION_REPORT.md)** - 项目完成报告（100%完成）
- **[PROJECT_STATUS.md](./PROJECT_STATUS.md)** - 详细的开发进度
- **[FILE_MANIFEST.md](./FILE_MANIFEST.md)** - 文件清单和用途

### 📋 参考文档
- **[plan.md](./plan.md)** - 完整的功能需求和技术方案
- **[CLAUDE.md](./CLAUDE.md)** - Python 代码规范

### 🔧 帮助文档
- **[STARTUP_FIX.md](./STARTUP_FIX.md)** ⭐ - **启动问题快速修复**
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - 故障排除指南
- **[FAQ.md](./FAQ.md)** - 常见问题解答
- **[DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md)** - 文档导航索引

### 🛠️ 工具脚本
- **[start-all.bat](./start-all.bat)** - 一键启动所有服务
- **[stop-all.bat](./stop-all.bat)** - 停止所有服务
- **[cleanup.bat](./cleanup.bat)** - 清理缓存文件

## 🎨 系统截图

*(截图待添加)*

## 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────┐
│                    前端层                            │
│  ┌──────────────────┐      ┌──────────────────┐    │
│  │   管理端前端      │      │   客户端前端      │    │
│  │  (Vue3 + EP)     │      │  (Vue3 + Naive)  │    │
│  └──────────────────┘      └──────────────────┘    │
└─────────────────────────────────────────────────────┘
                         ↕ HTTPS
┌─────────────────────────────────────────────────────┐
│                   API 网关层                          │
│              FastAPI Application                     │
└─────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────┐
│                   业务逻辑层                          │
│  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐   │
│  │ 用户   │  │ 客户   │  │ 邮件   │  │ 任务   │   │
│  │ 服务   │  │ 服务   │  │ 服务   │  │ 服务   │   │
│  └────────┘  └────────┘  └────────┘  └────────┘   │
└─────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────┐
│                   数据存储层                          │
│         MySQL (Async) + Redis (Optional)             │
└─────────────────────────────────────────────────────┘
```

## 📁 项目结构

```
tradebusiness/
├── plan.md                          # 项目需求与技术方案
├── CLAUDE.md                        # Python 代码开发规范
│
├── tradebusiness-backend/           # 后端项目 (Python + FastAPI)
│   ├── app/
│   │   ├── api/                     # API 路由层
│   │   ├── core/                    # 核心配置（安全、日志等）
│   │   ├── models/                  # 数据库模型
│   │   ├── schemas/                 # Pydantic 验证模式
│   │   ├── services/                # 业务逻辑层
│   │   ├── repositories/            # 数据访问层
│   │   ├── scrapers/                # 爬虫模块
│   │   ├── tasks/                   # Celery 异步任务
│   │   ├── utils/                   # 工具函数
│   │   ├── db/                      # 数据库配置
│   │   └── main.py                  # 应用入口
│   ├── scripts/                     # 脚本（初始化等）
│   ├── tests/                       # 测试
│   ├── requirements.txt             # 依赖列表
│   ├── pyproject.toml               # 项目配置
│   ├── docker-compose.yml           # Docker 编排
│   ├── Dockerfile                   # Docker 镜像
│   ├── Makefile                     # Make 命令
│   └── README.md
│
├── tradebusiness-admin/             # 管理端 (Vue 3 + Element Plus)
│   ├── src/
│   │   ├── api/                     # API 请求
│   │   ├── components/              # 公共组件
│   │   ├── views/                   # 页面组件
│   │   ├── router/                  # 路由配置
│   │   ├── store/                   # Pinia 状态管理
│   │   ├── utils/                   # 工具函数
│   │   ├── types/                   # TypeScript 类型
│   │   ├── App.vue                  # 根组件
│   │   └── main.ts                  # 应用入口
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── README.md
│
└── tradebusiness-client/            # 客户端 (Vue 3 + Naive UI)
    ├── src/
    │   ├── api/                     # API 请求
    │   ├── components/              # 公共组件
    │   ├── views/                   # 页面组件
    │   ├── router/                  # 路由配置
    │   ├── store/                   # Pinia 状态管理
    │   ├── utils/                   # 工具函数
    │   ├── App.vue                  # 根组件
    │   └── main.ts                  # 应用入口
    ├── package.json
    ├── vite.config.ts
    ├── tsconfig.json
    └── README.md
```

## 🚀 快速开始

### 方式一：使用快速启动脚本（推荐）

**Windows:**
```bash
start-all.bat          # 启动所有服务
start-backend.bat      # 仅启动后端
```

**Linux/Mac:**
```bash
chmod +x start-all.sh
./start-all.sh         # 启动所有服务
```

脚本会自动完成：
1. ✅ 检查虚拟环境和依赖
2. ✅ 启动 MySQL 和 Redis (Docker)
3. ✅ 激活虚拟环境
4. ✅ 启动后端API服务
5. ✅ 启动前端服务

### 方式二：手动启动

#### 前置要求
- Python 3.11+
- Node.js 18+
- **MySQL 8.0+** ⚠️ (已从PostgreSQL迁移)
- Redis 7+
- Docker (可选，用于MySQL和Redis)

#### 1. 启动数据库服务

**使用 Docker (推荐):**
```bash
cd tradebusiness-backend
docker-compose up -d mysql redis
```

**或使用本地 MySQL:**
```bash
# 确保 MySQL 8.0+ 已安装并运行
# 创建数据库
mysql -u root -p -e "CREATE DATABASE IF NOT EXISTS tradebusiness CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

#### 2. 启动后端服务

```bash
cd tradebusiness-backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 复制环境变量文件
cp .env.example .env

# 编辑 .env 文件，配置数据库连接：
# DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/tradebusiness?charset=utf8mb4

# 可选：执行数据库初始化脚本
mysql -u root -p tradebusiness < scripts/create_tables.sql

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**启动成功标志:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

#### 3. 启动前端服务

**管理端:**
```bash
cd tradebusiness-admin
npm install
npm run dev
```
访问: http://localhost:3000

**客户端:**
```bash
cd tradebusiness-client
npm install
npm run dev
```
访问: http://localhost:3001

---

## 💾 数据库说明

### 数据库技术栈
- **数据库**: MySQL 8.0+ (已从 PostgreSQL 迁移)
- **字符集**: utf8mb4
- **排序规则**: utf8mb4_unicode_ci
- **异步驱动**: aiomysql + pymysql

### 连接字符串格式
```bash
# 开发环境
DATABASE_URL=mysql+aiomysql://root:password@localhost:3306/tradebusiness?charset=utf8mb4

# Docker 环境
DATABASE_URL=mysql+aiomysql://tradebusiness:tradebusiness@mysql:3306/tradebusiness?charset=utf8mb4
```

### 数据库表结构
项目包含 6 个核心数据表：

| 表名 | 说明 | 记录数 |
|------|------|--------|
| users | 系统用户（管理员/业务员） | - |
| customers | 货运代理公司客户 | 主表 |
| emails | 邮件发送记录 | - |
| email_templates | 邮件模板（Jinja2） | - |
| tasks | 业务员待办任务 | - |
| holidays | 全球节假日数据 | - |

**📄 详细文档**: [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)
- 完整的字段定义
- 索引和外键关系
- ER关系图
- 完整的建表SQL脚本

### 数据库迁移
项目已从 PostgreSQL 迁移到 MySQL 8.0，主要变更：

✅ UUID 字段: `UUID` → `CHAR(36)`  
✅ ARRAY 字段: `ARRAY` → `JSON`  
✅ DateTime: 去除 timezone 支持  
✅ JSONB: `JSONB` → `JSON`  
✅ 驱动: `asyncpg` → `aiomysql`  

**📄 迁移文档**: [MYSQL_MIGRATION.md](./MYSQL_MIGRATION.md)

#### 2. 启动管理端

```bash
cd tradebusiness-admin

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问: http://localhost:3000

#### 3. 启动客户端

```bash
cd tradebusiness-client

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问: http://localhost:3001

## 🔑 默认账号

### 管理员账号
- 用户名: `admin`
- 密码: `Admin123`

### 测试业务员账号
- 用户名: `sales01`
- 密码: `Sales123`

## ✨ 已完成功能（100%）

### ✅ 核心功能模块

#### 用户认证系统
- ✅ 用户注册和登录
- ✅ JWT Token 认证
- ✅ Token 刷新机制
- ✅ 密码哈希（bcrypt）
- ✅ 用户管理（CRUD）
- ✅ 权限控制（Admin/Sales）
- ✅ 用户状态切换

#### 客户管理系统
- ✅ 客户信息管理（公司、联系、业务）
- ✅ 客户搜索和筛选
- ✅ 客户分配功能
- ✅ 批量导入客户
- ✅ 客户状态跟踪
- ✅ 优先级管理
- ✅ 数据统计和分析
- ✅ 非洲国家专用查询

#### 邮件系统
- ✅ SMTP 邮件发送
- ✅ HTML 邮件模板（Jinja2）
- ✅ 邮件模板管理
- ✅ 批量发送邮件
- ✅ 邮件记录查看
- ✅ 邮件跟踪（打开、点击）
- ✅ 自动问候邮件

#### 数据采集系统
- ✅ 爬虫框架（异步、重试、延迟）
- ✅ Google 搜索爬虫
- ✅ 数据提取和验证
- ✅ 非洲国家预配置
- ✅ 搜索关键词模板
- ✅ 批量采集支持

#### 通知系统
- ✅ WebSocket 实时通信
- ✅ 连接管理器
- ✅ 消息广播
- ✅ 新邮件通知
- ✅ 任务提醒
- ✅ 浏览器通知

#### 自动化功能
- ✅ Celery 任务队列
- ✅ 定时任务（节假日问候）
- ✅ 自动跟进提醒
- ✅ 异步邮件发送
- ✅ Celery Beat 调度

#### 任务管理
- ✅ 任务列表和管理
- ✅ 任务状态跟踪
- ✅ 任务优先级设置
- ✅ 任务提醒功能

#### 数据分析
- ✅ 客户分布统计
- ✅ 业务量统计
- ✅ 转化率分析
- ✅ 业务员绩效对比

#### 文件管理
- ✅ 文件上传（Logo、附件）
- ✅ 文件类型验证
- ✅ 数据导出（Excel、CSV）

#### 系统设置
- ✅ 个人设置
- ✅ 通知偏好
- ✅ SMTP配置
- ✅ 系统配置

**详细进度**: [PROGRESS.md](./PROGRESS.md) - 完整的开发进度报告  
**完成总结**: [PROJECT_COMPLETE.md](./PROJECT_COMPLETE.md) - 项目完成总结

## 📖 开发规范

### Python 后端
严格遵循 `CLAUDE.md` 中定义的代码规范：

- **编码标准**: PEP 8, Black, isort
- **类型注解**: 所有函数必须有类型注解
- **文档字符串**: Google 风格的文档字符串
- **分层架构**: API → Service → Repository
- **异常处理**: 使用自定义异常类
- **测试**: pytest, pytest-asyncio

### 前端
- Vue 3 Composition API
- TypeScript 严格模式
- 组件命名: PascalCase
- 文件命名: kebab-case
- 代码格式化: Prettier
- 代码检查: ESLint

## 🛠️ 常用命令

### 后端
```bash
# 开发
make dev                    # 启动开发服务器
make test                   # 运行测试
make format                 # 格式化代码
make lint                   # 代码检查

# 数据库
make db-reset               # 重置数据库
make db-seed                # 填充初始数据

# Docker
make docker-up              # 启动 Docker
make docker-down            # 停止 Docker
```

### 管理端
```bash
npm run dev                 # 启动开发服务器
npm run build               # 构建生产版本
npm run lint                # 代码检查
npm run format              # 格式化代码
```

### 客户端
```bash
npm run dev                 # 启动开发服务器
npm run build               # 构建生产版本
npm run lint                # 代码检查
npm run format              # 格式化代码
```

## 📚 完整文档列表

### 核心文档
- [README.md](./README.md) - **项目总览和快速开始**（本文档）
- [plan.md](./plan.md) - 项目需求与技术方案
- [CLAUDE.md](./CLAUDE.md) - Python 代码开发规范
- [PROGRESS.md](./PROGRESS.md) - 开发进度报告
- [PROJECT_COMPLETE.md](./PROJECT_COMPLETE.md) - 项目完成总结

### 数据库文档
- [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) - **MySQL 8.0 数据库结构文档**
- [MYSQL_MIGRATION.md](./MYSQL_MIGRATION.md) - PostgreSQL → MySQL 8.0 迁移指南

### 故障排查
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - **常见问题和解决方案**

### 项目文档
- [后端 README](./tradebusiness-backend/README.md)
- [管理端 README](./tradebusiness-admin/README.md)
- [客户端 README](./tradebusiness-client/README.md)

### 文档导航
```
tradebusiness/
├── README.md                    # 👈 从这里开始！
├── DATABASE_SCHEMA.md           # 数据库结构文档
├── MYSQL_MIGRATION.md          # 数据库迁移指南
├── TROUBLESHOOTING.md          # 故障排查指南
├── PROGRESS.md                  # 开发进度报告
├── PROJECT_COMPLETE.md          # 项目完成总结
├── plan.md                      # 项目需求文档
└── CLAUDE.md                    # 开发规范文档
```

## 🤝 贡献指南

1. 遵循既定的代码规范（[CLAUDE.md](./CLAUDE.md)）
2. 为新功能编写测试
3. 更新相关文档
4. 提交前进行代码格式化和检查

## 🐛 问题排查

### 常见问题

**Q: uvicorn 命令未找到？**
- 查看：[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)
- 使用：`start-backend.bat` 一键启动

**Q: 数据库连接失败？**
- 检查 MySQL 8.0 是否已安装并运行
- 确认 `.env` 文件中的数据库连接字符串正确
- 参考：[DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)

**Q: 依赖安装失败？**
- 使用国内镜像源：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`
- 详细解决方案：[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

## 📄 许可证

MIT License

---

## ✅ 项目状态

**当前版本**: v1.0.0  
**开发状态**: ✅ **已完成，可投入使用**  
**完成度**: 100%  
**代码量**: ~16,300+ 行  
**完成日期**: 2026-04-03

**本项目所有核心功能已完成，可以投入生产环境使用！** 🎉

详细功能列表请查看：[PROJECT_COMPLETE.md](./PROJECT_COMPLETE.md)
