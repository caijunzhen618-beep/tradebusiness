# AI B2B 获客平台开发步骤文档

本文档用于指导当前货运代理业务管理系统逐步升级为类似 Revor.ai 的 AI B2B 获客平台。开发顺序遵循“先跑通核心闭环，再做自动化，再做商业化”的原则。

## 1. 总体目标

在现有系统基础上新增一套 AI 获客能力，形成以下业务闭环：

```text
目标客户配置
  -> 潜客搜索
  -> 企业信息抓取
  -> AI 企业背调
  -> AI 开发信生成
  -> 线索入库
  -> 多渠道跟进
  -> 数据统计与计费
```

第一版不追求所有渠道自动化，优先保证用户能真实完成：

- 输入目标客户条件。
- 获得一批潜在客户。
- 查看企业背调报告。
- 生成开发信或 WhatsApp/LinkedIn 话术。
- 保存和跟进线索。

## 2. 技术原则

### 2.1 后端原则

- 使用 FastAPI 继续作为 API 服务。
- 保持 API -> Service -> Repository 分层。
- 搜索、抓取、AI 生成、邮件发送等耗时任务必须走 Celery 异步任务。
- 数据库访问统一放在 Repository 层。
- AI 调用统一封装，避免业务代码直接调用第三方 SDK。
- 所有新增公开接口必须有 Pydantic Schema。
- 涉及扣积分、发送消息、创建任务等操作必须记录流水。

### 2.2 前端原则

- 管理端优先新增“AI 获客”模块。
- 第一版以前端管理后台为主，客户端门户后续再扩展。
- 页面优先保证可用性和业务流程清晰，不做复杂营销页。
- 复杂任务使用状态流转展示，例如“等待中 / 搜索中 / 背调中 / 已完成 / 失败”。

### 2.3 合规原则

- 邮箱、WhatsApp、LinkedIn 等渠道必须遵守平台规则。
- LinkedIn 第一阶段只做“生成话术 + 人工执行任务”，不做违规自动登录和批量操作。
- 用户密钥、邮箱授权、渠道 token 必须加密保存。
- AI 生成内容必须允许人工确认后再发送。

## 3. 阶段一：MVP 核心闭环

### 3.1 阶段目标

实现最小可用版本：

```text
创建获客任务 -> 获取潜客 -> 企业背调 -> 生成开发信 -> 保存线索
```

### 3.2 后端开发任务

#### 3.2.1 新增数据模型

建议新增以下模型：

- `LeadSearchTask`：潜客搜索任务。
- `Lead`：潜客公司。
- `LeadContact`：联系人和联系方式。
- `CompanyResearchReport`：企业背调报告。
- `SalesCopy`：AI 生成的开发信和话术。

建议字段：

```text
lead_search_tasks
- id
- user_id
- name
- target_country
- target_industry
- product_keywords
- customer_profile
- exclude_keywords
- status
- total_found
- error_message
- created_at
- updated_at

leads
- id
- task_id
- company_name
- website
- country
- industry
- description
- source
- match_score
- status
- created_at
- updated_at

lead_contacts
- id
- lead_id
- name
- title
- email
- phone
- linkedin_url
- whatsapp
- source
- is_verified
- created_at
- updated_at

company_research_reports
- id
- lead_id
- summary
- business_model
- products
- target_markets
- buying_signals
- pain_points
- recommended_angle
- raw_sources
- created_at
- updated_at

sales_copies
- id
- lead_id
- channel
- language
- subject
- content
- tone
- status
- created_at
- updated_at
```

#### 3.2.2 新增后端模块

建议目录：

```text
tradebusiness-backend/app/
├── api/v1/endpoints/lead_generation.py
├── models/lead.py
├── schemas/lead.py
├── repositories/lead_repository.py
├── services/lead_search_service.py
├── services/company_research_service.py
├── services/sales_copy_service.py
├── services/ai_provider_service.py
└── tasks/lead_generation_tasks.py
```

#### 3.2.3 API 接口

第一版接口建议：

```text
POST   /api/v1/lead-generation/tasks
GET    /api/v1/lead-generation/tasks
GET    /api/v1/lead-generation/tasks/{task_id}
POST   /api/v1/lead-generation/tasks/{task_id}/run

GET    /api/v1/lead-generation/leads
GET    /api/v1/lead-generation/leads/{lead_id}
POST   /api/v1/lead-generation/leads
PATCH  /api/v1/lead-generation/leads/{lead_id}

POST   /api/v1/lead-generation/leads/{lead_id}/research
GET    /api/v1/lead-generation/leads/{lead_id}/research

POST   /api/v1/lead-generation/leads/{lead_id}/sales-copy
GET    /api/v1/lead-generation/leads/{lead_id}/sales-copies
```

