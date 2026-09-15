## 19 数据需求：开发与支撑对象

| 对象 | 主要数据及业务用途 | 边界 |
| --- | --- | --- |
| SalesCopy | lead_id、channel、language、subject、content、tone、status；保存生成话术 | status 默认 draft；没有与发信的已发送状态同步闭环。 |
| FollowupTask | lead_id、user_id、channel、subject、content、due_at、status | 与普通 Task 分离；非邮件渠道不自动发送。 |
| SalesAgent | user_id、name、公司/产品介绍、价值主张、目标客户、tone、forbidden_words、default_language、is_default | 配置属于个人；字段存在不代表生成时全部强制执行。 |
| AgentKnowledgeDocument | agent_id、file_name、content_text、embedding_status | 保存文本；ready 不代表完成向量化。 |
| AgentPromptTemplate | agent_id、name、channel、language、prompt_text、is_active | 提示词模板，与 EmailTemplate 的 Jinja2 发信模板不同。 |
| Email / EmailTemplate | 邮件的 customer_id/sender_id、收发件人、正文、方向、状态、模板引用、sent/opened/clicked/replied 时间、错误、message/thread ID、附件；模板名称/语言/变量/启用 | Email 没有 lead_id；不少跟踪字段未形成写入闭环。 |
| Task | 客户关联、创建人、负责人、标题、类型、优先级、状态、到期/完成/提醒时间、提醒标记 | 人工待办，不等于采集任务或潜客自动跟进任务。 |
| Notification / Holiday | 通知用户、类型、标题、正文、data、已读与时间；节日模型存在 | 固定节日问候实际使用硬编码日期/国家，不读取 Holiday。 |
| User | 用户名、邮箱、密码哈希、姓名、admin/sales、启用、superuser、电话/头像、部门/入离职等资料 | 无企业租户/自定义权限模型；部门是资料字段。 |
| CreditWallet / CreditTransaction | 用户唯一钱包余额；流水金额、变动后余额、动作、描述 | 初始化分值由服务决定；钱包操作不等于真实货币账户。 |
| SubscriptionPlan / UserSubscription | 套餐名、价格、积分、interval、启用；用户与当前套餐、状态 | 没有完整周期到期/自动续费模型。 |
| PaymentOrder | user_id、plan_id、amount、provider、status、external_id | 用于套餐支付，不是客户货运订单。 |
| 上传文件 / 浏览器本地数据 | 文件落本地目录；自动化规则/日志、通知偏好、系统配置落 localStorage | 未形成统一按用户持久化的配置服务；文件没有所有权模型。 |

数据关系主干：User → AI 任务/Lead/智能体/钱包；Lead → 联系人/报告/文案/跟进；ScrapingTask → ScrapedLead → Customer；Customer → 普通 Task/Email；User → Notification。两条获客链路之间未见共同客户主键或自动归并规则。[S02–S28]

## 20 实现差异清单：核心业务

本页列现状差异，不定义 V1 新需求，不安排开发优先级。D 表示从当前调用/字段/路由可定位的冲突；真实运行表现仍需环境复现。

