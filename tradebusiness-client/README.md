# 货运代理业务管理系统 - 客户端

基于 Vue 3 + TypeScript + Naive UI 的客户端应用（业务员使用）。

## 技术栈

- **框架**: Vue 3 (Composition API)
- **语言**: TypeScript
- **构建工具**: Vite
- **UI 库**: Naive UI
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP 客户端**: Axios
- **图表**: ECharts
- **图标**: Ionicons5

## 快速开始

### 1. 安装依赖

```bash
npm install
# 或
pnpm install
```

### 2. 配置环境变量

```bash
cp .env.development .env.local
# 编辑 .env.local 配置 API 地址
```

### 3. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3001

### 4. 构建生产版本

```bash
npm run build
```

## 项目结构

```
src/
├── api/              # API 请求
├── assets/           # 静态资源
├── components/       # 公共组件
├── composables/      # 组合式函数
├── router/           # 路由配置
├── store/            # 状态管理
├── types/            # TypeScript 类型定义
├── utils/            # 工具函数
├── views/            # 页面组件
└── main.ts           # 应用入口
```

## 功能模块

- **首页**: 展示个人工作概览
- **客户管理**: 我的客户列表、发现新客户、客户详情
- **邮件管理**: 收发邮件、邮件模板
- **消息中心**: 实时消息通知
- **任务管理**: 任务列表、日历视图
- **自动化**: 节假日问候、自动回复、自动跟进
- **个人中心**: 个人信息、设置

## 开发指南

### 代码规范

```bash
# 格式化代码
npm run format

# 检查代码
npm run lint
```

### 默认账号

- 业务员: `sales01` / `Sales123`