#### 3.2.4 第一版搜索策略

为降低风险，第一版分两步实现：

1. 手动输入或导入公司官网。
2. 再接入真实搜索 API。

第一版支持：

- 单个官网输入。
- 批量粘贴官网列表。
- CSV 导入公司名称和官网。

后续接入：

- Bing Search API
- SerpAPI
- Tavily
- Exa
- Google Programmable Search

#### 3.2.5 企业背调逻辑

背调流程：

```text
读取 Lead
  -> 抓取官网首页和关键页面
  -> 提取文本
  -> 调用 AI 生成结构化报告
  -> 保存 CompanyResearchReport
```

需要抽象：

- `WebsiteCrawlerService`
- `CompanyResearchService`
- `AIProviderService`

AI 输出必须要求 JSON 结构，避免前端难以解析。

#### 3.2.6 开发信生成逻辑

输入：

- 当前用户公司资料。
- 目标客户背调报告。
- 渠道：email / whatsapp / linkedin。
- 语言：中文 / 英文。
- 语气：正式 / 简洁 / 友好 / 强销售。

输出：

- 邮件标题。
- 正文。
- 跟进话术。
- 推荐发送理由。

### 3.3 前端开发任务

#### 3.3.1 新增菜单

管理端新增一级菜单：

```text
AI 获客
```

子页面：

- 获客任务
- 潜客列表
- 企业背调
- 开发信生成

#### 3.3.2 页面一：获客任务

功能：

- 新建任务。
- 填写目标国家、行业、关键词、客户画像、排除关键词。
- 手动输入官网列表。
- 查看任务状态。
- 进入任务结果。

验收标准：

- 能创建任务。
- 能看到任务列表。
- 能查看任务详情。
- 能触发任务运行。

#### 3.3.3 页面二：潜客列表

功能：

- 按任务筛选潜客。
- 查看公司名称、官网、国家、行业、匹配分、状态。
- 支持手动新增潜客。
- 支持进入企业详情。

验收标准：

- 潜客可保存。
- 潜客可编辑状态。
- 潜客可进入详情页。

#### 3.3.4 页面三：企业背调

功能：

- 展示 AI 生成的企业报告。
- 展示公司简介、主营业务、潜在需求、痛点、推荐切入点。
- 支持重新生成。

验收标准：

- 点击“生成背调”后能得到报告。
- 报告保存后刷新页面仍可查看。

#### 3.3.5 页面四：开发信生成

功能：

- 选择渠道和语言。
- 点击生成开发信。
- 展示标题、正文、跟进话术。
- 支持复制内容。
- 支持保存多个版本。

验收标准：

- 能基于背调报告生成开发信。
- 能保存生成结果。
- 能复制内容。

## 4. 阶段二：销售智能体

### 4.1 阶段目标

让用户配置自己的销售智能体，使生成内容更贴合自身业务。

### 4.2 新增数据模型

- `SalesAgent`
- `AgentKnowledgeDocument`
- `AgentPromptTemplate`

建议字段：

```text
sales_agents
- id
- user_id
- name
- company_intro
- product_intro
- value_proposition
- target_customer
- tone
- forbidden_words
- default_language
- is_default
- created_at
- updated_at

agent_knowledge_documents
- id
- agent_id
- file_name
- file_url
- content_text
- embedding_status
- created_at
- updated_at
```

### 4.3 后端任务

- 新增智能体 CRUD。
- 新增资料上传和文本解析。
- 新增知识库检索。
- 开发信生成时引入智能体配置。
- 背调时根据智能体的目标客户进行匹配评分。

### 4.4 前端任务

新增页面：

- 智能体配置
- 产品资料
- 话术模板

验收标准：

- 用户能创建一个销售智能体。
- 用户能填写产品和客户资料。
- 生成开发信时能选择智能体。
- 同一个潜客使用不同智能体能生成不同话术。

## 5. 阶段三：多渠道触达

### 5.1 阶段目标

把“生成内容”升级为“执行跟进流程”。

### 5.2 数据模型

- `Campaign`
- `CampaignStep`
- `CampaignLead`
- `ChannelAccount`
- `MessageLog`
- `ReplyLog`

### 5.3 邮件渠道

优先实现邮箱，因为落地价值最高。

开发任务：

- SMTP 发信。
- Gmail OAuth。
- Outlook OAuth。
- 邮件发送记录。
- 邮件回复识别。
- 邮件序列任务。

验收标准：

- 用户能绑定邮箱。
- 用户能给单个潜客发送开发信。
- 系统能记录发送结果。
- 系统能按序列生成后续跟进任务。

### 5.4 WhatsApp 渠道

建议使用 WhatsApp Business Cloud API。

开发任务：

