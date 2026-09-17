# V1 数据源验证报告 01：公开数据冷启动

> 验证日期：2026-09-17
> 状态：第一轮公开页面 Spike
> 目的：验证在没有平台账号、没有展会资源的前提下，V1 是否能发现出口货主及近期物流需求。本文不代表正式接入或合规批准。

## 1. 本轮范围

使用两个业务语境：

- 委内瑞拉海运；
- 韩国海运。

验证四类来源：

1. 中国制造网公开供应商目录；
2. Alibaba Supplier 公开入口；
3. 香港贸发局香港国际创科展官方展商目录；
4. 福步外贸论坛公开搜索。

本轮只读取公开页面，不注册账号、不绕过验证码、不发送询盘、不采集私人消息。结果用于验证 Provider 可行性，不直接导入正式潜客池。

## 2. 结论摘要

| 来源 | 有效样本 | 能稳定获得 | 主要缺口 | 建议分级 |
| --- | ---: | --- | --- | --- |
| 中国制造网 | 20 家企业 | 企业名、平台主页、主营产品；多数页面有企业类型/城市等结构化字段 | 20 家均未公开显示 Email；独立官网需二次搜索；平台联系动作存在登录语境 | P0 Discovery，必须接 Website Enrichment |
| Alibaba Supplier | 0 家 | 公开说明页展示供应商资料能力 | 实际供应商搜索在当前环境触发验证码，无法形成诚实样本 | P0 候选；账号/授权/人工验证后再决定 |
| 香港贸发局展商目录 | 20 条展商 | 企业名、国家/地区、展位、展区、稳定详情 URL | 所选创科展的中国内地出口货主密度低；详情联系方式不完整 | Provider 形态可用，具体展会必须先筛选 |
| 福步论坛 | 20 条帖子 | 标题、摘要、发布日期、帖子 URL、路线/运输需求文本 | 大量旧帖、货代广告、资讯和匿名用户；企业主体与业务联系方式需外部确认 | P1 时效性需求信号，不作企业主档来源 |

关键结论：公开数据足以启动“企业发现”和“需求信号发现”，但单一来源无法直接生产可用潜客。必须执行企业识别、官网定位、联系方式富化和来源交叉确认。

## 3. 中国制造网验证

### 3.1 来源

- 公开供应商目录：<https://www.made-in-china.com/manufacturers/directory.html>
- 目录页面当次显示 675 家供应商、2,025 个产品；数量是页面实时值，不作为固定产品承诺。

### 3.2 20 家样本

| # | 企业 | 平台主页 |
| ---: | --- | --- |
| 1 | Quanzhou Fuwei Machinery Co., Ltd | <https://fwmach.en.made-in-china.com/> |
| 2 | Easton Hotel Supplies Co., Ltd. | <https://eastonhk.en.made-in-china.com/> |
| 3 | Shenyang Ezd Sign Co., Ltd | <https://ezdsign.en.made-in-china.com/> |
| 4 | Yangzhou Mingchi Hotel Products Co., Ltd | <https://yzmingchi.en.made-in-china.com/> |
| 5 | Alumi Industrial Co., Ltd. | <https://alumihk.en.made-in-china.com/> |
| 6 | Jiangsu Hanbang Intelligent System Integration Co., Ltd. | <https://hobovar.en.made-in-china.com/> |
| 7 | Guangzhou Mingzhou Industrial Co., Ltd. | <https://vegcork.en.made-in-china.com/> |
| 8 | Ritscher Paper Products Limited | <https://ritscher.en.made-in-china.com/> |
| 9 | Domay Homeware Limited | <https://www.made-in-china.com/showroom/fda900509239e1cd/> |
| 10 | Shanghai Pudong Nench Hotelleather Factory | <https://hotelleather.en.made-in-china.com/> |
| 11 | Ningbo Haituo Machinery Technology Co., Ltd | <https://haituoplasticmachine.en.made-in-china.com/> |
| 12 | Nabowan (Shandong) Machinery Manufacturing Co., Ltd. | <https://nabowan.en.made-in-china.com/> |
| 13 | Hubei Best Crane Co., Ltd. | <https://hbqzcrane.en.made-in-china.com/> |
| 14 | SHENZHEN WEIGUAN SMART DISPLAY TECHNOLOGY CO., LTD. | <https://tyalux.en.made-in-china.com/> |
| 15 | Shenzhen Uniview Commercial Display Co., Ltd. | <https://univiewlcd.en.made-in-china.com/> |
| 16 | Rondos Pump Industry Co., Ltd. | <https://rondos-pump.en.made-in-china.com/> |
| 17 | Anhui Erybay Sign Co., Ltd. | <https://erybaysign.en.made-in-china.com/> |
| 18 | Shenzhen Zhongcheng Yuntouch Technology Co., Ltd. | <https://zooctouch2.en.made-in-china.com/> |
| 19 | Dongguan Kingone Technology Co., Ltd. | <https://kingonevision.en.made-in-china.com/> |
| 20 | Dongguan Yihui Hydraulic Machinery Co., Ltd. | <https://yihuihydraulic.en.made-in-china.com/> |

