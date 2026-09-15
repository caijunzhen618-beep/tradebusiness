# V1-02 潜在客户与联系方式【已确认】

> 状态：已确认  
> 版本：V1  
> 当前范围：国内拓客；目前确认的客户类型为国内同行货代与工厂。

## 1. Prospect 定义

**潜在客户 Prospect = 企业本身，不是具体联系人。**

例如“深圳 ABC 国际物流有限公司”是一个 Prospect。该公司下面可以有多个具体联系人，也可以只有公司电话或通用邮箱。

同一家企业在全系统保持唯一。即使它同时被“委内瑞拉海运”和“南非海运”等不同获客计划发现，也不应重复创建企业记录。

## 2. Prospect 基础字段

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| id | ID | 企业唯一标识 |
| company_name | 文本 | 公司名称 |
| company_type | 枚举 | 当前支持 freight_forwarder / factory |
| province | 文本/行政区字典 | 省 |
| city | 文本/行政区字典 | 市 |
| address | 文本，可空 | 企业地址 |
| website | URL，可空 | 企业官网 |
| business_description | 文本，可空 | 公开资料中获得的主营业务描述 |
| created_at | 时间 | 系统字段 |
| updated_at | 时间 | 系统字段 |

### company_type 第一版
- `freight_forwarder`：国内同行货代
- `factory`：工厂

暂不提前增加贸易公司、跨境电商等尚未由当前真实业务确认的类型。

## 3. 不直接放在 Prospect 上的数据

### 联系方式
一家公司可能有多个电话、多个邮箱、多个联系人，因此不使用 `phone1 / phone2 / email1 / email2` 这类平铺字段。

### 产品相关性
“这家公司对委内瑞拉海运有多相关”不是企业永久属性。同一家公司对不同物流产品的相关性不同，应放在 Prospect 与获客计划的关系或后续相关性数据中，而不是 `prospect.match_score`。

### 来源证据
企业和联系方式可能来自不同公开来源。来源应保留到具体数据证据层，而不是只在 Prospect 上写一个笼统 `source=Google`。

## 4. Contact：具体联系人

Contact 表示企业中的具体个人。

```text
Contact
- id
- prospect_id
- name
- title
- created_at
- updated_at
```

例如：张经理 / 销售经理。

Contact 本身不强制平铺一个手机号和一个邮箱，因为一个人可能拥有多个联系方式。

## 5. ContactPoint：可触达联系方式

ContactPoint 统一表达“怎么联系到企业或联系人”。

```text
ContactPoint
- id
- prospect_id
- contact_id?      # 可空；为空表示公司级联系方式
- type
- value
- source_url
- found_at
- is_valid?        # null / true / false
- created_at
- updated_at
```

### type 第一版枚举
- `mobile`：手机
- `phone`：公司电话/固定电话
- `email`：邮箱

### 企业级与个人级联系方式

`contact_id = null`：公司级联系方式，例如总机、`sales@abc.com`、`info@abc.com`。

`contact_id != null`：属于具体 Contact 的联系方式，例如张经理手机号、张经理个人邮箱。

## 6. 微信处理原则

微信暂不作为第一版核心联系方式类型。

“手机号可能可以添加微信”只是操作建议，不能在没有明确公开证据时把手机号复制成微信号事实。如果数据源明确提供微信号，后续可再扩展联系方式类型。

## 7. 来源证据

每条 ContactPoint 至少保留：
- `source_url`：公开来源地址
- `found_at`：发现时间

原因：联系方式会过期，而且不同数据源质量不同。后续可以根据业务员反馈判断某来源的电话/邮箱有效率。

## 8. 联系方式有效性

第一版采用 nullable Boolean：
- `null`：尚未验证
- `true`：已确认有效
- `false`：已确认无效

业务员确认空号、错误邮箱等情况时，不删除历史数据，而是记录为无效，避免再次推荐并保留数据源质量证据。

## 9. 可用潜客定义【已确认】

**可用潜客 = 符合目标客户类型，并且至少存在一种可触达联系方式的 Prospect。**

第一版以下任意一种均算可触达：
- 手机
- 公司电话
- 个人邮箱
- 公司通用邮箱（包括 `sales@...` / `info@...`）

只有公司名称、地址、官网，但没有上述任何联系方式的企业，不计入“可用潜客”数量。

不额外存储 `is_usable` 状态。可用性通过 Prospect 是否存在可用 ContactPoint 实时计算。

## 10. 对潜客池数量的含义

“潜客池目标 1000”表示目标为 **1000 家可联系的企业**，不是 1000 个联系人，也不是 1000 条搜索结果。

一家公司即使有多个联系人，仍然只计算为一个 Prospect。
