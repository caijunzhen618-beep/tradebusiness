## 13 邮件触达与潜客跟进

### R-EMAIL-01：邮件管理与单次发送

邮件模块支持本人邮件列表、状态/方向/主题筛选、详情、草稿保存、直接发送或套用模板、失败邮件重发和删除记录。模板可创建/编辑/删除/预览，使用 Jinja2 渲染变量；模板管理接口只要求登录，未做创建人隔离。重发会新建邮件记录，不是把原记录重新投递。[S17]

实际投递使用全局配置 SMTP_HOST/SMTP_PORT/SMTP_USER/SMTP_PASSWORD/SMTP_FROM；465 使用 SSL，其余分支 STARTTLS。服务创建 queued 记录，SMTP 成功改 sent，失败设置 failed 并抛错。没有按业务员绑定独立邮箱账户的发送逻辑；queued 提示不代表该接口一定只是异步排队。[S17]

### R-EMAIL-02：从潜客发信

发信前检查本人潜客且非 invalid、do_not_contact=false。人工提交收件邮箱、称呼、主题与正文；不强制收件人来自已建联系人，不强制存在已生成文案。成功后把 Lead.status 改为 contacted，并写审计事件。Email 没有 lead_id 字段，该接口也不写 Customer 关联；因此邮件历史与 AI 潜客不是完整的关系型通信记录。[S12、S14、S17]

### R-FOLLOW-01：创建与执行跟进

创建跟进保存潜客、当前用户、渠道、主题、正文和 due_at；创建时同样检查禁止联系。每 5 分钟的固定任务最多取 100 条到期 pending 且 channel=email 的记录。发送对象是该潜客邮箱非空的第一个联系人，优先 is_verified=true；执行时再次过滤潜客归属、invalid 与 do_not_contact。[S14]

无可用联系人或发送异常则 failed；成功则 completed，但不会同时把潜客改为 contacted。failed 可重试，改 pending 且 due_at=当前时间；completed 不可改回其他状态。非邮件渠道没有自动投递，任务可人工改状态；不能将 completed 一律解释为已真实触达。[S14]

### R-CONTACT-02：禁止联系的覆盖范围

do_not_contact 与原因保存在 Lead，并在潜客单次发送、创建跟进和自动跟进筛选处执行。该规则没有贯穿通用邮件接口、CRM 客户、邮件模板发送和所有收件地址，不能称作全局退订/黑名单系统。WhatsApp、LinkedIn 目前是文案及跟进渠道标签，不是集成的自动发送平台。[S12、S14、S17]

Email 有 opened_at/clicked_at/replied_at 字段，但已读取的发送服务和注册邮件接口没有完成打开/点击/回复采集；邮件统计的点击及打开率、点击率、回复率为固定零值。SMTP 成功也不等同于对方收件箱已送达或已读。[S17]

## 14 客户管理与合作维护

### R-CRM-01：客户档案与查询

Customer 保存公司基本资料、国家/城市、官网、联系方式、海运/空运/陆运/多式联运业务类型，以及港口、航线覆盖、擅长货类、估计货量、来源、标签、备注、负责人、状态和 1～5 优先级（1 最高，缺省 3）。港口/航线/货量是档案字段，没有看到相应的航运业务数据自动测算。[S03、S15]

列表设计支持国家、状态、归属、优先级、标签、搜索与排序。实际 business_type 接口参数没有向服务透传；带 search 时走另一查询，忽略其他筛选与本人归属，总数取当前页条数。“未分配客户”也把 None 当成不筛选，实际未限定 assigned_to IS NULL。[S15]

### R-CRM-02：创建、修改、分配与批量导入

手工创建检查邮箱或公司名是否已存在，任一命中则拒绝；普通用户未填 assigned_to 时自动分给自己。修改邮箱、电话或官网会自动把 last_verified_at 改为当前时间，只意味着资料被修改，不代表外部核验通过。[S15]

