# V1-02 潜在客户与联系方式【已确认】

> 状态：已确认  
> 版本：V1  
> 当前范围：国内拓客；当前确认的客户角色为国内同行货代与出口货主。

## 1. Prospect 定义

**潜在客户 Prospect = 企业本身，不是具体联系人。** 同一家企业在全系统保持唯一，不因不同物流产品重复创建。

## 2. Prospect 基础字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | ID | 企业唯一标识 |
| company_name | 文本 | 公司名称 |
| company_types | 多角色集合 | 当前支持 freight_forwarder / exporter，可同时具备 |
| province | 文本/行政区字典 | 省 |
| city | 文本/行政区字典 | 市 |
| address | 文本，可空 | 企业地址 |
| website | URL，可空 | 企业官网 |
| business_description | 文本，可空 | 主营业务描述 |
| created_at | 时间 | 系统字段 |
| updated_at | 时间 | 系统字段 |

### company_types 第一版
- `freight_forwarder`：国内同行货代
- `exporter`：出口货主

企业可以同时拥有多个角色。例如某供应链公司既做国际货代，又经营自己的出口贸易，则同时属于 freight_forwarder 与 exporter。Prospect、Contact、ContactPoint 仍只维护一份。

“出口货主”可以包含工厂、工贸一体企业、外贸公司以及其他实际出口企业。

## 3. 不直接放在 Prospect 上的数据

- 联系方式：使用 Contact / ContactPoint；
- 产品相关性：不存永久 match_score；
- 出口/产品相关证据：使用 Evidence 保存来源与事实；
- 针对某物流产品的联系结果：属于 ProductProspect / ContactActivity 语境，不是企业全局状态。

## 4. Contact

```text
Contact
- id
- prospect_id
- name
- title
- created_at
- updated_at
```

`title` 可参与联系方式可操作性排序，例如外贸经理、国际业务负责人、物流/供应链负责人等。

## 5. ContactPoint

```text
ContactPoint
- id
- prospect_id
- contact_id?      # 空 = 公司级联系方式
- type             # mobile / phone / email
- value
- source_url
- found_at
- is_valid?        # null / true / false
- created_at
- updated_at
```

公司总机、sales@、info@ 等通用邮箱也属于可触达方式。

## 6. 微信处理原则

微信暂不作为第一版核心类型。“手机号可能可以添加微信”不能在没有明确证据时写成微信事实。

## 7. 来源与数据质量

每条 ContactPoint 保留 source_url 与 found_at。入池前至少进行电话/手机号格式、明显占位号码、Email 格式、测试邮箱/域名、标准化重复值等确定性校验。

## 8. 联系方式有效性

- `null`：尚未由业务反馈确认
- `true`：已确认有效
- `false`：已确认无效

联系方式无效作用于具体 ContactPoint，不等于整个 Prospect 无效。企业如果还有其他有效电话或邮箱，仍然可触达。

## 9. 可用潜客准入

### 国内同行货代
国际货代角色 + 至少一种通过基础质量校验的可触达联系方式。

### 出口货主
出口货主角色 + 足够出口证据/明显出口经营信号 + 至少一种通过基础质量校验的可触达联系方式。

不额外存储 is_usable，按企业角色、Evidence 与 ContactPoint 实时判断。

## 10. “目标库存”的正确含义

产品潜客池的目标数量不是“数据库最多保存多少家企业”，而是：

> **希望当前产品 × 客户角色下，保持多少家尚未联系、可立即开发的新客户。**

例如：

```text
目标库存       500
待开发客户     220
已联系客户    1160
库存缺口       280
```

真正决定是否需要补充的是“待开发客户”数量。已联系企业继续保留在产品关系和历史数据中，不删除。

目标库存可以调大或调小，只影响补客参考值：
- 500 → 1000：缺口随之增加；
- 1000 → 500：如果当前待开发仍有 800，不删除多出的 300，只是暂时无需补充。

遵循原则：**调整目标库存绝不删除企业库数据、产品关系或联系历史。**
