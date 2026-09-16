# V0 → V1 复用评估

> 评估对象：当前 `main` 分支。分类含义：**直接复用**=业务语义不变；**改造复用**=保留工程/局部能力但不得沿用旧领域语义；**废弃**=V1 主流程不再使用，V0 文件和数据仍保留；**全新开发**=V0 无对应能力。

## 1. 总结

V0 的工程底座可复用，获客领域中心模型不可直接复用。V0 同时存在 `customers`、`leads`、`scraped_leads` 三套企业/线索表达，联系方式嵌在企业或 `LeadContact` 中，搜索任务以用户配置关键词/国家/行业为中心，并用永久 `match_score` 和全局 Lead 状态表达业务；这些都与确认后的 V1 冲突。

建议复用身份认证、基础 Repository、FastAPI/SQLAlchemy 会话、邮件发送、文件、日志审计、通知、Redis/Celery 部署骨架；新建 V1 产品、企业事实库、匹配、产品池、触达活动和 acquisition pipeline。

## 2. 后端模块逐项评估

| V0 模块/文件组 | 分类 | 理由与 V1 去向 |
| --- | --- | --- |
| `core/security.py`、`api/v1/auth.py`、`models/user.py`、`user_*` | 直接复用 | 身份认证/用户管理不改变；补充 tenant/owner 边界即可 |
| `db/session.py`、`models/base.py`、`repositories/base.py` | 改造复用 | SQLAlchemy 异步骨架可用；引入 Alembic、事务/UoW、分页与并发约束 |
| `main.py`、异常、日志、审计 | 改造复用 | 应用工厂、中间件、request_id、结构化错误和敏感字段脱敏需加强 |
| `notifications` 模型/API/Service/WebSocket | 改造复用 | 可承载补客完成/跟进提醒；消息类型和 tenant 语境扩展 |
| `files.py` / `file_service.py` | 直接复用 | 非 V1 核心但通用上传能力可保留 |
| `email.py`、`email_service.py`、邮件 API | 改造复用 | SMTP/模板/发送记录可用；外键从 Customer 扩到 Prospect/ContactPoint，发送需产生活动关联 |
| `task.py`、任务 API/Service | 改造复用 | 通用待办可保留；V1 下次跟进以 ContactActivity 为事实源，不用 Task 代替活动历史 |
| `customer.py`、Customer API/Repo/Service | 废弃（V1 主流程） | 单表混合企业、联系方式、线路、全局状态，与 Prospect 多角色/事实库/产品语境冲突；可作为历史客户域只读保留 |
| `lead_generation.py` 的 LeadSearchTask/Lead/LeadContact | 废弃模型，局部代码参考 | task 私有 Lead 导致跨产品重复；match_score、全局 status/DNC、嵌入式联系方式语义冲突 |
| `lead_generation_service.py` / Repo / API | 废弃主流程，局部算法参考 | 面向关键词/画像/排除词配置及一次搜索任务，不符合“用户只表达产品和角色、企业库优先” |
| `company_research_service.py` | 改造复用 | 网页研究和来源收集思路可抽为 Enrichment Provider；输出必须成为原子 Evidence，不保存单份不可计算报告作为权威 |
| `website_crawler_service.py` | 改造复用 | 抓取/提取可封装为官网 Provider；增加限流、来源、完整富化、幂等和合规边界 |
| `ai_provider_service.py` | 改造复用 | AI 只能做提取/候选判断，输出需 schema 校验和 Evidence 来源，不能做黑盒最终分数 |
| `sales_copy_service.py`、SalesCopy | 改造复用（后置） | 邮件文案能力可用于触达；非 V1 首批核心，且渠道收敛为 phone/email |
| `FollowupTask` 与自动发送 API | 废弃自动跟进语义 | V1 是可选下次跟进，不要求自动代发；由 ContactActivity 派生提醒 |
| `sales_agent` 模型/API/页面 | 废弃（V1 范围） | 销售智能体、知识文档、prompt 模板不在确认的最小闭环；V0 保留 |
| `scraping_task.py`、Scraping API | 废弃面向用户模型，改造执行骨架 | 用户不配置 scraper/关键词/国家；内部任务改为 AcquisitionRun/Batch |
| `scraped_lead.py`、审核/导入 Service/API | 改造复用概念，废弃表语义 | 原始记录、审核、重复检测有价值；替换为 provider_records + resolution queue，不再导入 Customer |
| `scrapers/base.py` | 改造复用 | 形成 Discovery/Enrichment 两类 provider contract |
| `google_search.py`、`example_scraper.py` | 改造复用 | 仅作为 Discovery 实现候选，先核对合法性/稳定性；输出 CompanySeed 而非 Customer |
| `data_normalizer.py` | 改造复用 | 保留确定性清洗，升级公司身份、电话/email 标准化和来源追踪 |
| `rate_limiter.py`、`proxy_pool.py` | 改造复用 | Provider 级限流可用；代理使用必须符合数据源条款，不作为绕过访问控制手段 |
| `scrapers/task_manager.py` | 废弃/参考 | 与 V0 ScrapingTask 强耦合；由 acquisition orchestrator 取代 |
| `lead_importer.py` | 废弃 | scraped_leads→customers 单向导入不符合全局事实 upsert |
| billing/credit 全模块 | 直接复用（与 V1 解耦） | 商业化基础设施语义独立；补客成本扣费若未来启用需单独产品规则 |
| `export_service.py`、导出 API | 改造复用 | 导出框架可用；改为 Prospect/ProductProspect 字段和权限 |
| `automation_tasks.py` | 改造复用 Celery 配置；任务逐项见第 5 节 | worker/beat 骨架可用，V1 工作流需新任务与幂等状态 |