领取接口将客户直接分给当前用户，未校验原来是否未分配；取消分配要求管理员或本人。管理员可通过修改客户归属字段调整负责人。普通用户新建/批量导入时，代码只在归属缺失时填自己，不能据此宣称已禁止填写其他人归属。[S15]

批量导入接口接收 JSON 客户数组和 overwrite 开关：按邮箱查到现有客户时，overwrite=true 尝试更新，false 计为失败；新记录仍受手工创建的重复规则约束。返回 total/created/updated/failed/errors。该接口与“上传 CSV/Excel 文件”不是一件事。[S15、S25]

### R-CRM-03：客户状态与合作

状态为 potential、contacting、cooperating、paused、lost。专用状态接口在首次进入 contacting 时记录 first_contact_date，在首次进入 cooperating 时记录 cooperation_date；普通更新接口改 status 不调用这段补日期逻辑。[S15]

普通用户通过 PUT 更新已合作客户的状态会被拒绝，但专用 /status 接口没有相同限制，规则不一致。不存在“只可按潜在→联系→合作依次流转”的强状态机。合作管理页面仅请求 status=cooperating 的客户列表，没有合同、报价、订舱、运单、收付款或合作履约模型。[S15、S22]

> Customer.status=potential 与 AI Lead.status=new 不是同一张表的同一阶段。客户被领取、更新或设为合作，不会自动同步 AI 潜客状态。

## 15 待办、通知与自动化

### R-TASK-01：普通待办

普通任务包含标题、说明、类型（如电话/邮件/会议/跟进）、关联客户、负责人、创建人、优先级、到期时间、完成时间、提醒时间和 is_reminded。优先级 low/medium/high/urgent；状态 pending/in_progress/completed/cancelled。支持创建、查询、修改、完成、我的任务、逾期、将到期与统计；普通用户只能创建分配给自己的任务，删除需管理员。[S20]

### R-NOTICE-01：通知与消息中心

通知列表按当前用户查询，支持未读过滤、未读数量、单条/全部已读、删除单条及删除已读。客户端“消息中心”是邮件通知、任务提醒、客户动态、系统通知的展示，而不是与外部客户聊天；页面读取最多 100 条并在本地计算分类数量。[S21、S30]

WebSocket 用于实时推送与 ping/pong，前端断线后 5 秒重连；服务端仅按路径 user_id 接入，没有完成 Token 验证。通知查询的认证不能替代 WebSocket 连接的鉴权。[S21、S30]

| 后端固定作业 | 实际规则 | 不能等同于 |
| --- | --- | --- |
| 潜客邮件跟进 | 每 5 分钟，最多 100 条到期邮件跟进，按联系人优先级选择收件人 | 任意渠道自动触达或用户自定义 Cron 生效。 |
| 节假日问候 | 每日 UTC 00:00；硬编码 1/1、5/1、12/25 的部分国家；只选 cooperating 客户并使用 holiday_greeting | 完整节日数据库、用户“提前几天”设置、宗教/公司节日配置已生效。 |
| 客户跟进提醒 | 每小时；cooperating 且 Customer.updated_at 早于 3 天前，提醒其负责人 | 真实“距上次联系 3 天”；任意资料修改都会改变该代理时间。 |
| 通知清理 | 每日 UTC 01:00 删除创建超过 30 天的通知 | 可配置的全系统数据保留策略或旧文件定时清理。 |

### R-AUTO-01：自动化页面的真实状态

自定义定时任务、启停、Cron 文本、节日偏好、自动回复规则及测试日志保存到 localStorage。创建/测试只写本地记录，“成功日志”表示配置或测试记录被保存，并不表示服务器执行。未接通上述固定作业，也不能跨浏览器作为系统配置共享；模板预览调用真实邮件模板接口是例外。[S14、S23]

## 16 账号、积分与套餐支付

### R-AUTH-01：账号与身份

