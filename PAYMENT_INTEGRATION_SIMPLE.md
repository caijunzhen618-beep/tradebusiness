# Tradebase 支付平台傻瓜式对接指南

本指南适合第一次接支付平台的开发人员。请严格按顺序操作。

## 一、先选平台

只选一个平台开始，不要同时配置三个。

| 使用场景 | 推荐平台 |
|---|---|
| 海外客户、美元、国际信用卡 | Stripe |
| 中国大陆客户、微信生态 | 微信支付 |
| 中国大陆客户、支付宝生态 | 支付宝 |

如果你还没有任何支付账号，建议先接 Stripe 测试环境，流程最简单。

---

# 二、Stripe 对接步骤（推荐先做）

## 第 1 步：创建 Stripe 账号

1. 打开 [Stripe Dashboard](https://dashboard.stripe.com/)。
2. 注册并完成邮箱验证。
3. 左上角保持 `Test mode` 测试模式。
4. 打开 Developers → API keys。
5. 复制：
   - Secret key，通常以 `sk_test_` 开头。

不要复制 Publishable key 到后端，后端只使用 Secret key。

## 第 2 步：创建 Webhook

1. 打开 Developers → Webhooks。
2. 点击 Add endpoint。
3. Endpoint URL 填：

```text
https://你的域名/api/v1/billing/webhooks/stripe
```

4. 选择事件：

```text
checkout.session.completed
payment_intent.succeeded
payment_intent.payment_failed
```

5. 创建后点击 Reveal。
6. 复制 Signing secret，通常以 `whsec_` 开头。

## 第 3 步：配置后端 `.env`

在 `tradebusiness-backend/.env` 添加：

```env
ENVIRONMENT=development
PAYMENT_PROVIDER=stripe
STRIPE_SECRET_KEY=sk_test_你的密钥
STRIPE_WEBHOOK_SECRET=whsec_你的签名密钥
STRIPE_CURRENCY=usd
```

注意：

- 不要加引号。
- 不要把密钥提交到 Git。
- 测试环境使用 `sk_test_`。
- 生产环境使用 `sk_live_`，并重新创建生产 webhook secret。

## 第 4 步：本地转发 webhook

安装 Stripe CLI，然后登录：

```powershell
stripe login
```

转发到本地后端：

```powershell
stripe listen --forward-to localhost:8000/api/v1/billing/webhooks/stripe
```

命令输出中会出现一个新的 `whsec_...`，本地测试必须使用这个 secret，而不是 Dashboard webhook 的 secret。

## 第 5 步：用测试卡付款

Stripe 测试卡：

```text
卡号：4242 4242 4242 4242
有效期：任意未来日期
CVC：任意三位数字
邮编：任意
```

## 第 6 步：检查结果

付款成功后检查：

1. `payment_orders.status` 变为 `paid`。
2. `credit_wallets.balance` 增加套餐积分。
3. `credit_transactions` 出现 `subscription_credit`。
4. `user_subscriptions.status` 为 `active`。
5. 重复发送同一 webhook 不会重复增加积分。

Stripe 官方文档要求使用 webhook 原始请求体和 `Stripe-Signature` 验签：[Webhook 文档](https://docs.stripe.com/webhooks)、[签名验证](https://docs.stripe.com/webhooks/signature?lang=python)。

---

# 三、微信支付对接步骤

微信支付适合中国大陆客户。需要企业主体、商户号和 API 证书。

## 第 1 步：准备账号

1. 打开 [微信支付商户平台](https://pay.weixin.qq.com/)。
2. 注册或登录商户号。
3. 完成企业认证。
4. 记录：
   - 商户号 `mch_id`
   - AppID
   - APIv3 Key
   - 商户 API 证书序列号
   - 商户私钥文件

## 第 2 步：设置回调地址

回调地址填写：

```text
https://你的域名/api/v1/billing/webhooks/wechat
```

必须是 HTTPS，不能使用 localhost。

## 第 3 步：配置 `.env`

```env
ENVIRONMENT=production
PAYMENT_PROVIDER=wechat
WECHAT_MCH_ID=你的商户号
WECHAT_APP_ID=你的AppID
WECHAT_SERIAL_NO=证书序列号
WECHAT_PRIVATE_KEY_PATH=/run/secrets/wechat/apiclient_key.pem
WECHAT_PLATFORM_CERT_PATH=/run/secrets/wechat/platform_cert.pem
WECHAT_API_V3_KEY=32位APIv3密钥
WECHAT_NOTIFY_URL=https://你的域名/api/v1/billing/webhooks/wechat
```

私钥和 APIv3 Key 不要写进代码，也不要提交 Git。

## 第 4 步：回调处理要求

微信支付回调必须：

1. 读取原始请求体。
2. 使用 `Wechatpay-Timestamp`、`Wechatpay-Nonce`、`Wechatpay-Signature` 验签。
3. 使用 APIv3 Key 解密 `resource`。
4. 校验商户号、订单号和金额。
5. 只对 `SUCCESS` 发放积分。
6. 在 5 秒内返回成功。

官方说明：[微信支付验签](https://pay.wechatpay.cn/doc/v3/partner/4012365880)、[微信回调验签与解密](https://pay.wechatpay.cn/doc/v3/partner/4019605946)。

---

# 四、支付宝对接步骤

## 第 1 步：创建应用

1. 打开 [支付宝开放平台](https://open.alipay.com/)。
2. 登录企业账号。
3. 创建网页/移动应用。
4. 配置应用网关和授权回调地址。
5. 生成 RSA2 密钥。
6. 上传应用公钥。
7. 保存支付宝公钥。

需要准备：

- AppID
- 应用私钥
- 支付宝公钥

## 第 2 步：配置异步通知地址

```text
https://你的域名/api/v1/billing/webhooks/alipay
```

不要只使用浏览器同步跳转地址，最终支付结果必须依赖服务端异步通知。

## 第 3 步：配置 `.env`

```env
ENVIRONMENT=production
PAYMENT_PROVIDER=alipay
ALIPAY_APP_ID=你的AppID
ALIPAY_PRIVATE_KEY_PATH=/run/secrets/alipay/private_key.pem
ALIPAY_PUBLIC_KEY_PATH=/run/secrets/alipay/alipay_public_key.pem
ALIPAY_NOTIFY_URL=https://你的域名/api/v1/billing/webhooks/alipay
ALIPAY_RETURN_URL=https://你的前端域名/payment/result
```

## 第 4 步：服务端验签

支付宝回调必须使用 RSA2 验签，并校验：

- `app_id`
- 商户号
- 商户订单号
- 支付金额
- 交易状态

建议状态映射：

```text
TRADE_SUCCESS -> paid
TRADE_FINISHED -> paid
WAIT_BUYER_PAY -> pending
TRADE_CLOSED -> cancelled
```

---

# 五、上线前最容易出错的 10 件事

1. 把测试密钥放到生产环境。
2. 把生产密钥提交到 Git。
3. 使用 HTTP 而不是 HTTPS。
4. 先 `request.json()` 再验 Stripe 签名。
5. 只相信前端跳转结果，不处理 webhook。
6. 不校验支付金额。
7. 重复 webhook 重复发积分。
8. 把 API 私钥写在源码里。
9. 回调接口没有超时和日志。
10. 没有配置订单对账。

---

# 六、最小上线检查表

```text
[ ] 已选择一个支付平台
[ ] 已创建测试商户账号
[ ] 已配置测试密钥
[ ] 已配置 HTTPS webhook
[ ] 已成功完成一笔测试支付
[ ] 订单状态变为 paid
[ ] 积分流水已生成
[ ] 钱包余额已增加
[ ] 重复 webhook 不重复加积分
[ ] 支付失败不会增加积分
[ ] 生产环境已关闭开发 callback 接口
[ ] 已切换生产密钥
[ ] 已完成一笔小额真实订单对账
```

# 七、当前项目的启动命令

初始化套餐：

```powershell
cd C:\commonspace\ai_create\tradebusiness\tradebusiness-backend
py scripts/seed_billing_plans.py
```

启动后端：

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

启动管理端：

```powershell
cd C:\commonspace\ai_create\tradebusiness\tradebusiness-admin
npm run dev
```

# 八、什么时候可以算真正上线

只有以下条件全部满足，才算完成生产支付接入：

- 对应平台的正式验签代码已经启用。
- 开发 callback 在生产环境不可访问。
- 所有支付回调都经过签名验证。
- 订单金额和套餐金额完成服务端校验。
- 订单幂等和积分发放在同一个数据库事务中。
- 已完成测试订单和真实小额订单对账。

# 九、Stripe 从零到跑通的完整命令

## 9.1 检查环境变量

PowerShell：

```powershell
Get-Content C:\commonspace\ai_create\tradebusiness\tradebusiness-backend\.env
```

至少确认存在：

```env
STRIPE_SECRET_KEY=sk_test_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_CURRENCY=usd
STRIPE_SUCCESS_URL=http://localhost:3000/settings/plans?success=1
STRIPE_CANCEL_URL=http://localhost:3000/settings/plans?cancelled=1
```

## 9.2 初始化套餐

```powershell
cd C:\commonspace\ai_create\tradebusiness\tradebusiness-backend
py scripts/seed_billing_plans.py
```

## 9.3 启动后端

```powershell
cd C:\commonspace\ai_create\tradebusiness\tradebusiness-backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 9.4 启动 Stripe webhook 转发

新开一个 PowerShell：

```powershell
stripe login
stripe listen --forward-to http://localhost:8000/api/v1/billing/webhooks/stripe
```

把命令输出的 `whsec_...` 覆盖到 `.env` 的 `STRIPE_WEBHOOK_SECRET`，然后重启后端。

## 9.5 前端启动

```powershell
cd C:\commonspace\ai_create\tradebusiness\tradebusiness-admin
npm run dev
```

打开“积分套餐”，点击“选择套餐”。浏览器会跳转 Stripe Checkout。

## 9.6 测试付款

```text
卡号：4242 4242 4242 4242
有效期：任意未来日期
CVC：任意三位数字
邮编：任意
```

## 9.7 触发失败支付测试

```text
卡号：4000 0000 0000 9995
```

失败支付不应发放积分。

## 9.8 检查订单

```powershell
# 查看订单和钱包时，使用项目数据库客户端执行对应查询
SELECT id, status, provider, amount, external_id FROM payment_orders ORDER BY created_at DESC;
SELECT user_id, balance FROM credit_wallets;
SELECT user_id, amount, action, balance_after FROM credit_transactions ORDER BY created_at DESC;
```

成功订单必须同时满足：

```text
payment_orders.status = paid
credit_transactions.action = subscription_credit
credit_wallets.balance 已增加套餐积分
user_subscriptions.status = active
```

## 9.9 测试重复回调

在 Stripe CLI 中重复触发同一个成功事件，检查钱包余额只增加一次。若余额增加两次，立即停止生产接入并检查订单锁和幂等逻辑。

# 十、生产切换清单

1. 在 Stripe Dashboard 切换 Live mode。
2. 创建生产 webhook endpoint。
3. 复制生产 endpoint 的 `whsec_...`。
4. 将 `sk_test_` 换成 `sk_live_`。
5. 将前端成功/取消地址换成 HTTPS 正式域名。
6. 重启后端服务。
7. 使用低金额真实订单测试。
8. 核对 Stripe Dashboard、订单表、钱包和流水。
9. 关闭测试 webhook。
10. 保存本次上线的订单号和对账结果。
