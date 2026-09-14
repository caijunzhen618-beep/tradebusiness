<template>
  <div class="lead-generation-page">
    <n-space vertical :size="22">
      <div class="hero">
        <div>
          <div class="eyebrow">AI LEAD GENERATION</div>
          <h2>把目标客户变成下一条商机</h2>
          <p>查看获客任务、潜客状态和待跟进内容，集中推进销售动作。</p>
        </div>
        <n-button type="primary" @click="router.push({ name: 'DiscoverCustomers' })">发现客户</n-button>
      </div>

      <n-grid :cols="7" :x-gap="14" responsive="screen">
        <n-grid-item v-for="metric in metrics" :key="metric.label">
          <n-card size="small"><n-statistic :label="metric.label" :value="metric.value" /></n-card>
        </n-grid-item>
      </n-grid>

      <n-alert v-if="walletBalance < 5" type="warning" :show-icon="true" title="积分余额较低">
        当前剩余 {{ walletBalance }} 积分，企业背调需要 5 积分，开发信生成需要 2 积分，请及时充值。
      </n-alert>

      <n-card title="触达渠道分布" size="small" :bordered="false">
        <n-space v-if="Object.keys(channels).length">
          <n-tag v-for="(count, channel) in channels" :key="channel" type="info" round v-text="`${channel} ${count}`" />
        </n-space>
        <n-empty v-else description="暂无渠道数据" />
      </n-card>

      <n-card title="最近潜客" :bordered="false">
        <template #header-extra>
          <n-space>
            <n-input v-model:value="search" clearable placeholder="搜索公司、国家或行业" @keyup.enter="load" />
            <n-button text type="primary" @click="load">查询</n-button>
          </n-space>
        </template>
        <n-data-table :columns="columns" :data="leads" :loading="loading" :pagination="false" />
      </n-card>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { h, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { NButton, NTag, type DataTableColumns } from 'naive-ui'
import { getCreditWallet, getLeadGenerationStats, getLeads, type Lead } from '@/api/leadGeneration'

const router = useRouter()
const loading = ref(false)
const leads = ref<Lead[]>([])
const search = ref('')
const channels = ref<Record<string, number>>({})
const walletBalance = ref(0)
const metrics = ref([
  { label: '潜客总数', value: 0 },
  { label: '开发信生成', value: 0 },
  { label: '跟进任务', value: 0 },
  { label: '已完成跟进', value: 0 },
  { label: '剩余积分', value: 0 },
  { label: '已联系', value: 0 },
  { label: '已回复', value: 0 },
  { label: '回复率 %', value: 0 },
])
const columns: DataTableColumns<Lead> = [
  { title: '公司', key: 'company_name' },
  { title: '国家', key: 'country', render: (row) => row.country || '-' },
  { title: '行业', key: 'industry', render: (row) => row.industry || '-' },
  { title: '状态', key: 'status', render: (row) => h(NTag, { type: row.status === 'invalid' ? 'error' : 'info' }, { default: () => row.status }) },
  { title: '操作', key: 'actions', render: (row) => h(NButton, { text: true, type: 'primary', onClick: () => router.push({ name: 'LeadGenerationDetail', params: { id: row.id } }) }, { default: () => '查看详情' }) },
]

async function load() {
  loading.value = true
  try {
    const [stats, wallet, result] = await Promise.all([
      getLeadGenerationStats(),
      getCreditWallet(),
      getLeads({ limit: 10, search: search.value || undefined }),
    ])
    metrics.value = [
      { label: '潜客总数', value: stats.leads },
      { label: '开发信生成', value: stats.sales_copies },
      { label: '跟进任务', value: stats.followups },
      { label: '已完成跟进', value: stats.completed_followups },
      { label: '剩余积分', value: wallet.balance },
      { label: '已联系', value: stats.contacted },
      { label: '已回复', value: stats.replied },
      { label: '回复率 %', value: stats.reply_rate },
    ]
    channels.value = stats.channels || {}
    walletBalance.value = wallet.balance
    leads.value = result.items || []
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.lead-generation-page{max-width:1200px;margin:0 auto}.hero{display:flex;align-items:flex-end;justify-content:space-between;padding:28px 30px;border:1px solid #e9e8e4;border-radius:18px;background:linear-gradient(120deg,#fff 0%,#fff8f3 62%,#f2efff 100%)}.eyebrow{font-size:10px;letter-spacing:1.7px;color:#8a7cf4;font-weight:800}.hero h2{margin:10px 0 5px;font-size:27px;letter-spacing:-.8px}.hero p{margin:0;color:#737780;font-size:13px}
</style>
