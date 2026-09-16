# 货代获客工具 V1 技术方案

> 状态：待技术评审，评审通过前不进入正式 V1 业务代码开发
>
> 需求基线：`docs/requirements/v1/01`～`09`
>
> 原型：`docs/prototype/v1/index.html`

## 1. 决策摘要

V1 采用“通用企业获客底座 + 货代领域策略”的模块化单体。前端保留 Vue 3 技术栈；后端保留 FastAPI、SQLAlchemy、MySQL、Redis/Celery 等经验证的工程底座，但 V1 领域模型和业务 API 独立建设，不以 V0 `Customer`、`Lead` 或 `ScrapingTask` 为中心继续堆字段。

核心约束：

- 一份全局企业事实库；同一企业不因产品或客户角色重复创建。
- `Prospect` 可同时拥有 `freight_forwarder`、`exporter` 角色。
- 联系方式拆为 `Contact` 与 `ContactPoint`；无效只作用于具体联系方式。
- 企业客观事实优先保存为企业级 `Evidence`；产品级判断仅在无法动态推导时保存。
- `ProductProspect` 只表达“产品 × 客户角色”的业务工作集，不复制企业字段、不保存永久匹配分数和可计算状态。
- 联系历史以 `ContactActivity` 为事实源；6 类结果保持产品语境。
- 补客为用户手动触发的异步工作流：企业库优先，仍不足才外部发现。
- Provider 可替换、可观测、可限流，不形成单一 `find_customers()` 黑盒。

## 2. 系统边界与模块

```text
Vue 3 业务端
  ├─ 物流产品
  ├─ 潜客工作台
  ├─ 企业详情/事实库
  ├─ 触达与跟进
  └─ 补客任务进度
          │ REST + SSE/轮询
FastAPI 模块化单体
  ├─ product              物流产品与角色库存目标
  ├─ prospect             企业、角色、联系人、联系方式
  ├─ evidence             企业事实与来源
  ├─ matching             货代产品匹配与推荐解释
  ├─ pool                 ProductProspect 与库存计算
  ├─ outreach             ContactActivity、拒绝范围、邮件
  ├─ acquisition          补客编排、批次、漏斗
  └─ provider             Discovery / Enrichment 适配器
          │
MySQL（事实与状态） + Redis（队列/短期锁） + Celery（异步任务）
```

V1 先使用模块化单体，而非微服务。原因是当前团队需要快速验证数据漏斗和业务闭环；领域边界通过 Python 包、Service/Repository 和任务消息契约隔离，未来可按 Provider 或 acquisition worker 的吞吐独立拆分。

## 3. 前端方案

### 3.1 页面与路由

| 路由 | 页面 | 关键交互 |
| --- | --- | --- |
| `/products` | 物流产品列表 | 创建、编辑、启停、进入产品工作台 |
| `/products/:id/prospects` | 潜客工作台 | 同行/出口货主切换、库存、补客、筛选、连续触达 |
| `/prospects/:id` | 企业详情抽屉/页 | 企业角色、Evidence 来源、联系人、联系方式、产品语境历史 |
| `/enterprise-library` | 企业事实库 | 搜索企业、查看跨产品复用事实和匹配产品 |
| `/acquisition-runs` | 补客任务 | 阶段、批次、漏斗、错误、停止原因 |

### 3.2 状态与组件

- 使用 Pinia 分域：`productStore`、`poolStore`、`prospectStore`、`acquisitionStore`。
- 服务端为库存、最近结果、下次跟进的计算权威；前端只缓存查询结果。
- 组件：`ProductForm`、`InventorySummary`、`ProspectTable`、`RecommendationReasons`、`CompanyDrawer`、`ContactPointActions`、`ActivityForm`、`AcquisitionProgress`。
- 电话/邮箱一键复制；Email 复用发送基础设施。V1 不承诺浏览器内拨号。
- 记录结果时必须选择 6 类之一；“拒绝联系”额外选择当前产品或企业全局范围。

## 4. 数据模型

所有业务表使用 UUID、`created_at`、`updated_at`；时间统一 UTC，API 返回 ISO 8601。枚举在应用层和数据库约束中双重限定。

