# 货运代理业务管理系统 - 快速启动指南

## ✅ 系统状态

**最后更新:** 2026-04-04
**状态:** 🟢 所有服务正常运行

**最新修复:**
- ✅ 后端语法错误已修复
- ✅ 数据库初始化脚本已修复
- ✅ 所有启动脚本已验证可用

---

## ⚠️ 重要提示

**如果您之前使用过此系统，请注意更新：**

🆕 **新增功能（2026-04-04）:**
- ✅ 任务管理系统
- ✅ 实时通知系统（WebSocket）
- ✅ 数据采集框架

📝 **需要执行的操作：**

1. **更新依赖包**
   ```bash
   cd tradebusiness-backend
   pip install -r requirements.txt
   ```

2. **更新数据库**
   ```bash
   python scripts/init_db.py
   ```
   ⚠️ 注意：这会创建新的 `notifications` 表，不会删除现有数据

3. **更新前端环境变量**（新增WebSocket配置）
   ```bash
   # 在 .env.development 中确认有以下配置：
   VITE_APP_WS_URL=ws://localhost:8000
   ```

📚 **详细信息请查看:**
- [数据库更新说明](./DATABASE_UPDATES.md) - 新增表结构和配置
- [项目完成报告](./COMPLETION_REPORT.md) - 完整的功能列表

### 🆘 启动遇到问题？

**查看启动修复指南:**
- ⭐ **[STARTUP_FIX.md](./STARTUP_FIX.md)** - 启动问题快速修复（推荐）
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) - 完整故障排除指南

**常见问题:**
- Python虚拟环境创建失败
- pip install 失败
- 数据库连接失败
- npm install 失败
- 端口被占用

**快速解决方案:**
```bash
# 1. 使用单独启动脚本测试
start-backend.bat    # 单独启动后端
start-admin.bat     # 单独启动管理端
start-client.bat     # 单独启动客户端

# 2. 清理缓存后重试
cleanup.bat

# 3. 查看 STARTUP_FIX.md 详细步骤
```

---

## 📋 前置要求

### 必需软件
- **Python** 3.11+ 
- **Node.js** 18+ 
- **MySQL** 8.0+
- **Redis** (可选，用于高级功能)

### 检查安装
```bash
python --version  # 应该显示 Python 3.11+
node --version    # 应该显示 Node.js 18+
mysql --version   # 检查 MySQL 是否安装
```

## 🚀 快速启动（5分钟）

### 1️⃣ 启动后端服务

```bash
# 进入后端目录
cd tradebusiness-backend

# 安装依赖（首次运行）
pip install -r requirements.txt

# 初始化数据库
python scripts/init_db.py

# 启动后端服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**后端将启动在:** http://localhost:8000
**API文档:** http://localhost:8000/docs

### 2️⃣ 启动管理端前端

```bash
# 新开一个终端窗口

# 进入管理端目录
cd tradebusiness-admin

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev
```

**管理端将启动在:** http://localhost:3000

### 3️⃣ 启动客户端前端（可选）

```bash
# 新开另一个终端窗口

# 进入客户端目录
cd tradebusiness-client

# 安装依赖（首次运行）
npm install

# 启动开发服务器
npm run dev
```

**客户端将启动在:** http://localhost:3001

## 🔑 默认账号

### 管理员账号
- **用户名:** `admin`
- **密码:** `Admin123`

### 测试业务员账号
- **用户名:** `sales01`
- **密码:** `Sales123`

## 📊 首次登录流程

1. 访问 http://localhost:3000（管理端）或 http://localhost:3001（客户端）
2. 使用默认账号登录
3. 登录成功后，您可以：
   - **管理端**: 管理所有客户、用户、邮件等
   - **客户端**: 查看分配给自己的客户、发送邮件、管理任务

## 🗄️ 数据库配置

数据库连接配置在 `tradebusiness-backend/.env` 文件中：

```env
# MySQL 配置（根据您的实际情况修改）
DATABASE_URL=mysql+aiomysql://root:YOUR_PASSWORD@localhost:3306/tradebusiness?charset=utf8mb4
```

### 创建数据库（如果不存在）
```sql
CREATE DATABASE tradebusiness CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 📧 邮件配置（可选）

如需使用邮件功能，请在 `tradebusiness-backend/.env` 中配置SMTP：

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com
SMTP_FROM_NAME=TradeBusiness
```

## ⚠️ 常见问题

### 问题1: MySQL连接失败
**解决方案:**
1. 确认MySQL服务正在运行
2. 检查 `.env` 文件中的数据库密码
3. 确认数据库 `tradebusiness` 已创建

### 问题2: Python依赖安装失败
**解决方案:**
```bash
# 使用虚拟环境
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 然后重新安装依赖
pip install -r requirements.txt
```

### 问题3: 前端端口冲突
**解决方案:**

修改 `tradebusiness-admin/vite.config.ts`:
```typescript
export default defineConfig({
  server: {
    port: 3000  // 改为其他端口，如 3002
  }
})
```

## 📚 更多功能

### 启用Redis（用于缓存和任务队列）
```bash
# Windows: 下载并启动 Redis
# Linux:
sudo systemctl start redis

# Mac:
brew services start redis
```

### 启动Celery任务队列（用于异步任务）
```bash
# 在tradebusiness-backend目录下
celery -A app.tasks.celery_app worker --loglevel=info
```

## 🎯 下一步

1. ✅ 系统已启动
2. 📝 修改默认密码
3. 👥 添加新用户
4. 🏢 开始添加客户数据
5. 📧 配置邮件服务
6. 📊 查看数据统计

## 📖 完整文档

- 详细功能文档: [README.md](./README.md)
- 开发规范: [CLAUDE.md](./CLAUDE.md)
- 故障排除: [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)

---

**祝您使用愉快！** 🎉

如有问题，请查看故障排除文档或联系技术支持。
