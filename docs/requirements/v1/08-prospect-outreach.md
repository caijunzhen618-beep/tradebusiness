# V1-08 潜客触达与最小跟进闭环【已确认】

> 状态：已确认  
> 版本：V1  
> 当前范围：国内拓客第一阶段，不扩展为完整 CRM、报价、订单或成交系统。

## 1. 业务目标

```text
查看潜客 → 电话 / Email 触达 → 记录联系结果 → 必要时设置下次跟进 → 销售确认事实反哺企业事实库
```

## 2. 第一版触达渠道

- `phone`：电话/手机
- `email`：邮件

第一版不要求系统内拨号。手机号、电话、邮箱至少支持一键复制；Email 可复用现有发送能力。微信、拜访、WhatsApp 等待真实业务验证后再扩展。

## 3. 联系结果

| 结果 | 业务含义 | 处理原则 |
| --- | --- | --- |
| 未联系上 | 无人接、暂时没找到人 | 保留，可再次联系 |
| 无该方向业务 | 明确没有当前产品方向业务 | 当前产品下暂不优先 |
| 有该方向业务，暂无货 | 有该方向业务但当前没货 | 有效潜客，值得维护 |
| 近期有货 / 可以询价 | 出现实物流机会 | 重点跟进 |
| 联系方式无效 | 当前电话/邮箱无效 | 只更新对应 ContactPoint，不判死整个企业 |
| 拒绝联系 | 明确要求停止开发 | 按用户选择的拒绝范围执行 |

## 4. 无业务与暂无货必须分开

“我们不做委内瑞拉”和“我们做委内瑞拉，但最近没有货”价值完全不同。后者是高价值销售验证事实。“当前没有货”不能错误写成“没有该方向业务”。

## 5. ContactActivity

```text
ContactActivity
- id
- prospect_id
- product_id
- customer_type       # 当前以同行或出口货主哪种业务角色开发
- contact_id?
- contact_point_id?
- channel             # phone / email
- occurred_at
- result
- note?
- next_follow_up_at?
- created_by
- created_at
```

电话/邮件是渠道，result 是本次业务结果。联系历史关联企业 + 产品 + 当前客户角色语境。

## 6. 跟进保持最小化

需要继续跟进时仅要求可选填写下次跟进时间与备注。第一版不扩展完整 Opportunity / Quote / Order 模型。

## 7. 联系结果是产品级业务结论

同一家企业可能：委内瑞拉有业务暂无货、韩国近期有货、南非无相关业务。因此不能在 Prospect 上设置全局 interested 状态。

## 8. 拒绝联系的作用范围

“拒绝联系”不能默认把企业所有未来产品全部封死。第一版至少区分：

### 当前产品范围
对方表达“这个方向不用再联系我”等，仅停止当前 `prospect × product` 语境的主动开发。其他物流产品仍可根据真实业务继续判断。

### 企业全局范围
只有业务员根据对方明确表达，选择“该企业全局不再联系”时，才阻止该 Prospect 在所有产品下继续主动触达。

如后续需要进一步细化到“只禁用某一个电话/邮箱渠道”，可以基于 ContactPoint 扩展；V1 第一版先保持产品级与企业级两个范围。

## 9. 销售反馈反哺企业事实库

例如业务员确认 ABC 确实有委内瑞拉方向业务，形成带时间与来源的第一方 Evidence：

```text
prospect_id = ABC
type = destination_business
country_code = VE
source_type = sales_verified
```

销售确认事实可以被后续产品匹配复用，但不能被当成永远不变的事实。

## 10. 联系方式无效反馈

空号/错误邮箱只作用于具体 ContactPoint：不删除历史，设置 `is_valid=false`。如果企业还有其他有效电话或邮箱，仍然是可触达企业。

## 11. ProductProspect 不重复保存可计算状态

```text
ProductProspect
- id
- product_id
- prospect_id
- customer_type
- added_at
```

last_contact_at、last_result、next_follow_up_at 等从 ContactActivity 计算，不重复维护。

## 12. 潜客列表重点信息

- 公司名称
- 推荐理由 / Evidence 摘要
- 具体联系人及职位
- 手机 / 电话 / Email
- 一键复制/邮件入口
- 最近联系结果
- 下次跟进时间
- 记录联系结果入口

目标是让业务员连续处理潜客，不要求填写复杂 CRM 表单。