| 表 | 关键字段/约束 | 用途 |
| --- | --- | --- |
| `logistics_products` | `owner_id`, `product_name`, `destination_country`, `transport_mode`, `description`, `status` | 物流产品 |
| `product_inventory_targets` | `product_id`, `customer_type`, `target_count`; unique(product, role) | 产品 × 角色的目标待开发库存 |
| `prospects` | 标准名、展示名、省市地址、官网、业务描述、`global_do_not_contact_at/reason` | 全局企业主档 |
| `prospect_roles` | `prospect_id`, `role`; unique(prospect, role) | 多角色集合 |
| `prospect_identities` | 类型、标准化值、来源、置信度；unique(type, normalized_value)（可按类型调整） | 名称/域名/电话等实体解析线索 |
| `contacts` | `prospect_id`, name, title | 具体联系人 |
| `contact_points` | `prospect_id`, `contact_id?`, type, raw/normalized value, source_url, found_at, validation_status, is_valid | 企业级或个人联系方式 |
| `evidences` | `prospect_id`, `product_id?`, type, country/region, description, source_url, source_type, found_at, expires_at? | 可追溯事实 |
| `product_matches` | `product_id`, `prospect_id`, `customer_type`, relevance_band, reason_snapshot, calculated_at, rule_version; unique(product, prospect, role) | 可重算的匹配候选缓存，不是永久分数 |
| `product_prospects` | `product_id`, `prospect_id`, `customer_type`, added_at; unique(product, prospect, role) | 实际潜客工作集 |
| `product_suppressions` | `product_id`, `prospect_id`, reason, created_by/at; unique(product, prospect) | 产品范围拒绝联系/停止开发 |
| `contact_activities` | 企业、产品、角色、联系人/点位、channel、result、note、occurred_at、next_follow_up_at、created_by | 联系结果事实源 |
| `acquisition_runs` | product、role、requested_gap、status、stage、stop_reason、统计、幂等键 | 一次补客工作流 |
| `acquisition_batches` | run、provider、capability、cursor、状态、输入/输出计数、错误 | 可恢复批次 |
| `discovery_records` | run、batch、product、role、provider、source_type、query_text/group、city、rank、source_url、referrer_id、prospect_id?、resolution_status/reason、discovered_at | 企业发现与官网定位链路；去重后仍保留 |
| `provider_records` | provider、external_id、source_url、payload_hash、raw_payload/retained_metadata、fetched_at；unique(provider, external_id/payload_hash) | 原始供应商记录、幂等与审计，不替代发现链路 |

### 4.1 核心对象关系

```text
LogisticsProduct ──< ProductInventoryTarget
       │
       ├──< ProductMatch >── Prospect ──< ProspectRole
       └──< ProductProspect >──┤       ├──< Contact ──< ContactPoint
                               │       └──< Evidence
                               ├──< ContactActivity
                               └──< DiscoveryRecord >── AcquisitionRun
```

### 4.2 库存计算

`待开发`必须同时满足：存在 `ProductProspect`；当前角色准入成立；不存在当前产品 suppression 和企业全局 DNC；在该 `product + prospect + customer_type` 下不存在任何已发生的首次 `ContactActivity`。`已联系`按存在 ContactActivity 计算。`缺口 = max(target_count - 待开发, 0)`。调低目标只改变缺口，不删除任何记录。

### 4.3 Evidence 与新鲜度

- Evidence 去重键建议为 `(prospect_id, product_id|null, type, country_code|null, region_code|null, normalized_source_url, content_fingerprint)`。
- `source_type` 至少包括 `public_web`、`provider`、`sales_verified`。
- 匹配规则按证据类型配置新鲜度衰减；原始 Evidence 不因降权删除。
- 推荐理由由规则产生结构化 code + 文案参数 + Evidence IDs，接口同时返回来源链接。

## 5. Product Matching

匹配分为准入和排序两步：

1. 准入：同行需 freight_forwarder 角色 + 有效可触达点；出口货主需 exporter 角色 + 强/明显出口证据 + 有效可触达点。
2. 排序：输出 `strong / medium / general / deprioritized` 等解释性档位，不向用户显示 0～100 黑盒分。