## 3. 数据库表逐表评估

| V0 表 | 分类 | 处理 |
| --- | --- | --- |
| `users` | 直接复用 | 保持 ID；补 owner/tenant 策略 |
| `customers` | 废弃为 V1 主档 | 只读保留；经清洗去重后映射到 prospects，不能直接改名 |
| `lead_search_tasks` | 废弃 | 不作为产品或补客计划；无生产数据需要迁移 |
| `leads` | 废弃为 V1 主档 | 不复用永久 match_score、全局状态和 task 私有企业模型 |
| `lead_contacts` | 废弃表结构，参考字段 | V1 全新实现 contacts/contact_points；email/phone 分行并保留来源 |
| `company_research_reports` | 改造复用提取思路 | V1 将可追溯结果拆为 Evidence，不复用报告表 |
| `sales_copies` | 改造复用 | 可保留历史草稿；未来关联 Prospect/Activity |
| `followup_tasks` | 废弃 V1 语义 | V1 使用 ContactActivity.next_follow_up_at；无历史数据迁移 |
| `scraping_tasks` | 废弃 | V1 用 acquisition_runs/batches；V0 只读保留 |
| `scraped_leads` | 废弃表语义 | Provider 新结果写入 provider_records；不迁移未上线样例数据 |
| `emails` | 改造复用 | 保留发送基础；增加 Prospect/ContactPoint/产品语境关联或桥接表 |
| `email_templates` | 直接复用 | 模板能力独立 |
| `tasks` | 直接复用通用待办 | 不作为 ContactActivity 的替代 |
| `notifications` | 直接复用 | 扩展 V1 类型 |
| `holidays` | 废弃（V1 范围） | V0 保留；节日营销不在 V1 |
| `sales_agents`、`agent_knowledge_documents`、`agent_prompt_templates` | 废弃（V1 范围） | V0 保留 |
| `credit_wallets`、`credit_transactions`、`subscription_plans`、`user_subscriptions`、`payment_orders` | 直接复用 | 与 V1 领域解耦 |

V1 全新表：`logistics_products`、`product_inventory_targets`、`prospects`、`prospect_roles`、`prospect_identities`、`contacts`、`contact_points`、`evidences`、`product_matches`、`product_prospects`、`product_suppressions`、`contact_activities`、`acquisition_runs`、`acquisition_batches`、`provider_records`、`prospect_merge_logs`。

## 4. API 逐组评估