用户名 3～50 字符，允许字母数字、下划线和连字符，创建时转小写；邮箱必须格式有效。注册和改密密码 8～100 字符，包含大写、小写和数字；登录支持用户名或邮箱。账户禁用后不能认证。令牌刷新重新检查用户存在/启用；登出只返回消息，实际依赖客户端删除令牌，没有服务端吊销表。[S04]

管理员用户管理支持创建、查询、修改、角色与状态管理、删除，不能删除自己。用户可以改本人资料和校验旧密码后改密。公开注册同时接受 UserCreate.role，未将角色强制收敛为 sales，属于与管理员建号边界冲突的实现问题。[S04]

### R-CREDIT-01：钱包与扣费

首次通过服务获取/扣减钱包时按 100 积分初始化；钱包按用户唯一。背调首次生成 5 分、每次话术生成 2 分；扣费额必须为正，余额不足返回 402，并记录 amount、balance_after、action、description。现有钱包扣费查询使用行锁；钱包表默认值为 0，与服务层初始化 100 的口径需要区分。[S19、S24]

钱包与最近 100 条流水按本人读取。/billing/adjust 允许登录用户调整本人余额，只检查结果不为负；未要求管理员或可信支付来源。它不是可安全上线的人工充值权限设计，不能据此确认商业化计费闭环已可靠。[S24]

### R-PAY-01：套餐、订单与 Stripe

公开列出启用套餐，字段为名称、整数价格、积分、interval、启用状态。创建订单从套餐读取金额，状态 pending；用户可查询本人最近 100 条订单与当前订阅记录。Stripe Checkout 路径真实调用外部接口，要求密钥；生产环境拒绝本地回跳地址配置；成功通过 Checkout URL 跳转支付。[S24]

Stripe webhook 按原始请求验 HMAC 签名和 300 秒时间差，仅处理 checkout.session.completed 且 payment_status=paid，凭 metadata.payment_order_id 找订单，锁定订单并在未 paid 时给钱包加套餐积分、记流水、激活订阅。实际交易成功与金额/会话等对应关系仍需运行验收，代码存在不等于真实支付验收通过。[S24]

开发环境还有直接激活订阅与开发回调；生产禁用分支中，开发回调函数在局部 import HTTPException 之前使用它，存在作用域错误风险。Checkout 使用 mode=payment，不是周期性自动续费；订阅记录没有到期续扣或退款处理链路，interval 字段本身不能证明这些能力已实现。[S24]

## 17 文件、统计与设置

### R-FILE-01：上传与文件使用

通用文件默认最大 10MB；Logo 限 jpg/jpeg/png/gif/svg、5MB；附件为常见文档/图片/压缩包、20MB；导入文件限 csv/xlsx/xls、50MB。按 UUID 重命名并保存本地上传目录，返回原文件名、相对路径、URL、大小、类型和上传时间；路径处理有越界校验。[S25]

上传接口和文件删除要求登录，但没有文件所有者记录/校验，静态 /uploads 提供访问。导入文件上传只落盘，没有在该服务中解析并创建客户；邮件草稿可存附件元信息，但 SMTP 发送代码只附 HTML 正文，没有把上传附件拼成邮件附件。[S01、S17、S25]

### R-EXPORT-01：导出

导出客户、邮件和客户状态/国家统计，支持 xlsx/csv。客户和邮件直接查全表，未应用当前用户/前端筛选；文件属于全局导出而非“导出我筛选出的数据”。这与个人列表权限不一致，文档标注为缺陷，不作为正当跨用户权限。[S26]