| 编号 | 发现与业务影响 | 证据 / 状态 |
| --- | --- | --- |
| D01 | 业务员“发现客户”调用的采集接口要求 admin，普通业务员无法使用该页面完成搜索。 | S05；D |
| D02 | AI 任务只按官网建档，产品词和排除词不执行；match_score 固定 60。 | S12；B/C |
| D03 | AI CSV 导入按钮调用未注册路由，不能实际导入。 | S13、S29；D |
| D04 | 选择智能体生成文案时调用错误 Repository 方法；知识注入分支阻断。 | S18、S19；D |
| D05 | 采集、AI 潜客、CRM 是分立对象；没有统一去重、自动转化或联系人同步。 | S02、S10–S15；B |
| D06 | 采集取消只改状态，不能阻止后台继续采集；完成状态可覆盖取消。 | S06；D |
| D07 | 业务员 max_results/business_type 与执行器参数/实际过滤不一致。 | S05–S07；D |
| D08 | 来源分命名有限；可信度按原始字段计分，清洗后可能仍保留“有邮箱”的加分。 | S09；B |
| D09 | 重复分 70 为固定值；模糊检测未调用；正常导入跳过重复而非自动合并。 | S09–S11；B/C |
| D10 | 采集业务类型与简介导入 CRM 时未映射；duplicate_of 的字段注释与写入对象不一致。 | S10、S11、S28；D |
| D11 | 报告复用不刷新；背调/文案会覆盖潜客阶段，统计不是不可逆转化漏斗。 | S12、S16、S19；B |
| D12 | 自定义自动化/自动回复只存 localStorage，与服务器固定作业不连通。 | S14、S23；C |
| D13 | SMTP 不带上传附件；没有完整收信/打开点击/回复采集；渠道标签不等于平台接入。 | S14、S17、S25；B/C |
| D14 | 自动跟进成功不更新 contacted；允许人工设 completed，完成数不能代替真实送达数。 | S14；B |

另外，知识文档“ready”、CRM“最近验证时间”、背调“需求信号”和“合作管理”都存在名称比实际处理更强的情况，正文已按真实语义拆解，未将名称直接扩大为产品能力。

## 21 实现差异清单：权限与统计

| 编号 | 代码事实及影响 | 证据 / 状态 |
| --- | --- | --- |
| D15 | 公开注册接受 admin 角色，与“管理员管理账号”边界冲突。 | S04；D |
| D16 | CRM search 分支丢失用户归属/其他筛选；“未分配”没有 IS NULL；可能返回不应展示的客户。 | S15；D |
| D17 | 领取客户没有未分配前置校验，可覆盖原负责人；普通创建/批量导入可能保留传入归属。 | S15；D |
| D18 | 客户 PUT 与专用 status 接口对已合作状态限制不同；日期补齐规则也不同。 | S15；D |
| D19 | 客户/邮件导出直接查全表；客户和邮件统计为全局口径，未沿用个人列表范围。 | S15、S17、S26；D |
| D20 | 普通用户可调用本人钱包 adjust；不能确认充值来源的可信控制已闭合。 | S24；D |
| D21 | WebSocket 接收路径 user_id 而无 Token 校验；在线用户接口也未认证。 | S21；D |
| D22 | 文件上传/删除没有所有者模型；公开静态文件与“登录后删除”不是资源级权限。 | S01、S25；D |
| D23 | 潜客禁止联系没有覆盖通用邮件/CRM 发送入口，不能视为全局退订管理。 | S12、S14、S17；B |
| D24 | 邮件统计的比例/点击指标固定为 0；AI 回复率依赖状态，渠道分布只计跟进。 | S14、S17；B/C |
| D25 | 开发支付回调生产分支存在局部 HTTPException 导入前引用；开发回调状态又不是严格单向终态。 | S24；D |
| D26 | 支付套餐 interval 不等于自动续费；未见周期扣款、订阅到期、退款闭环。 | S24；B |

### 实现状态不能替代运行验收

本次没有执行越权请求、发送邮件、调整积分、发起支付或修改仓库。权限问题通过接口依赖、筛选条件与调用参数静态判断，不提供实际业务数据泄露证明，也不把未测试环境行为写成已发生的事故。

模型返回通用文字、没有搜到企业、返回空图表或出现“保存成功”，都可能是代码预期分支，不自动等于相应业务目标达成。V0 应保留这些结果口径，用于后续逐项与真实运行结果比对，而不是用 UI 完整度代替交付结果。

## 22 现状核对场景与运行边界

以下为据代码推导的核对场景，尚未执行，不是新增产品方案。它们用于避免后续沟通把某个功能名称误认为更完整的实现。