同行规则优先“国际货运能力 + 资源互补”；相邻区域为正向信号；同线路庄家/一级代理等降序但不删除。出口货主按真实目的国出口、目的国市场、区域市场、有数据依据的品类关系、普通出口企业排序，再综合具体联系人、职位和联系方式可操作性。

`product_matches` 是可重建投影。新增企业或关键 Evidence 后发出 `prospect.fact_changed`，异步重算所有启用产品；只产生候选，不自动加入已满产品池。

## 6. 潜客发现具体实现方案

潜客发现不实现为“给 AI 一句话，让 AI 自己搜索”。它由可记录、可重放、可评估的 `SearchPlan` 驱动。一个计划只服务一次 `产品 × 客户角色 × 库存缺口`，但发现的企业事实写入全局企业库。

### 6.1 发现对象与中间数据

```text
SearchPlan
- product_id / customer_type / gap
- strategy_version
- query_groups[]
- source_groups[]
- candidate_budget / stop_policy

SearchQuery
- query_text
- query_group       base / destination / region / source_site
- city? / page_cursor?
- priority / status

DiscoveryHit
- query_id / provider / title / snippet / url / rank

DiscoveryRecord
- run_id / batch_id / product_id / customer_type
- provider / source_type / query_text / query_group / city / rank
- source_url / referrer_record_id / discovered_at
- prospect_id? / resolution_status / rejection_reason?

CompanySeed
- candidate_name / website / source_url
- possible_role / location
- raw_evidence[]
```

`DiscoveryHit` 是 Provider 适配器的瞬时结果，不是潜客；接收后立即幂等落为 `DiscoveryRecord`。只有经过企业识别后才生成/合并 Prospect；只有满足角色准入并获得有效 ContactPoint 后才进入可用产品池。

### 6.2 总体补客算法

```text
计算待开发缺口
  ↓
消费企业库强/中匹配候选
  ↓ 仍有缺口
消费企业库其他合格候选
  ↓ 仍有缺口
生成 SearchPlan
  ↓
按优先级执行一小批 Query / Source
  ↓
网页结果 → 企业识别 → 去重 → 资格判断
  ↓
官网完整富化 → Evidence → 联系方式发现与校验
  ↓
全局企业库 Upsert → 全产品重新匹配 → 当前池入池
  ↓
重新计算缺口和本批产出率，决定下一批或停止
```

不是先一次性生成数千条搜索任务。每批完成后用真实漏斗决定下一批规模，避免库存已经补足后仍继续付费搜索和抓取。

### 6.3 国内同行货代搜索设计

同行同时执行“基础覆盖”和“产品相关”两组搜索。

#### A. 基础覆盖组

业务词：

```text
国际货运代理 | 国际货代 | 国际物流 | 国际海运 | 海运货代
freight forwarder | international logistics | shipping agent
```

城市由系统分批展开，不让用户选择。首批城市建议按货代密度配置，例如深圳、广州、上海、宁波、义乌、厦门、青岛、天津；后续城市是系统维护的 Search Strategy 数据，不写死在业务代码。

示例：

```text
深圳 国际货运代理 公司
广州 国际海运 货代 联系方式
宁波 freight forwarder
上海 international logistics company
```

#### B. 产品相关组

从 `destination_country + transport_mode` 生成目的国中文名、英文名、所属区域和运输方式同义词。

委内瑞拉海运示例：

```text
委内瑞拉 海运 货代
Venezuela freight forwarder China
拉美 海运 货代
南美 国际物流 公司
委内瑞拉 专线 国际货运代理
```

韩国海运示例：

```text
韩国 海运 货代
Korea freight forwarder China
中韩 国际物流
韩国 专线 国际货运代理
东亚 海运 货代
```

#### C. 排除与保留

查询级排除词用于减少明显噪声，例如招聘、司机、搬家、同城配送、物流园、培训、快递网点；结果级分类再次排除纯国内物流、媒体文章、招聘页、聚合列表页。排除词不能过滤“同线路庄家”，后者仍是货代企业，只在匹配排序中降级。

#### D. 同行资格识别

