# V1-01 物流产品【已确认】

> 状态：已确认  
> 版本：V1  
> 目标：定义货代获客系统中的“物流产品”对象，为后续客户画像与搜索策略提供稳定的结构化输入。

## 1. 产品定义

**物流产品 = 货代长期、相对稳定、可以对外销售的一组线路 + 运输 + 履约服务能力。**

例如：
- 委内瑞拉海派双清
- 南非海派双清
- 韩国海派包税

物流产品只记录相对稳定的服务能力。客户类型、目标行业、目标货类、搜索关键词、客户匹配分等不属于物流产品，应在后续“客户画像 / 搜索策略 / Lead”中定义。

## 2. 设计原则

1. 创建物流产品要轻量，避免让用户为了获客先填写复杂的物流操作单。
2. 核心业务判断和搜索使用结构化字段，不依赖产品名称文本。
3. 行业术语“海派 / 双清 / 包税”不作为不可拆分的产品类型，而由底层能力字段组合表达。
4. 国家使用标准国家字典（建议 ISO 国家代码），港口使用独立港口基础数据，不在代码中写死普通枚举。
5. 不要求用户穷举“可接货物”。货物种类无限，且商品行业分类与运输属性不是同一维度。
6. 特殊货能力/限制第一版作为可选备注，后续有明确搜索价值或履约价值时再结构化。

## 3. V1 字段

| 字段 | 必填 | 类型 | 示例 | 说明 |
| --- | --- | --- | --- | --- |
| product_name | 是 | 文本（系统默认生成、用户可改） | 委内瑞拉海派双清 | 仅用于展示，不作为搜索判断依据 |
| origin_country | 是 | Country 标准字典 | CN / 中国 | 起运国家 |
| destination_country | 是 | Country 标准字典 | VE / 委内瑞拉 | 目的国家，是找客的重要字段 |
| transport_mode | 是 | 单选枚举 | sea | 主干运输方式 |
| load_types | 否 | 多选枚举 | LCL, FCL | 一个产品可以同时支持散货和整柜 |
| pickup_regions | 否 | 区域集合/文本 | 华南、全国 | 可揽收范围 |
| origin_ports | 否 | Port 基础数据 | Yantian | 实际起运港，可为空 |
| destination_ports | 否 | Port 基础数据 | La Guaira | 目的港，可为空 |
| delivery_regions | 否 | 区域集合/文本 | Caracas | 可派送区域 |
| export_customs | 否 | Boolean | true | 是否提供出口清关 |
| import_customs | 否 | Boolean | true | 是否提供进口清关 |
| last_mile_delivery | 否 | Boolean | true | 是否提供末端派送 |
| tax_mode | 否 | 单选枚举 | included | 税费模式 |
| cargo_notes | 否 | 文本 | 带电可询，危险品不接 | 特殊货能力/限制说明，不做复杂可接货物枚举 |
| status | 是 | 单选枚举 | active | 产品启用状态 |

### 最小必填集合

为了降低创建成本，核心必填字段控制为：

> **产品名称 + 起运国家 + 目的国家 + 运输方式**

其中产品名称由系统自动生成默认值，因此用户通常只需完成三个核心业务选择即可创建产品。

## 4. 枚举定义

### transport_mode 运输方式

- `sea`：海运
- `air`：空运
- `rail`：铁路
- `road`：陆运
- `multimodal`：多式联运

第一版使用单选。复杂运输组合统一归入 multimodal，避免模型过早复杂化。

### load_types 装载方式

多选：
- `LCL`：散货 / 拼箱
- `FCL`：整柜
- `parcel`：快递 / 包裹

### tax_mode 税费模式

- `excluded`：不包税
- `included`：包税
- `optional`：可选

### status 产品状态

- `active`：启用
- `inactive`：停用

### Boolean 字段

以下字段不创建业务枚举，直接使用 Boolean：
- export_customs
- import_customs
- last_mile_delivery

## 5. 行业术语的结构化表达

### 海派

`transport_mode = sea` + `last_mile_delivery = true`

### 双清

`export_customs = true` + `import_customs = true`

### 双清包税

`export_customs = true` + `import_customs = true` + `tax_mode = included`

例如“韩国海派包税”可以表达为：

```text
origin_country = CN
destination_country = KR
transport_mode = sea
last_mile_delivery = true
export_customs = true
import_customs = true
tax_mode = included
```

## 6. 产品名称规则【已确认】

产品名称采用：**系统根据结构化字段自动生成默认名称 + 用户允许修改。**

例如用户选择：
- 目的国：委内瑞拉
- 运输方式：海运
- 出口清关：是
- 进口清关：是
- 末端派送：是
- 税费：不包税

系统可生成默认名称：`委内瑞拉海派双清`。

如果税费模式为包税，可生成：`委内瑞拉海派双清包税`。

用户可以修改为内部习惯名称，例如：`委内瑞拉普货双清专线`。

**重要规则：product_name 只用于展示。即使用户修改名称，搜索、匹配和业务逻辑仍使用 destination_country、transport_mode、清关、派送、税费等结构化字段。**

数据库不强制保存 `auto_generated_name`；默认名称可以根据结构化字段实时生成。

## 7. 关于货物字段【已确认】

第一版不设计 `accepted_cargo[] / 可接货物[]` 让用户穷举货类。

原因：
1. 可运输商品种类无法穷举；
2. “家具/汽配/机械”属于商品或行业分类，而“带电/液体/粉末/危险品”属于运输属性，不能混为同一个枚举；
3. 实际货代经常采用“普货可接、特殊货需确认”的业务方式；
4. 本系统首先是获客系统，而非完整 TMS，不能为了找客户增加过高产品配置成本。

V1 第一版仅保留 `cargo_notes` 作为特殊能力/限制说明，例如：

> 带电可询，食品需资料，危险品不接。

“本次希望找家具厂 / 汽配厂”等属于客户画像或搜索策略，不属于物流产品。

## 8. 明确不属于物流产品的字段

以下字段不得放入 LogisticsProduct：
- customer_type（同行 / 工厂 / 贸易商等）
- target_industry
- target_cargo_category
- search_keywords
- exclude_keywords
- customer_match_score
- 联系方式

这些字段会在后续模块分别设计。

## 9. 后续待讨论

下一对象：**目标客户画像 Customer Segment / ICP**。

需要回答：一个物流产品可以配置哪些目标客户群，以及哪些字段真正应该影响“系统去哪里找哪些公司”。