| 场景 | 代码预期 / 应观察的事实 | 对应需求 |
| --- | --- | --- |
| 普通 sales 打开发现客户并创建任务 | 采集接口应拒绝非管理员；页面存在不代表可用。 | R-ROLE-02 / D01 |
| AI 任务只填产品词，不填官网 | 可创建并执行为新增 0，不会自动搜索企业。 | R-AILEAD-01 |
| 同任务重复运行相同官网 | 不重复新增该同任务同网址潜客；本次新增数可归 0。 | R-AILEAD-01 |
| 两个任务输入同一官网 | 当前去重有 task_id 条件，可能建立两个 Lead。 | R-AILEAD-01 |
| 采集 raw 字段齐全但邮箱格式无效 | 规则分可能获得邮箱加分，标准化邮箱仍置空。 | R-QUAL-01/02 |
| 同名不同邮箱的 approved 线索导入 | 现行 AND 条件可能判为不重复；与 CRM 手工创建不同。 | R-IMPORT-01 |
| 未配置模型，首次/再次背调 | 首次返回规则报告并正常计费；再次直接复用，不重复扣 5。 | R-RESEARCH-01/02 |
| 选择有效智能体生成话术 | 应核对 get_context_text 调用位置产生的异常，不作为知识生成成功。 | R-COPY-01 / D04 |
| 无邮箱联系人或 DNC 的到期跟进 | 邮箱跟进无法选到允许联系的联系人，转失败；不会自动换渠道。 | R-FOLLOW-01 |
| 创建 WhatsApp/LinkedIn 跟进 | 固定邮件任务不会自动发送它们；人工状态变化不等于平台送达。 | R-FOLLOW-01 |
| 自动化页面创建 Cron 并查看日志 | 浏览器保存配置/测试记录；后端不会因此新增调度作业。 | R-AUTO-01 |
| 采集正常完成但为 0 条 | 查看诊断与来源检查，不能仅凭 completed 判断获客成功。 | R-DISC-02 |

### 运行前置条件与本次未覆盖事项

持久化依赖数据库与实际迁移版本；搜索依赖网络、目标站点可访问性和可能的 Google 凭据；AI 依赖模型配置，否则规则回退；邮件依赖 SMTP；到期跟进依赖 Celery Worker 与 Beat；Stripe 依赖密钥、回跳地址和 webhook 配置。网页采集运行于 Web 进程，和 Celery 调度不是同一机制。[S06、S07、S14、S16、S17、S24]

未核验线上配置、真实数据库数据、全量测试覆盖/执行结果、部署脚本能否成功启动、外部服务成功率或真实客户业务适配性。因此，这份 V0 是可追溯的代码现状说明，不是可直接签署的生产可用性或业务有效性验收报告。

## 附录：代码证据索引

以下路径均对应固定提交 `48edaeb99553a72ecd95b5c2721b3675796e6b41`，不是随主分支变更的浮动版本。文中 [Sxx] 为代码来源组，不是新增需求。

### S01 产品入口与模块注册

`tradebusiness-backend/app/main.py`  
`tradebusiness-admin/src/router/index.ts`  
`tradebusiness-client/src/router/index.ts`  

### S02 模型范围与数据主干

`tradebusiness-backend/app/models/lead_generation.py`  
`tradebusiness-backend/app/models/scraped_lead.py`  

### S03 客户语义、业务与状态字段

`tradebusiness-backend/app/models/customer.py`  
`tradebusiness-client/src/views/customers/DiscoverCustomers.vue`  

### S04 认证、用户及角色规则

`tradebusiness-backend/app/api/v1/auth.py`  
`tradebusiness-backend/app/api/v1/users.py`  
`tradebusiness-backend/app/api/deps.py`  
`tradebusiness-backend/app/schemas/user.py`  
`tradebusiness-backend/app/models/user.py`  
`tradebusiness-backend/app/services/user_service.py`  

### S05 采集接口与业务员入口

`tradebusiness-backend/app/api/v1/scraping.py`  
`tradebusiness-client/src/views/customers/DiscoverCustomers.vue`  

### S06 采集调度、来源搜索与网页处理

