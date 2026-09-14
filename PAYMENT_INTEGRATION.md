# Tradebase 支付平台生产对接指南

## 1. 当前实现边界

当前代码已经具备：

- `SubscriptionPlan` 套餐
- `PaymentOrder` 订单
- `CreditWallet` 钱包
- `CreditTransaction` 积分流水
- 支付成功后幂等发放积分
- 订阅状态更新

`POST /api/v1/billing/orders/{order_id}/callback` 是开发预留接口，不能直接暴露到生产环境。生产环境必须使用平台专用 webhook，并完成签名校验、原始请求体校验、幂等处理和 HTTPS。

## 2. 通用生产流程

```text
用户选择套餐
  -> 服务端创建 PaymentOrder(status=pending)
  -> 服务端调用支付平台创建支付会话/订单
  -> 返回支付链接或二维码
  -> 用户完成支付
  -> 支付平台调用 webhook
  -> 验签、解析、校验金额和套餐
  -> 幂等更新 PaymentOrder=paid
  -> 发放套餐积分
  -> 更新 UserSubscription
```

必须校验：

- 订单号是否存在
- 支付平台订单号是否重复
- 回调金额是否等于订单金额
- 回调币种是否匹配
- 套餐是否仍然有效
- 回调状态是否为成功
- 同一订单是否已经发放过积分

## 3. Stripe

官方要求 webhook 使用原始请求体验签，不能先被 JSON parser 修改；应使用 `Stripe-Signature` 和 endpoint secret，并检查时间戳避免重放攻击。[Stripe Webhooks](https://docs.stripe.com/webhooks)、[Stripe 签名验证](https://docs.stripe.com/webhooks/signature?lang=python)

建议环境变量：

```env
PAYMENT_PROVIDER=stripe
STRIPE_SECRET_KEY=sk_live_xxx
STRIPE_WEBHOOK_SECRET=whsec_xxx
STRIPE_CURRENCY=usd
```

事件建议监听：

```text
checkout.session.completed
payment_intent.succeeded
payment_intent.payment_failed
```

`metadata` 必须携带：

```json
{
  "payment_order_id": "内部订单 ID",
  "plan_id": "套餐 ID",
  "user_id": "用户 ID"
}
```

验签必须使用原始 bytes：

```python
payload = await request.body()
signature = request.headers.get("stripe-signature")
event = stripe.Webhook.construct_event(
    payload,
    signature,
    settings.STRIPE_WEBHOOK_SECRET,
)
```

不要使用 `await request.json()` 后再验签。

## 4. 微信支付 API v3

微信支付 API v3 的回调需要使用 `Wechatpay-Timestamp`、`Wechatpay-Nonce`、原始请求体和 `Wechatpay-Signature` 验签；业务数据使用 APIv3 Key 进行 AES-256-GCM 解密。验签使用微信支付平台证书或微信支付公钥，不能使用商户 API 私钥替代。[微信支付签名与验签](https://pay.wechatpay.cn/doc/v3/partner/4012365880)、[微信支付回调验签与解密](https://pay.wechatpay.cn/doc/v3/partner/4019605946)

建议环境变量：

```env
PAYMENT_PROVIDER=wechat
WECHAT_MCH_ID=xxx
WECHAT_APP_ID=xxx
WECHAT_SERIAL_NO=xxx
WECHAT_PRIVATE_KEY_PATH=/run/secrets/wechat/apiclient_key.pem
WECHAT_PLATFORM_CERT_PATH=/run/secrets/wechat/platform_cert.pem
WECHAT_API_V3_KEY=32位密钥
WECHAT_NOTIFY_URL=https://api.example.com/api/v1/billing/webhooks/wechat
```

处理顺序：

1. 读取原始请求体。
2. 根据请求头选择平台证书/公钥。
3. 验证 RSA-SHA256 签名。
4. 使用 APIv3 Key 解密 `resource.ciphertext`。
5. 校验解密后的商户号、金额、订单号和交易状态。
6. 幂等发放积分。
7. 在 5 秒内返回成功应答。

## 5. 支付宝

支付宝生产环境通常使用 RSA2 签名。服务端必须使用支付宝公钥验证 `notify` 参数签名，并校验 `app_id`、商户号、订单号、金额和交易状态。验签通过后才允许发放积分。

建议环境变量：

```env
PAYMENT_PROVIDER=alipay
ALIPAY_APP_ID=xxx
ALIPAY_PRIVATE_KEY_PATH=/run/secrets/alipay/private_key.pem
ALIPAY_PUBLIC_KEY_PATH=/run/secrets/alipay/alipay_public_key.pem
ALIPAY_NOTIFY_URL=https://api.example.com/api/v1/billing/webhooks/alipay
ALIPAY_RETURN_URL=https://app.example.com/billing/result
```

状态判断建议：

```text
TRADE_SUCCESS -> paid
TRADE_FINISHED -> paid（按业务决定是否允许退款后继续使用）
WAIT_BUYER_PAY -> pending
TRADE_CLOSED -> cancelled
```

不要只依赖浏览器 `return_url`，必须以服务端异步通知为最终支付依据。

## 6. 数据库幂等要求

当前 `PaymentOrder` 应继续补充以下约束：

- `external_id` 唯一索引（按 provider + external_id 组合唯一）
- `paid_at`
- `callback_payload_hash`
- `credited_at`
- `currency`

积分发放必须在数据库事务中完成：

```text
锁定 PaymentOrder
  -> 如果 status=paid 或 credited_at 不为空，直接返回成功
  -> 校验金额
  -> 更新订单为 paid
  -> 增加钱包余额
  -> 写入 CreditTransaction
  -> 标记 credited_at
  -> 提交事务
```

## 7. 上线前检查

- 所有 webhook 使用 HTTPS
- 不在日志中打印支付密钥、证书私钥和完整回调报文
- webhook 使用原始 body 验签
- 验签失败返回 400，不发放积分
- 回调处理设置数据库事务
- 配置 webhook 重试监控
- 配置订单对账任务
- 支付金额使用整数最小货币单位
- 生产环境关闭开发回调接口
- 支付密钥使用 Secret Manager 或部署平台密钥注入
- 支付成功和积分发放都有审计日志

## 8. 当前项目上线步骤

1. 执行数据库迁移/建表。
2. 初始化套餐：

```powershell
cd tradebusiness-backend
py scripts/seed_billing_plans.py
```

3. 配置对应支付平台环境变量。
4. 创建平台 webhook 地址。
5. 实现对应平台验签适配器。
6. 使用测试订单验证 pending、paid、failed、重复回调。
7. 检查积分流水和订阅状态。
8. 关闭 `/api/v1/billing/orders/{id}/callback` 开发接口。
9. 切换生产密钥和生产 webhook。
10. 做一笔小额真实订单对账。