页面或官网至少出现一类国际货运事实：国际货代/国际物流、海运/空运/跨境运输、NVOCC/订舱/报关等。仅出现“物流”而无国际业务证据时保持后台候选，不进入可用池。之后必须找到一个通过基础校验的电话、手机或 Email。

### 6.4 国内出口货主搜索设计

出口货主不使用“城市 + 工厂”全国盲搜，SearchPlan 按来源建立候选池。

#### A. P0 来源组

| 来源 | Discovery 方法 | 主要准入 Evidence | 联系方式路径 |
| --- | --- | --- | --- |
| 国际 B2B 中国供应商 | 合法 API、授权数据或可访问的公开供应商页 | `international_b2b`、供应商国家=中国、产品 | 供应商页 → 官网 → Contact 页 |
| 出口型展会 | 官方/授权参展商目录，按届次和行业遍历 | `export_exhibition`、展会名称与届次 | 参展商页 → 官网 → Contact 页 |
| 企业官网/公开网络 | 搜索引擎的来源限定和主题搜索 | export/global/overseas market 等 | 官网 contact/about/team 页面 |

具体网站名称和采购方式在 Provider 技术验证时选择，但输入、输出和漏斗口径保持一致，避免供应商更换导致业务层重写。

#### B. 官网/公开网络查询模板

先寻找“有出口事实的企业”，再用目的国增强排序：

```text
中国 supplier "global market" 联系方式
中国 manufacturer "overseas market"
site:.cn "export department" manufacturer
site:.cn "international sales" 产品
```

委内瑞拉增强查询：

```text
中国 supplier Venezuela
manufacturer "Venezuela market" China
出口 委内瑞拉 企业 联系方式
中国供应商 拉美 市场
```

韩国增强查询：

```text
中国 supplier Korea
manufacturer "Korea market" China
出口 韩国 企业 联系方式
中国供应商 韩国 经销商
```

目的国查询只用于优先发现和排序。没有公开 Venezuela/Korea 信息、但出口证据充分且可触达的企业仍可进入普通出口货主候选。

#### C. 出口资格识别

强证据直接确认 exporter 角色：国际 B2B 中国供应商、出口型展会参展商、可靠贸易记录、官网明确 export/global market。明显经营信号需要至少一项来源清晰的事实，例如 International Sales 部门、海外经销网络、多语言海外营销站或 export@ 邮箱。英文公司名、外贸城市、产品“看起来适合出口”等弱信号不能单独准入。

### 6.5 Query Generator 的实现

Query Generator 使用受版本管理的词典和组合规则，不直接让大模型自由生成最终查询。

```python
def build_queries(product, customer_type, strategy):
    destination = country_terms(product.destination_country)
    regions = region_terms(product.destination_country)
    modes = transport_terms(product.transport_mode)
    if customer_type == "freight_forwarder":
        return base_forwarder_queries(strategy.cities) + \
               route_queries(destination, regions, modes)
    return exporter_source_queries(strategy.export_sources) + \
           exporter_market_queries(destination, regions)
```

大模型可用于从页面文本提取候选公司名、业务事实和市场国家，但所有结果必须通过结构化 Schema 校验并绑定原文片段和 source_url；不得让模型凭常识生成不存在的企业或出口事实。

### 6.6 Discovery / Enrichment Provider

```python
class DiscoveryProvider(Protocol):
    async def discover(self, query: SearchQuery, cursor: str | None) -> DiscoveryPage: ...

class EnrichmentProvider(Protocol):
    capabilities: set[Capability]
    async def enrich(self, company: CompanySeed) -> EnrichmentResult: ...
```

第一阶段至少拆为：

- `WebSearchDiscoveryProvider`：返回搜索结果标题、摘要、URL、排名，不直接写 Prospect；
- `B2BSupplierDiscoveryProvider`：返回中国供应商候选和出口 Evidence；
- `ExhibitorDiscoveryProvider`：按展会/届次遍历参展企业；
- `WebsiteEnrichmentProvider`：抓取首页及高价值内页，提取企业、市场、产品、业务和联系方式；
- `ContactEnrichmentProvider`：当官网联系方式不足时才调用额外补全服务。

官网抓取优先队列：主页 → Contact/联系我们 → About/关于我们 → Products/业务 → Market/Global/Export → Team。限制同域页数和正文大小，robots/条款禁止时不抓取。

