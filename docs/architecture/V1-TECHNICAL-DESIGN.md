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
| `provider_records` | provider、external_id、source_url、payload_hash、raw_payload、fetched_at；unique(provider, external_id/payload_hash) | 来源追踪与幂等 |

### 4.1 核心对象关系

```text
LogisticsProduct ──< ProductInventoryTarget
       │
       ├──< ProductMatch >── Prospect ──< ProspectRole
       └──< ProductProspect >──┤       ├──< Contact ──< ContactPoint
                               │       └──< Evidence
                               └──< ContactActivity
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

## 6. Provider 与异步流水线

### 6.1 接口

```python
class DiscoveryProvider(Protocol):
    async def discover(self, query: DiscoveryQuery, cursor: str | None) -> DiscoveryPage: ...

class EnrichmentProvider(Protocol):
    capabilities: set[Capability]
    async def enrich(self, company: CompanySeed) -> EnrichmentResult: ...
```

Capability 使用 `company_profile`、`export_evidence`、`market_evidence`、`contact` 等；Provider 只声明能力，不决定最终准入。

### 6.2 补客工作流

1. 原子创建 `acquisition_run`，同一产品/角色只允许一个 active run。
2. 重算库存缺口；若为 0 直接 `no_gap` 停止。
3. 从 `product_matches` 消费未入池的强/中相关且合格候选。
4. 再消费企业库其他合格、未入池候选。
5. 缺口仍存在才生成货代领域 Search Strategy，分批调用 Discovery。
6. 每批依次执行实体解析、资格判断、完整富化、联系人补全、确定性校验、全局 upsert、全产品匹配。
7. 当前产品按排序和剩余缺口写入 `product_prospects`；达到目标或搜索空间耗尽停止。

Celery Canvas 可按 run 编排小批任务；每个阶段以数据库状态为准，任务至少一次投递下必须幂等。重试采用指数退避 + 抖动；Provider 级限流、熔断与配额；失败批次进入可人工重试状态。不要在 Celery result backend 保存业务权威状态。

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
| POST | `/acquisition-runs/{id}/cancel` | 安全取消未完成批次 |
| GET | `/prospects` | 企业库搜索 |
| GET | `/prospects/{id}` | 主档、角色、Evidence、联系人、匹配产品 |
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
- 集成：Provider contract、实体合并、全流水线断点重试、邮件与 ContactActivity 关联。
- 端到端：创建产品→设定双角色库存→补客→列表/详情→电话/邮件→6 类结果→跟进。
- 必测复用：韩国发现企业同时写入 KR/VE Evidence；韩国产品可入池；委内瑞拉只生成新候选；下次补充时优先消费；不重复抓取、不复制 Prospect。
- 迁移演练使用生产数据副本并输出对账报告；V0 表只读保留，回滚不删除 V0 数据。

## 11. 待技术评审决策点

业务规则不重开讨论，仅需确认实现选择：MySQL 当前版本与迁移工具（建议 Alembic）、租户边界、首批合法数据 Provider、补客批大小与配额、SSE 或短轮询、V0 数据迁移的质量阈值。确认这些项目后才进入正式 V1 业务代码开发。
