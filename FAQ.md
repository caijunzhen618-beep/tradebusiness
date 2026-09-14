# 货运代理业务管理系统 - 常见问题解答 (FAQ)

## 开发环境问题

### Q1: 后端启动失败，提示 "ModuleNotFoundError"
**A:** 确保已激活虚拟环境并安装依赖：
```bash
cd tradebusiness-backend
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### Q2: 数据库连接失败 "Access denied"
**A:** 检查 .env 文件中的数据库配置：
- 确认MySQL服务正在运行
- 检查用户名和密码是否正确
- 确认数据库名称存在

### Q3: 前端页面显示"白板"
**A:** 检查API配置：
- 确认后端服务已启动（http://localhost:8000）
- 检查 .env.development 中的 `VITE_APP_BASE_API`
- 应该是：`VITE_APP_BASE_API=http://localhost:8000/api/v1`

## 功能使用问题

### Q4: 点击"我的客户"等菜单报错 "does not provide an export named"
**A:** 这是图标导入错误，已修复。如果仍出现：
```bash
# 清理缓存并重启
cd tradebusiness-client
rm -rf node_modules/.vite
npm run dev
```

### Q5: 导航失败 "No match found for location"
**A:** 路由配置问题，已修复。确保：
- 使用路由名称而不是路径
- 刷新浏览器（Ctrl+Shift+R）

### Q6: 登录失败 "Request failed with status code 422"
**A:** 后端API已修复，使用JSON格式登录。确保：
- 前端使用正确的登录API
- 后端服务正常运行

## 邮件发送问题

### Q7: 邮件发送失败 "Authentication unsuccessful"
**A:** SMTP认证问题，需要：

**Outlook邮箱：**
1. 开启两步验证：https://account.microsoft.com/security
2. 生成应用专用密码
3. 更新 .env：`SMTP_PASSWORD=应用专用密码`

**QQ邮箱：**
1. 登录QQ邮箱网页版
2. 设置 → 账户 → POP3/SMTP服务
3. 开启服务并生成授权码
4. 配置：
```bash
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_USER=your@qq.com
SMTP_PASSWORD=授权码
```

**163邮箱：**
```bash
SMTP_HOST=smtp.163.com
SMTP_PORT=465
SMTP_USER=your@163.com
SMTP_PASSWORD=授权码
```

### Q8: 点击邮件按钮报错404
**A:** 邮件API未加载，需要重启后端服务器：
```bash
# 停止后端（Ctrl+C）
cd tradebusiness-backend
python -m app.main
```

## 数据库问题

### Q9: 数据库表不存在错误
**A:** 运行数据库初始化脚本：
```bash
cd tradebusiness-backend
python scripts/init_db.py
```

或使用SQL：
```bash
mysql -u root -p < scripts/create_tables.sql
```

### Q10: 密码登录失败
**A:** 使用默认账户：
- 管理员：admin / Admin123
- 销售员：sales01 / Sales123

如需重置密码，运行：
```bash
python -c "
import bcrypt
password = '新密码'
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
print(f'Hashed password: {hashed}')
"
```

## 前端构建问题

### Q11: npm install 报错 "package not found"
**A:** 修复依赖版本：
```bash
cd tradebusiness-admin
# 修改 package.json 中的 vue3-leaflet 版本为 @vue-leaflet/vue-leaflet
npm install
```

### Q12: Vite构建错误 "Search string not found"
**A:** vue-tsc版本兼容问题，可以：
```bash
npm install vue-tsc@latest
# 或跳过类型检查
npm run build -- --skipLibCheck
```

## 性能优化问题

### Q13: 页面加载慢
**A:** 优化建议：
- 使用生产构建：`npm run build`
- 启用后端分页
- 优化数据库索引
- 配置CDN（生产环境）

### Q14: API响应慢
**A:** 检查：
- 数据库查询是否有索引
- 是否使用了 N+1 查询
- 网络延迟
- 启用缓存（Redis）

## 部署问题

### Q15: 生产环境配置
**A:** 注意事项：
- 修改 SECRET_KEY 和 JWT_SECRET_KEY
- 设置 DEBUG=false
- 配置正确的 CORS_ORIGINS
- 使用HTTPS
- 配置防火墙

### Q16: 端口冲突
**A:** 修改端口配置：

**后端** (.env):
```bash
PORT=8001  # 改为其他端口
```

**前端** (.env.development):
```bash
VITE_APP_BASE_API=http://localhost:8001/api/v1
```

## 日志和调试

### Q17: 如何查看错误日志
**A:** 检查日志文件：
```bash
# 后端日志
tail -f tradebusiness-backend/logs/app.log

# 实时跟踪
tail -f tradebusiness-backend/logs/app.log | grep ERROR
```

### Q18: 如何重置数据库
**A:** 完全重置：
```bash
# 删除数据库
mysql -u root -p -e "DROP DATABASE IF EXISTS tradebusiness;"

# 重新创建
mysql -u root -p < tradebusiness-backend/scripts/create_tables.sql
```

## 获取帮助

- 📖 查看文档：README.md
- 🔧 故障排除：TROUBLESHOOTING.md
- 📝 开发规范：CLAUDE.md
- 💾 数据库说明：scripts/README.md

## 更新日志

- 2026-04-03: 添加路由、图标导入、邮件发送等问题
- 2026-04-03: 创建FAQ文档