### 3.3 观察结果

- 20/20 可以取得明确企业名和稳定平台主页；
- 目录页可直接取得主营产品，多数企业同时展示企业类型、城市、OEM/ODM、认证或人员规模等字段；
- 8/20 抽查页面出现 Main Markets、Export Percentage 或国际贸易条款相关结构，可作为进一步提取目标，但不能直接推导委内瑞拉/韩国市场；
- 0/20 在公开正文中发现可直接使用的 Email；
- 20 个页面都带登录入口，平台内 Contact Now 不能等同于公开电话/邮箱；
- 未发现可靠的独立企业官网外链，官网需要以企业名称、地址、电话等二次定位。

### 3.4 判断

中国制造网适合担当 `B2BSupplierDiscoveryProvider`，其平台供应商身份可以形成 exporter 准入 Evidence。它不能单独完成 ContactPoint 生产，应继续执行官网定位和 Contact Enrichment。

## 4. Alibaba Supplier 验证

### 4.1 来源

- 供应商说明入口：<https://suppliers.alibaba.com/>
- 使用条款：<https://rule.alibaba.com/>

公开说明页表示供应商资料可包含企业信息、认证、生产能力、质量管理、研发和买家评价等字段。但本轮进入实际供应商搜索时，页面触发验证码拦截，因此没有取得可审计的企业样本。

### 4.2 判断

- 不把公开宣传的“20 万+供应商”当成 V1 可采数量；
- 不绕过验证码，不虚构20条样本；
- 下一阶段可由用户注册普通账号后进行人工可见字段验证，或直接咨询官方 API/数据合作；
- 在验证访问方式、条款和字段产出前，Alibaba 只能保持 P0 候选，不能进入开发承诺。

## 5. 官方展商目录验证

### 5.1 来源

- 香港贸发局香港国际创科展参展商目录：<https://www.hktdc.com/event/innoex/tc/exhibitor-list>
- 目录当次显示 590 个结果，并明确提示只包括已提供完整资料的参展商。

### 5.2 前20条样本

