<template>
  <div class="plans">
    <el-alert v-if="paymentState === 'success'" type="success" title="支付已提交" description="支付平台正在确认订单，积分到账后页面会自动刷新。" show-icon closable />
    <el-alert v-if="paymentState === 'cancelled'" type="warning" title="支付已取消" description="订单未完成支付，积分不会发生变化。" show-icon closable />
    <div class="head"><div><h2>积分套餐</h2><p>选择适合当前获客规模的积分方案。</p></div></div>
    <el-row :gutter="18"><el-col v-for="plan in plans" :key="plan.id" :span="8"><el-card class="plan"><h3>{{ plan.name }}</h3><div class="price">{{ plan.price }} <small>/ {{ plan.interval }}</small></div><p>{{ plan.credits }} 积分</p><el-button type="primary" :plain="subscription?.plan_id !== plan.id" @click="selectPlan(plan)">{{ subscription?.plan_id === plan.id ? '当前套餐' : '选择套餐' }}</el-button></el-card></el-col></el-row>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute } from 'vue-router'
import { createPaymentOrder, createStripeSession, getPlans, getSubscription, type SubscriptionPlan, type UserSubscription } from '@/api/billing'

const route = useRoute()
const plans = ref<SubscriptionPlan[]>([])
const subscription = ref<UserSubscription | null>(null)
const paymentState = ref(String(route.query.success ? 'success' : route.query.cancelled ? 'cancelled' : ''))
async function load() { plans.value = await getPlans(); subscription.value = await getSubscription() }
async function selectPlan(plan: SubscriptionPlan) { if (subscription.value?.plan_id === plan.id) return; await ElMessageBox.confirm(`确认选择 ${plan.name} 套餐吗？`, '订阅确认'); const order = await createPaymentOrder(plan.id, 'stripe'); const session = await createStripeSession(order.id); window.location.href = session.checkout_url }
onMounted(async () => { await load(); if (paymentState.value === 'success') { ElMessage.success('支付已提交，正在确认到账'); window.setTimeout(load, 2000) } })
</script>

<style scoped>
.plans { max-width: 1100px; margin: auto; }.head { margin: 24px 0; }.head h2 { margin: 0; }.head p { color: #667085; }.plan { text-align: center; padding: 18px; margin-bottom: 18px; }.plan h3 { font-size: 20px; }.price { font-size: 36px; font-weight: 700; }.price small { font-size: 13px; color: #98a2b3; }.plan p { color: #667085; margin-bottom: 24px; }
</style>