- 绑定 WhatsApp Business 配置。
- 保存模板消息。
- 发送合规模板消息。
- 记录消息状态。

### 5.5 LinkedIn 渠道

第一版只做半自动：

- 生成 LinkedIn 连接话术。
- 生成私信话术。
- 创建人工跟进任务。
- 用户手动复制和执行。

不建议第一版做自动登录和自动批量操作。

## 6. 阶段四：积分计费和商业化

### 6.1 阶段目标

支持 SaaS 化运营。

### 6.2 数据模型

- `SubscriptionPlan`
- `UserSubscription`
- `CreditWallet`
- `CreditTransaction`
- `PaymentOrder`

### 6.3 积分规则

建议初始规则：

```text
创建潜客：1 积分 / 条
企业背调：5 积分 / 次
开发信生成：2 积分 / 次
邮箱验证：1 积分 / 次
AI 深度报告：10 积分 / 次
```

### 6.4 支付渠道

国内优先：

- 支付宝
- 微信支付

海外扩展：

- Stripe

验收标准：

- 用户有积分余额。
- 每次 AI 或搜索操作都扣积分。
- 积分不足时阻止操作。
- 后台能查看积分流水。

## 7. 阶段五：数据看板和增长优化

### 7.1 阶段目标

帮助用户判断哪些市场、渠道、话术更有效。

### 7.2 指标

- 搜索任务数。
- 潜客总数。
- 有效潜客数。
- 背调完成数。
- 开发信生成数。
- 触达数。
- 回复数。
- 回复率。
- 国家维度表现。
- 行业维度表现。
- 渠道维度表现。

### 7.3 前端页面

新增：

- 获客仪表盘
- 渠道效果分析
- 国家和行业分析
- 智能体表现分析

## 8. 推荐开发顺序

### 8.1 第 1 周

- 建立 `LeadSearchTask`、`Lead`、`LeadContact` 模型。
- 完成数据库迁移。
- 完成后端 CRUD。
- 前端新增“AI 获客”菜单和获客任务页面。

### 8.2 第 2 周

- 完成手动输入官网和 CSV 导入。
- 完成潜客列表页。
- 完成潜客详情页。
- 接入基础网页抓取服务。

### 8.3 第 3 周

- 封装 AI Provider。
- 完成企业背调服务。
- 完成背调报告页面。
- 加入异步任务状态。

### 8.4 第 4 周

- 完成开发信生成服务。
- 完成开发信页面。
- 支持复制和保存多个版本。
- 完成 MVP 端到端测试。

### 8.5 第 5-6 周

- 新增销售智能体配置。
- 开发产品资料和话术模板。
- 生成内容时引入智能体上下文。
- 实现基础线索评分。

### 8.6 第 7-8 周

- 邮箱绑定。
- 单封邮件发送。
- 邮件发送记录。
- 邮件跟进任务。

### 8.7 第 9-10 周

- 积分钱包。
- 积分流水。
- 套餐配置。
- 支付订单预留接口。

## 9. MVP 验收清单

MVP 完成时必须满足：

- [x] 管理后台可以创建获客任务。
- [x] 可以手动输入或导入公司官网。
- [x] 系统可以保存潜客公司。
- [x] 系统可以抓取官网公开内容。
- [x] 系统可以生成企业背调报告。
- [x] 系统可以生成开发信。
- [x] 背调报告和开发信可以保存。
- [x] 页面刷新后数据不丢失。
- [x] 异步任务失败时能看到错误信息。
- [x] 后端 `pytest` 通过。
- [x] 后端 `black --check` 通过。
- [x] 后端 `isort --check-only` 通过。
- [x] 前端构建通过。

## 10. 生产上线前检查清单

- [x] 所有密钥放入环境变量。
- [x] 生产环境禁止 `DEBUG=True`。
- [x] CORS 不允许使用 `localhost`。
- [x] 数据库开启备份。
- [x] Redis 设置密码。
- [ ] Nginx 开启 HTTPS。
- [x] AI 调用设置超时和重试。
- [x] Celery worker 设置并发限制。
- [x] 搜索和抓取设置速率限制。
- [x] 邮件发送设置退订和黑名单机制。
- [x] 日志不记录 API Key、邮箱密码、access token。
- [x] 关键操作有审计日志。

## 11. 后续立即开始的第一个开发任务

建议下一步直接执行：

```text
开发阶段一的基础数据模型和 API：
LeadSearchTask + Lead + LeadContact
```

具体包含：

- 新建模型文件。
- 新建 Schema 文件。
- 新建 Repository。
- 新建 Service。
- 新建 API endpoint。
- 注册路由。
- 添加基础测试。

完成后，前端即可开始接入“获客任务”和“潜客列表”页面。