### 6.7 联系方式发现

联系方式按成本从低到高补全：

1. Discovery 来源页已公开的电话/邮箱；
2. 官网首页、页头页尾和 Contact 页面；
3. About/Team 页面中的具体联系人；
4. 合法的联系人补全 Provider。

页面提取同时记录联系人附近文本，用于判断姓名和职位；无法建立归属的电话/邮箱保存为企业级 ContactPoint。邮箱/电话通过基础格式和占位值校验后才能计算为可用潜客。

### 6.8 批次规模、产出估算与停止条件

系统用历史漏斗估算为补足缺口需要发现多少候选：

```text
预计候选量 = 剩余缺口 ÷ 最近可用潜客产出率 × 安全系数
```

例如出口货主缺口 100，最近 500 个候选最终产出 50 个可用潜客，产出率 10%，安全系数 1.2，则计划最多处理约 1,200 个新候选，但仍以 50～100 个候选为一批动态执行，不一次性全部搜索。

停止条件满足任一即可：

- 待开发库存达到目标；
- 本轮配置的候选预算或 Provider 配额耗尽；
- 所有 Query/source cursor 已耗尽；
- 连续 N 批（建议默认 3，可配置）没有新增可用潜客；
- 单个可用潜客成本超过配置上限；
- 用户取消；
- Provider 持续失败并触发熔断。

停止原因写入 `acquisition_run.stop_reason`，向用户返回“本次新增多少、仍缺多少、为何停止”，绝不降低准入标准凑数。

### 6.9 异步任务拆分

```text
plan_acquisition
  → execute_discovery_batch
  → resolve_company_seeds
  → qualify_company_batch
  → enrich_company_batch
  → enrich_contact_batch
  → validate_and_upsert
  → recompute_matches
  → admit_current_product_pool
  → evaluate_next_batch_or_finish
```

Celery 每阶段接收 ID 列表而非整份网页正文。业务权威状态保存在 MySQL；Redis 只用于队列、限流和短期锁。任务至少一次投递下必须幂等，按 `provider + external_id/source_url + payload_hash` 防止重复处理。

### 6.10 来源链路持久化与官网确认

Provider 返回 `DiscoveryHit` 后，系统先写 `ProviderRecord` 和首个 `DiscoveryRecord`，再做页面分类与实体解析。发现页指向目录详情、目录详情再指向官网时，每次跳转新增记录并通过 `referrer_record_id` 相连。最终由域名、企业名称、地址、电话等确定性信号确认官网归属，并把整条链路关联到规范 Prospect。

`resolution_status` 状态转换为：`unresolved → resolved | merged | rejected`。合并企业只更新规范 `prospect_id`/`merged_to_prospect_id`，不删除旧记录；失败结果记录原因与内容哈希，后续同一 Query/URL 可跳过重复解析。`Evidence` 和 `ContactPoint` 通过各自的 `source_url` 或可选 `discovery_record_id` 回指发现节点，但仍按各自事实语义独立存储。

来源链路产生两类查询投影：

- 企业溯源：按时间展示首次/历次来源、Query、落地页、官网确认路径及所属产品任务；
- 渠道漏斗：按 Query 组、城市、Provider、source type 统计 hit、resolved、merged、qualified、contactable、admitted。

## 7. 数据质量与实体解析

### 7.1 联系方式

- Email：trim/lowercase、基本语法、IDN/域名标准化、排除测试/占位地址、标准化值去重。
- 电话：去空格和分隔符、保留国家码、按中国电话/手机号基本长度校验、排除重复数字/占位号。
- `validation_status`: `unchecked / passed_basic / failed_basic`；`is_valid` 保留 `null/true/false` 业务反馈语义，两者不可混为一谈。

### 7.2 企业去重

先确定性、后模糊：统一社会信用代码（若合法取得）/官网主域/标准电话/精确标准名+城市为强匹配；标准名相似度、英文名、地址、邮箱域为候选匹配。模糊合并低于阈值进入人工/后台待判，不自动覆盖。合并需保留 `prospect_merge_log` 和字段来源，支持撤销错误合并。

