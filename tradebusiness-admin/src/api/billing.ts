import request from '@/utils/request'
export interface CreditWallet { id: string; user_id: string; balance: number }
export interface CreditTransaction { id: string; amount: number; balance_after: number; action: string; description?: string; created_at: string }
export function getWallet() { return request<CreditWallet>({ url: '/api/v1/billing/wallet', method: 'get' }) }
export function getCreditTransactions() { return request<CreditTransaction[]>({ url: '/api/v1/billing/transactions', method: 'get' }) }
export function adjustCredits(data: { amount: number; action?: string; description?: string }) { return request<CreditWallet>({ url: '/api/v1/billing/adjust', method: 'post', data }) }
export interface SubscriptionPlan { id: string; name: string; price: number; credits: number; interval: string; is_active: boolean }
export interface UserSubscription { id: string; user_id: string; plan_id: string; status: string }
export function getPlans() { return request<SubscriptionPlan[]>({ url: '/api/v1/billing/plans', method: 'get' }) }
export function getSubscription() { return request<UserSubscription | null>({ url: '/api/v1/billing/subscription', method: 'get' }) }
export function subscribe(plan_id: string) { return request<UserSubscription>({ url: '/api/v1/billing/subscription', method: 'post', data: { plan_id } }) }
export interface PaymentOrder { id: string; plan_id: string; amount: number; provider: string; status: string; created_at: string }
export function createPaymentOrder(plan_id: string, provider: 'stripe' | 'wechat' | 'alipay' | 'pending' = 'pending') { return request<PaymentOrder>({ url: '/api/v1/billing/orders', method: 'post', data: { plan_id, provider } }) }
export function getPaymentOrders() { return request<PaymentOrder[]>({ url: '/api/v1/billing/orders', method: 'get' }) }

export function createStripeSession(order_id: string) { return request<{ order_id: string; session_id: string; checkout_url: string }>({ url: `/api/v1/billing/orders/${order_id}/stripe-session`, method: 'post' }) }