| # | 展商 | 详情来源 |
| ---: | --- | --- |
| 1 | Tradelink Electronic Commerce Limited | <https://www.hktdc.com/event/innoex/tc/exhibitor/1S0060PXK?fairCode=innoex&locale=tc> |
| 2 | Hong Kong Science and Technology Parks Corporation | <https://www.hktdc.com/event/innoex/tc/exhibitor/1S006118B?fairCode=innoex&locale=tc> |
| 3 | WildFaces Technology Limited | <https://www.hktdc.com/event/innoex/tc/exhibitor/1S0060PWN?fairCode=innoex&locale=tc> |
| 4 | Hong Kong Telecommunications (HKT) Limited | <https://www.hktdc.com/event/innoex/tc/exhibitor/1S0060R8L?fairCode=innoex&locale=tc> |
| 5 | Hong Kong Applied Science and Technology Research Institute Company Limited | <https://www.hktdc.com/event/innoex/tc/exhibitor/1S0060Q24?fairCode=innoex&locale=tc> |
| 6 | Macau Productivity and Technology Transfer Center | <https://www.hktdc.com/event/innoex/tc/exhibitor/1S00610VF?fairCode=innoex&locale=tc> |
| 7 | The Hong Kong Polytechnic University | <https://www.hktdc.com/event/innoex/tc/exhibitor/1S0060R9I?fairCode=innoex&locale=tc> |
| 8 | Hi-Think Technology International Limited | <https://www.hktdc.com/event/innoex/tc/exhibitor/1S0060QP7?fairCode=innoex&locale=tc> |
| 9 | Hikvision Technology Pte. Ltd. | <https://www.hktdc.com/event/innoex/tc/exhibitor/1S0060QOA?fairCode=innoex&locale=tc> |
| 10 | B4B Limited | <https://www.hktdc.com/event/innoex/tc/exhibitor/1S0061AZT?fairCode=innoex&locale=tc> |
| 11 | Digital Policy Office | <https://www.hktdc.com/event/innoex/tc/exhibitor/1S0060QLJ?fairCode=innoex&locale=tc> |
| 12 | Hong Kong Cyberport Management Company Limited | <https://www.hktdc.com/event/innoex/tc/exhibitor/1S0060QKM?fairCode=innoex&locale=tc> |
| 13 | Hong Kong-Shenzhen Innovation and Technology Park | <https://www.hktdc.com/event/innoex/tc/exhibitor/1S0060QMG?fairCode=innoex&locale=tc> |
| 14 | Huawei International Co Limited | <https://www.hktdc.com/event/innoex/tc/exhibitor/1S0060RKL?fairCode=innoex&locale=tc> |
| 15 | Innobator (Hong Kong) Limited | <https://www.hktdc.com/event/innoex/tc/exhibitor/1S0061B0P?fairCode=innoex&locale=tc> |
| 16 | Smart City Consortium Limited | <https://www.hktdc.com/event/innoex/tc/exhibitor/1S0060QHV?fairCode=innoex&locale=tc> |
| 17 | AEROFUGIA | <https://www.hktdc.com/event/innoex/tc/exhibitor/1S006116H?fairCode=innoex&locale=tc> |
| 18 | Hong Kong Generative AI Research and Development Center Limited | <https://www.hktdc.com/event/innoex/tc/exhibitor/1S0060Q8M?fairCode=innoex&locale=tc> |
| 19 | Logistics and Supply Chain MultiTech R&D Centre Limited | <https://www.hktdc.com/event/innoex/tc/exhibitor/1S0060Q17?fairCode=innoex&locale=tc> |
| 20 | British Consulate General Hong Kong | <https://www.hktdc.com/event/innoex/tc/exhibitor/1S0060Q5V?fairCode=innoex&locale=tc> |

### 5.3 观察结果

- 20/20 有企业/机构名称、国家/地区、展位、展区和稳定详情链接；
- 详情页抽查5条，5条都出现 Website 字段或官网路径，但均未在公开正文中发现 Email；
- 名单包含政府机构、园区、大学、领事机构等，并非所有参展者都是出口货主；
- 前20条以香港机构为主，只有极少量中国内地生产/企业信号，不适合作为“国内出口货主”的首批高产出展会；
- 证明了官方展商目录 Provider 的技术形态可行，同时证明“有公开展商名录”不等于“适合当前客户类型”。

### 5.4 判断

展会接入前必须增加 `TradeShowQualification`：国内生产/供应商占比、B2B属性、出口属性、参展企业类型、公开目录完整度、官网/联系方式覆盖率。香港国际创科展可作为 Provider 技术样本，但不建议作为 V1 首批出口货主生产来源。

## 6. 福步论坛验证

### 6.1 来源与查询

- 搜索入口：<https://fobshanghai.com/search.php>
- 查询：`委内瑞拉 海运`、`韩国 海运`
- 未登录状态每个查询约100条结果，页面说明当前权限可查看前50条；本轮读取每个查询首页10条，共20条。

### 6.2 样本分类

