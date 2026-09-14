# scripts 目录说明

本目录存放 TradeBusiness 货运代理业务管理系统的验证、诊断、测试和数据库辅助脚本。

## 一、验证脚本

### verify_auth_fix.py

**用途：** 全面验证 Authorization 请求头修复是否生效。

**检查内容：**

- 后端健康检查
- 登录接口功能
- 携带 Authorization 请求头访问接口
- 通知接口（之前出现过问题的接口）
- 客户接口
- 前端环境配置

**使用方式：**

```bash
# Windows
cd ..
verify-auth-fix.bat

# Linux/Mac
./verify-auth-fix.sh

# 直接使用 Python 执行
python scripts/verify_auth_fix.py
```

**预期结果：** 重启前端服务后，所有检查项目都应显示 PASS。

---

## 二、诊断脚本

### diagnose_cors.py

**用途：** 全面诊断 CORS 跨域配置。

**检查内容：**

- 后端 CORS 设置
- 预检请求处理
- Origin 来源验证
- 请求头配置

**使用方式：**

```bash
python scripts/diagnose_cors.py
```

---

### test_cors.py

**用途：** 快速测试 CORS 跨域配置。

**检查内容：**

- 向 `/api/v1/health` 发送 OPTIONS 请求
- 检查响应中是否包含 CORS 请求头

**使用方式：**

```bash
python scripts/test_cors.py
```

---

## 三、数据库脚本

### verify_database.py

**用途：** 全面验证数据库状态。

**检查内容：**

- 数据库连接是否正常
- 所有必需数据表是否存在
- 数据表结构
- 数据记录数量
- 外键关联关系

**使用方式：**

```bash
python scripts/verify_database.py
```

**预期结果：** 7 个必需数据表都应存在。

---

### check_tables.py

**用途：** 快速检查数据表是否存在。

**使用方式：**

```bash
python scripts/check_tables.py
```

---

## 四、进程管理脚本

## 五、运行全部验证检查

如需完整验证系统，可以按以下顺序执行：

```bash
# 1. 验证数据库
python scripts/verify_database.py

# 2. 检查 CORS 配置
python scripts/diagnose_cors.py

# 3. 验证 Authorization 修复
python scripts/verify_auth_fix.py

# 或使用快捷脚本
verify-auth-fix.bat   # Windows
./verify-auth-fix.sh  # Linux/Mac
```

## 六、脚本运行要求

所有脚本通常需要：

- Python 3.7 或更高版本
- `requests` 库：`pip install requests`
- 后端服务已启动，地址为 `http://localhost:8000`
- 数据库检查脚本还需要正确配置 `tradebusiness-backend/.env`

建议在项目根目录运行，或者使用脚本中提供的完整路径。

## 七、常见问题

### 7.1 脚本无法连接后端

- 确认后端服务已经启动：

  ```bash
  cd tradebusiness-backend
  python -m uvicorn app.main:app --reload
  ```

- 检查 8000 端口是否被防火墙拦截。
- 检查 8000 端口是否被其他程序占用。
- 确认浏览器可以打开 `http://localhost:8000/docs`。

### 7.2 出现导入错误

安装脚本依赖：

```bash
pip install requests
```

如果电脑同时安装了多个 Python 版本，可以使用：

```bash
python3 -m pip install requests
python3 scripts/verify_auth_fix.py
```

### 7.3 Linux/Mac 提示 Permission denied

给 Shell 脚本增加执行权限：

```bash
chmod +x *.sh
```

如果系统没有 `python` 命令，请使用 `python3`。

## 八、脚本输出格式

所有脚本尽量使用统一的状态标识：

- `✓`：成功
- `✗`：失败
- `ℹ`：信息

示例：

```text
============================================================
1. Testing Backend Health
============================================================
✓ Backend is running: http://localhost:8000
ℹ Response: {"status": "healthy"}
```

## 九、新增脚本规范

新增脚本时，建议遵循以下模板：

```python
#!/usr/bin/env python3
"""
脚本名称 - 简短说明
"""

import requests
from typing import Any, Dict

# 配置
BASE_URL = "http://localhost:8000"


def test_something():
    """执行某项测试"""
    pass


def main():
    """运行全部测试"""
    print(f"\n{'=' * 60}")
    print("脚本名称".center(60))
    print(f"{'=' * 60}\n")
    # ... 测试逻辑 ...


if __name__ == "__main__":
    main()
```

新增脚本时请注意：

- 使用明确的文件名和函数名；
- 对外部服务连接失败给出清晰提示；
- 不要在日志中输出密码、Token、API Key 等敏感信息；
- 修改脚本后同步更新本 README。

---

**最后更新：** 2026-07-17
