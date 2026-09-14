# 数据库初始化说明

## 快速开始

### 方式一：使用SQL脚本（推荐）

```bash
# 1. 创建数据库并导入表结构
mysql -u root -p < scripts/create_tables.sql

# 2. 验证
mysql -u root -p tradebusiness -e "SHOW TABLES;"
```

### 方式二：使用Python脚本

```bash
# 1. 确保.env文件配置正确
cd tradebusiness-backend

# 2. 运行初始化脚本
python scripts/init_db.py
```

## 数据库表结构

系统包含以下6个核心表：

### 1. users - 用户表
- 存储管理员和业务员账户
- 支持角色：admin, sales
- 包含员工信息（部门、入职日期等）

### 2. customers - 客户表
- 货运代理公司的完整信息
- 支持多语言公司名称
- 包含业务信息（航线、货量等）
- 联系方式（电话、WhatsApp、邮箱等）

### 3. email_templates - 邮件模板表
- 支持Jinja2模板语法
- 多语言支持
- 模板分类（介绍、跟进、问候等）

### 4. emails - 邮件记录表
- 跟踪所有发送和接收的邮件
- 支持邮件状态跟踪（发送、打开、回复等）
- 关联客户和模板

### 5. tasks - 任务表
- 任务管理（跟进、邮件、会议等）
- 任务分配和状态跟踪
- 支持提醒功能

### 6. holidays - 节假日表
- 全球节假日数据
- 支持多国家
- 用于自动化问候功能

## 默认账户

系统预置2个账户：

| 用户名 | 密码 | 角色 | 邮箱 |
|--------|------|------|------|
| admin | Admin123 | 管理员 | admin@tradebusiness.com |
| sales01 | Sales123 | 销售员 | sales01@tradebusiness.com |

⚠️ **重要**：生产环境请立即修改默认密码！

## 数据库要求

- **MySQL版本**：8.0+
- **字符集**：utf8mb4
- **排序规则**：utf8mb4_unicode_ci
- **引擎**：InnoDB

## 备份与恢复

### 备份
```bash
mysqldump -u root -p tradebusiness > backup_$(date +%Y%m%d).sql
```

### 恢复
```bash
mysql -u root -p tradebusiness < backup_20260403.sql
```

## 常见问题

### Q: 如何重置数据库？
```bash
mysql -u root -p -e "DROP DATABASE IF EXISTS tradebusiness;"
mysql -u root -p < scripts/create_tables.sql
```

### Q: 如何添加新用户？
使用管理端用户管理功能或直接插入：
```sql
INSERT INTO users (id, username, email, hashed_password, full_name, role)
VALUES (UUID(), 'newuser', 'user@example.com', '$2b$12$...', 'User Name', 'sales');
```

### Q: 密码如何加密？
使用bcrypt，Python示例：
```python
import bcrypt
password = "your_password"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
```

## 技术支持

如有问题，请查看：
- 项目文档：CLAUDE.md
- 故障排除：TROUBLESHOOTING.md
- 数据库设计：DATABASE_SCHEMA.md
