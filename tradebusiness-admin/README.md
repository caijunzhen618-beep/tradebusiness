# 货运代理业务管理系统 - 管理端

基于 Vue 3 + TypeScript + Element Plus 的管理端应用。

## 技术栈

- **框架**: Vue 3 (Composition API)
- **语言**: TypeScript
- **构建工具**: Vite
- **UI 库**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP 客户端**: Axios
- **图表**: ECharts
- **地图**: Leaflet

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

访问 http://localhost:3000

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

## 开发指南

### 代码规范

```bash
# 格式化代码
npm run format

# 检查代码
npm run lint
```

### 默认账号

- 管理员: `admin` / `Admin123`
- 业务员: `sales01` / `Sales123`