| 查询 | 样本 | 直接运输需求 | 货代广告/供给 | 资讯/讨论/其他 | 近12个月明显需求 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 委内瑞拉 海运 | 10 | 4 | 3 | 3 | 1 |
| 韩国 海运 | 10 | 3 | 1 | 6 | 0 |
| 合计 | 20 | 7 | 4 | 9 | 1 |

“直接运输需求”只表示帖子文本中出现具体货物、港口、柜型或询价，不表示已识别真实企业。20条中多数发布于2007～2021年，说明综合相关度排序不适合直接获客；必须按发布时间排序并设置新鲜度。

部分可追溯示例：

- 委内瑞拉拼箱需求：<https://bbs.fobshanghai.com/thread-8617803-1-1.html>
- 南沙到委内瑞拉40尺柜需求：<https://bbs.fobshanghai.com/thread-9266434-1-1.html>
- 韩国釜山滑石粉出口需求：<https://bbs.fobshanghai.com/thread-7001186-1-1.html>
- 深圳到韩国釜山小柜询价：<https://bbs.fobshanghai.com/thread-2934201-1-1.html>

### 6.3 判断

- 论坛能发现高意向、强目的国、强运输方式信号；
- 帖子作者经常是匿名用户，且货主、货代、广告商和资讯转载混在一起；
- 论坛中的个人 QQ、微信或手机号不能未经主体确认直接成为企业 ContactPoint；
- `logistics_demand_signal` 默认有效期建议30～90天，超过一年只作历史 Evidence，不进入优先开发列表；
- 论坛应使用 `ForumSignalProvider`，先产出 Signal/CompanySeed，再通过公司名、官网或公开企业资料完成实体确认；不能直接 Upsert 为可用 Prospect。

## 7. 对 V1 技术方案的直接影响

### 7.1 Provider 输出不能统一

至少区分：

- `CompanySeed`：B2B、展会、协会等产生的企业候选；
- `DemandSignal`：论坛、询价、招聘等产生的有时效行为线索；
- `Evidence`：完成企业归属确认后的出口/市场/需求事实；
- `ContactPoint`：经过来源、主体和基础质量校验的业务联系方式。

论坛帖子不能绕过 CompanySeed/Entity Resolution 直接成为 Prospect；平台的 Contact Now 按钮也不能计算为 phone/email 可触达。

### 7.2 新增来源准入评估

每个 Provider 上线前记录：

- 访问方式：公开、账号、付费、API、授权文件；
- 条款/robots/频率限制；
- 企业主体识别率；
- exporter 证据强度；
- 官网确认率；
- 公开 ContactPoint 覆盖率；
- 新鲜度及过期策略；
- 目标国家/区域信号覆盖率；
- 最终可用潜客率与单客成本。

### 7.3 首批优先级调整

1. 中国制造网公开目录：进入下一轮官网富化验证；
2. 另选1～2个国内制造/消费品出口企业密集、目录公开的展会，不继续扩大创科展样本；
3. 福步论坛：只实现时效性 Signal 规则，先不承诺规模产出；
4. Alibaba：待账号或官方授权路径确认后再做20条样本；
5. 联系方式覆盖率必须在官网富化后统计，不能用平台按钮代替。

## 8. 本轮限制

- 本轮不是正式爬虫性能测试，只验证公开可见字段和数据语义；
- 尚未对中国制造网20家企业逐一完成独立官网定位，因此不能报告最终可联系率；
- 尚未使用任何付费贸易数据或联系人服务；
- 未验证登录账号后的字段、配额和平台条款；
- 样本量只适合决定下一轮验证方向，不足以估算全量单客成本。

## 9. 下一轮执行建议

从中国制造网20家样本中选择企业名称清晰、产品明确的10家，执行“企业名搜索 → 官网归属确认 → Contact/About → Email/phone → VE/KR/区域 Evidence”的完整链路；同时选择一个中国内地制造企业占比高的官方展商目录做同样的10家富化。两组完成后才能回答公开渠道的最终可用潜客率，以及是否值得注册/购买平台账号。