`tradebusiness-backend/app/scrapers/task_manager.py`  
`tradebusiness-backend/app/scrapers/example_scraper.py`  

### S07 Google 查询与公司信息抽取

`tradebusiness-backend/app/scrapers/google_search.py`  

### S08 采集线索审核/导入路由

`tradebusiness-backend/app/api/v1/scraped_leads.py`  

### S09 标准化、可信度与未接入的模糊查重

`tradebusiness-backend/app/scrapers/data_normalizer.py`  

### S10 审核/导入/删除业务实际约束

`tradebusiness-backend/app/services/scraped_lead_service.py`  

### S11 重复 SQL 与 Customer 转换映射

`tradebusiness-backend/app/services/lead_importer.py`  

### S12 AI 任务执行与潜客归属

`tradebusiness-backend/app/services/lead_generation_service.py`  
`tradebusiness-backend/app/repositories/lead_generation_repo.py`  
`tradebusiness-backend/app/schemas/lead_generation.py`  

### S13 AI 获客路由和页面入口

`tradebusiness-backend/app/api/v1/lead_generation.py`  
`tradebusiness-admin/src/views/lead-generation/index.vue`  

### S14 潜客发送、跟进、统计与固定定时作业

`tradebusiness-backend/app/api/v1/lead_generation.py`  
`tradebusiness-backend/app/tasks/automation_tasks.py`  

### S15 CRM 规则及权限冲突

`tradebusiness-backend/app/api/v1/customers.py`  
`tradebusiness-backend/app/services/customer_service.py`  
`tradebusiness-backend/app/repositories/customer_repo.py`  

### S16 背调、主页抓取与模型/规则回退

`tradebusiness-backend/app/services/company_research_service.py`  
`tradebusiness-backend/app/services/website_crawler_service.py`  
`tradebusiness-backend/app/services/ai_provider_service.py`  

### S17 邮件、模板、统计及附件发送边界

`tradebusiness-backend/app/api/v1/emails.py`  
`tradebusiness-backend/app/services/email_service.py`  
`tradebusiness-backend/app/models/email.py`  

### S18 智能体与知识文本的真实实现

`tradebusiness-backend/app/api/v1/sales_agents.py`  
`tradebusiness-backend/app/repositories/sales_agent_repo.py`  
`tradebusiness-backend/app/models/sales_agent.py`  

### S19 开发话术生成与错误的方法调用

`tradebusiness-backend/app/services/sales_copy_service.py`  

### S20 普通任务接口及数据字段

`tradebusiness-backend/app/api/v1/tasks.py`  
`tradebusiness-backend/app/models/task.py`  

### S21 通知权限及 WebSocket 入口

`tradebusiness-backend/app/api/v1/notifications.py`  

### S22 合作列表与统计图表

`tradebusiness-admin/src/views/cooperation/list.vue`  
`tradebusiness-admin/src/views/statistics/overview.vue`  

### S23 本地自动化配置与测试记录

`tradebusiness-client/src/views/automation/Automation.vue`  

### S24 积分、套餐、订单和支付处理

`tradebusiness-backend/app/services/credit_service.py`  
`tradebusiness-backend/app/api/v1/billing.py`  
`tradebusiness-backend/app/models/billing.py`  

### S25 文件大小/类型/存储规则

`tradebusiness-backend/app/api/files.py`  
`tradebusiness-backend/app/services/file_service.py`  

### S26 全局导出查询及文件格式

`tradebusiness-backend/app/api/export.py`  
`tradebusiness-backend/app/services/export_service.py`  

### S27 管理端设置的保存位置

`tradebusiness-admin/src/views/settings/config.vue`  

### S28 采集线索审核/导入/重复字段语义

`tradebusiness-backend/app/models/scraped_lead.py`  

### S29 CSV 前端请求契约

`tradebusiness-admin/src/api/leadGeneration.ts`  

### S30 客户端消息中心及统计范围

`tradebusiness-client/src/views/messages/Messages.vue`  