| V0 API 组 | 分类 | 说明 |
| --- | --- | --- |
| `/auth/*`, `/users/*` | 直接复用 | 权限边界补强 |
| `/billing/*` | 直接复用 | 与 V1 解耦 |
| `/notifications/*` | 改造复用 | 增加 acquisition/follow-up 事件 |
| `/files/*` | 直接复用 | 保留 |
| `/emails/*` | 改造复用 | V1 增加 Prospect/ContactPoint/Product 上下文 |
| `/tasks/*` | 改造复用 | 保留通用任务，不承载产品联系结论 |
| `/customers/*` | 废弃于 V1 UI | 为 V0 保持兼容，不删除 |
| `/lead-generation/tasks/*`, `/leads/*`, `/followups/*`, `/stats` | 废弃并新建 V1 API | 对象、状态、搜索输入和匹配分数均不兼容 |
| `/scraping/*` | 废弃于业务端 | Provider 运行变为内部 acquisition API |
| `/leads`（scraped leads）审核/导入 | 废弃/后台重构 | 不再人工导入 Customer；必要时提供实体冲突队列 |
| `/sales-agents/*` | 废弃（V1 范围） | 非最小闭环 |
| `/export/*` | 改造复用 | 查询源改为 V1 模型 |

## 5. 后台任务逐项评估

| V0 任务 | 分类 | 说明 |
| --- | --- | --- |
| `run-lead-search` | 废弃 | 用 acquisition run 分阶段任务取代 |
| `scrape-customers` | 改造复用 | 变为 provider discovery batch，不直接产生 Customer |
| `send-email`、`send-bulk-emails` | 改造复用 | 发送需关联 ContactPoint/Product 并落 ContactActivity；批量触达不作为首批 UI |
| `send-due-lead-followups` | 废弃自动代发 | V1 提醒跟进，不默认自动发送 |
| `send-automated-followup` | 废弃（V1） | 超出最小闭环 |
| `send-followup-reminders` | 改造复用 | 数据源改为 ContactActivity.next_follow_up_at |
| `send-holiday-greetings` | 废弃（V1） | 非 V1 范围 |
| `cleanup-old-notifications` | 直接复用 | 通用维护任务 |

V1 新任务：`start_acquisition_run`、`consume_library_matches`、`discover_batch`、`resolve_entities`、`qualify_prospects`、`enrich_companies`、`enrich_contacts`、`validate_contact_points`、`upsert_global_library`、`recompute_product_matches`、`admit_product_pool`、`finalize_acquisition_run`。

## 6. 前端页面与 API 模块逐项评估

### 业务端 `tradebusiness-client`

| 页面/模块 | 分类 | 说明 |
| --- | --- | --- |
| 登录、Layout、Profile、Settings | 直接/改造复用 | 壳与身份可用，导航改为产品工作台 |
| `home`、`analytics` | 改造复用 | 指标改为库存、触达、漏斗、复用率 |
| `customers/MyCustomers`、`UnassignedCustomers`、详情抽屉 | 废弃 V1 语义，组件样式参考 | 分配/全局 Customer 状态不符合产品语境 |
| `customers/DiscoverCustomers` | 废弃 | 用户不配置爬虫/关键词；由“补充潜客”代替 |
| `lead-generation/Overview`、`Detail` | 废弃并重建 | 任务中心 Lead 模型与 V1 产品池冲突 |
| `emails/Inbox`、`Compose` | 改造复用 | 写邮件入口嵌入潜客工作台，保留发送/历史能力 |
| `tasks/Tasks` | 改造复用 | 可展示跟进提醒，权威数据仍来自 Activity |
| `messages`、`automation` | 废弃（V1 范围） | 不在确认闭环 |
| `api/request.ts`、auth store/utils | 直接复用 | 通用基础 |
| customer/scraping/leadGeneration API | 废弃并新增 product/prospect/pool/activity/acquisition API | 契约不兼容 |
| email/task/notification/file API | 改造复用 | 增加 V1 上下文 |

### 管理端 `tradebusiness-admin`

| 页面组 | 分类 | 说明 |
| --- | --- | --- |
| 登录/Layout/用户/套餐/积分/通知/设置 | 直接/改造复用 | 通用后台能力 |
| 客户、合作、AI 获客、采集、采集线索 | 废弃 V1 语义并另建运营视图 | V1 需要企业合并冲突、Provider 漏斗、run 诊断 |
| 邮件、任务、统计 | 改造复用 | 数据源切换到 V1 关联与指标 |
| 销售智能体/话术模板 | 废弃（V1 范围） | V0 保留 |

## 7. V0 保留边界

产品尚未上线，不设计 V0→V1 数据迁移、双写、兼容读取或数据回滚。V1 新模型、新 API 和新页面独立建设；V0 代码继续保留在仓库，不删除、不进入 V1 运行链路。复用评估的目的仅是判断哪些工程代码值得拿来用，不是为旧数据建立兼容包袱。