| 指标/页面 | 代码计算口径 | 状态 |
| --- | --- | --- |
| CRM 统计 | Customer 全局总数、按状态、按国家及前列国家 | A/D：普通登录用户亦可访问全局统计。 |
| AI 获客统计 | 本人潜客/文案/跟进数量；国家/行业/当前状态分布 | A：不同对象分别计数。 |
| AI 回复率 | replied ÷ (contacted + replied) ×100；分母为 0 返回 0 | B：依赖当前人工/操作状态，不是邮件收件回复事件。 |
| AI 渠道分布 | 按 FollowupTask.channel 分组统计跟进记录 | A/B：不是各渠道实际送达数。 |
| 邮件统计 | 按邮件当前状态聚合；clicked=0，打开率/点击率/回复率=0 | B/C：有字段与页面，不等于跟踪能力。 |
| 今日发信（服务内） | 按当天创建且 outgoing 的记录计数 | B：不是仅统计发送成功，草稿/失败记录可能混入。 |

### R-SETTING-01：设置范围

管理端个人信息/改密/邮件模板调用实际 API；通知偏好、系统名称、分页、自动保存、调试模式等配置仅写 localStorage。不能认为在页面保存后已改变服务端调度、SMTP、AI 或其他用户行为。后台统计页面的基础图表读取实际统计接口；没有据此证明业务员收入、订单业绩或完整营销归因。[S17、S22、S27]

## 18 数据需求：核心业务对象

以下是业务数据字典，不是数据库迁移文件。UUID、创建/更新时间为常见基础字段；写有某个 ID 不一定存在数据库外键约束，尤其采集线索中的审核/导入/匹配 ID 多为普通字符串。[S02、S03、S12、S28]

| 对象 | 关键数据 | 归属与关系 / 输出 |
| --- | --- | --- |
| ScrapingTask<br>采集任务 | 名称、类型、关键词、国家、来源 URL、config；状态、创建人、起止时间、发现/保存数量、进度、日志、诊断与错误 | 管理员管理的全局采集工作；通过 scraping_task_id 关联采集线索。 |
| ScrapedLead<br>采集线索 | raw_data、来源/来源 URL、公司名/英文名、国家/代码/城市、邮箱/电话/WhatsApp/网站、业务类型、简介、confidence_score | 待审核公司资料，不是已确认客户；状态 pending/approved/rejected/imported。 |
| ScrapedLead<br>审核/转换字段 | reviewed_by/at、rejection_reason；imported_to_customer_id/at、matched_by；duplicate_of、similarity_score | 实际 duplicate_of 写 Customer ID；导入结果回指 CRM；审核信息与质量分分开。 |
| Customer<br>CRM 客户 | 公司多语言名、Logo、官网、成立年份、资本/规模；业务类型、港口/航线/货类 JSON、估计货量；国家、地址、联系方式、社交链接 | assigned_to 为负责人；status、priority、tags、notes、source、data_confidence、last_verified_at、首联/合作日期。 |
| LeadSearchTask<br>AI 获客任务 | user_id、名称、目标国/行业、product_keywords、exclude_keywords、customer_profile、website_inputs、状态、total_found、error_message | 用户个人任务；关键词等 JSON items；一对多 Lead。 |
| Lead<br>AI 潜客 | user_id、可空 task_id、公司名、网址、国家、行业、描述、来源、match_score、status、do_not_contact/原因、notes | 个人潜客；关联联系人、报告、文案与跟进；没有 Customer 外键。 |
| LeadContact<br>潜客联系人 | lead_id、name/title/email/phone/linkedin_url/whatsapp/source/is_verified | 个人归属由 Lead 推导；可有多条，自动邮件选邮箱非空且 verified 优先。 |
| CompanyResearchReport<br>企业背调 | lead_id、summary、business_model、products、target_markets、buying_signals、pain_points、recommended_angle、raw_sources | 按潜客读取最新报告；无独立跨用户授权；报告复用不等于资料最新。 |

重要转换损耗：ScrapedLead 的 business_type/description 没有进入正常 Customer 导入映射；ScrapedLead → Lead、Lead → Customer、LeadContact → Customer 联系字段均未发现自动转换主链。[S10–S15]