### 7.3 写入策略

不同来源只做字段级 upsert：空值可补全；新事实追加 Evidence；联系方式按标准值合并并保留多来源；冲突值不静默覆盖，按来源优先级/新鲜度选择展示值并保留 provenance。

## 8. API 设计

统一前缀 `/api/v1`；列表采用 cursor pagination；写接口支持 `Idempotency-Key`；错误体含 `code/message/details/request_id`。

| Method | Path | 说明 |
| --- | --- | --- |
| POST/GET | `/logistics-products` | 创建/列表产品 |
| GET/PATCH | `/logistics-products/{id}` | 详情、编辑、启停 |
| PUT | `/logistics-products/{id}/inventory-targets/{customer_type}` | 修改目标库存 |
| GET | `/logistics-products/{id}/inventory` | 两角色库存、已联系和缺口 |
| GET | `/logistics-products/{id}/prospects?customer_type=&state=` | 产品潜客列表及推荐理由 |
| POST | `/logistics-products/{id}/replenishments` | 幂等启动补客 |
| GET | `/acquisition-runs/{id}` | 阶段、批次、漏斗、停止原因 |
| GET | `/acquisition-runs/{id}/funnel?group_by=` | 按 Query/城市/Provider/来源下钻发现漏斗 |
| POST | `/acquisition-runs/{id}/cancel` | 安全取消未完成批次 |
| GET | `/prospects` | 企业库搜索 |
| GET | `/prospects/{id}` | 主档、角色、Evidence、联系人、匹配产品 |
| GET | `/prospects/{id}/discovery-records` | 首次及历次发现、官网定位和合并链路 |
| POST | `/contact-activities` | 记录 6 类结果与跟进 |
| GET | `/prospects/{id}/activities?product_id=&customer_type=` | 产品语境联系历史 |
| POST | `/outreach/emails` | 向指定 ContactPoint 发邮件并关联语境 |
| POST | `/product-suppressions` | 当前产品拒绝 |
| POST | `/prospects/{id}/global-suppression` | 明确选择后全局 DNC |

并发保护：记录活动与入池用唯一约束；补客启动通过数据库唯一 active key 或 advisory lock；库存接口使用同一查询模块，避免列表与数字口径漂移。

## 9. 安全、合规和可观测性

- 所有企业、联系方式、Evidence 查询按 owner/tenant 隔离；后台任务携带 tenant_id。
- Provider 凭据只存密钥系统/环境变量；日志脱敏邮箱、电话、令牌。
- 保留数据来源、抓取时间、使用依据、Provider 授权方式；遵守 robots、服务条款、频率和个人信息处理要求，具体供应商接入必须单独合规评审。
- 审计产品目标修改、合并、联系方式有效性、拒绝范围和人工 Evidence。
- 指标：发现量、去重后量、角色确认率、出口证据覆盖率、联系方式覆盖率、基础校验通过率、最终可用率、企业库复用命中率、单个可用潜客成本、各阶段耗时/错误率。

## 10. 测试与验收门槛

- 单元：准入、排序理由、库存口径、6 类结果副作用、拒绝范围、联系方式校验、幂等 upsert。
- 集成：Provider contract、发现链路落库、实体合并后来源保留、全流水线断点重试、邮件与 ContactActivity 关联。
- 端到端：创建产品→设定双角色库存→补客→列表/详情→电话/邮件→6 类结果→跟进。
- 必测复用：韩国发现企业同时写入 KR/VE Evidence；韩国产品可入池；委内瑞拉只生成新候选；下次补充时优先消费；不重复抓取、不复制 Prospect。
- 发现验收使用固定样本集和小批真实搜索，分别核对企业真实性、官网确认路径、角色准入、Evidence 来源、联系方式有效率和跨产品复用结果。

## 11. 待技术评审决策点

业务规则不重开讨论，仅需确认实现选择：MySQL 当前版本与数据库版本管理工具（建议 Alembic）、租户边界、首批合法 Discovery/Enrichment Provider、首批城市与来源清单、补客批大小/成本上限/停止阈值，以及任务进度采用 SSE 还是短轮询。确认这些项目后才进入正式 V1 业务代码开发。
