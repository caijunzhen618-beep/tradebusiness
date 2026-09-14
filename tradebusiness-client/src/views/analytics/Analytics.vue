<template>
  <div class="analytics-page">
    <n-card title="数据分析" :bordered="false">
      <template #header-extra>
        <n-space>
          <n-select
            v-model:value="dateRange"
            :options="dateRangeOptions"
            :style="{ width: '150px' }"
          />
          <n-button @click="handleRefresh">
            <template #icon>
              <n-icon><RefreshIcon /></n-icon>
            </template>
            刷新
          </n-button>
        </n-space>
      </template>

      <!-- 核心指标 -->
      <n-grid :cols="5" :x-gap="16" class="metrics-grid">
        <n-grid-item>
          <n-card class="metric-card">
            <n-statistic label="总客户数" :value="metrics.total_customers">
              <template #suffix>
                <n-icon size="20" color="#18a058">
                  <TrendingUpIcon />
                </n-icon>
              </template>
            </n-statistic>
            <div class="metric-change">实时统计</div>
          </n-card>
        </n-grid-item>

        <n-grid-item>
          <n-card class="metric-card">
            <n-statistic label="合作客户" :value="metrics.cooperating_customers">
              <template #suffix>
                <n-icon size="20" color="#2080f0">
                  <PeopleIcon />
                </n-icon>
              </template>
            </n-statistic>
            <div class="metric-change">客户状态</div>
          </n-card>
        </n-grid-item>

        <n-grid-item>
          <n-card class="metric-card">
            <n-statistic label="转化率" :value="metrics.conversion_rate" suffix="%">
              <template #suffix>
                <n-icon size="20" color="#f0a020">
                  <TrendingUpIcon />
                </n-icon>
              </template>
            </n-statistic>
            <div class="metric-change">合作 / 总客户</div>
          </n-card>
        </n-grid-item>

        <n-grid-item>
          <n-card class="metric-card">
            <n-statistic label="发送邮件" :value="metrics.emails_sent">
              <template #suffix>
                <n-icon size="20" color="#18a058">
                  <MailIcon />
                </n-icon>
              </template>
            </n-statistic>
            <div class="metric-change">邮件统计</div>
          </n-card>
        </n-grid-item>

        <n-grid-item>
          <n-card class="metric-card">
            <n-statistic label="任务完成" :value="metrics.tasks_completed">
              <template #suffix>
                <n-icon size="20" color="#2080f0">
                  <CheckboxIcon />
                </n-icon>
              </template>
            </n-statistic>
            <div class="metric-change">任务统计</div>
          </n-card>
        </n-grid-item>
      </n-grid>

      <n-tabs type="line" animated class="analytics-tabs">
        <!-- 客户分布地图 -->
        <n-tab-pane name="map" tab="客户分布">
          <n-card title="客户全球分布" size="small" :bordered="false">
            <div class="map-container">
              <n-data-table
                :columns="countryColumns"
                :data="countryData"
                :bordered="true"
                size="small"
                :style="{ marginTop: '24px' }"
              />
            </div>
          </n-card>
        </n-tab-pane>

        <!-- 业务量统计 -->
        <n-tab-pane name="volume" tab="业务量统计">
          <n-grid :cols="2" :x-gap="16" :y-gap="16">
            <n-grid-item :span="2">
              <n-card title="客户状态分布" size="small">
                <n-data-table
                  :columns="statusColumns"
                  :data="statusData"
                  :bordered="true"
                  size="small"
                />
              </n-card>
            </n-grid-item>

            <n-grid-item>
              <n-card title="业务类型分布" size="small">
                <n-empty description="暂无业务类型聚合数据" />
              </n-card>
            </n-grid-item>

            <n-grid-item>
              <n-card title="任务状态分布" size="small">
                <n-data-table
                  :columns="taskStatusColumns"
                  :data="taskStatusData"
                  :bordered="true"
                  size="small"
                />
              </n-card>
            </n-grid-item>

            <n-grid-item :span="2">
              <n-card title="月度业务量" size="small">
                <n-data-table
                  :columns="volumeColumns"
                  :data="volumeData"
                  :bordered="true"
                  size="small"
                />
              </n-card>
            </n-grid-item>
          </n-grid>
        </n-tab-pane>

        <!-- 转化率分析 -->
        <n-tab-pane name="conversion" tab="转化率分析">
          <n-grid :cols="2" :x-gap="16">
            <n-grid-item>
              <n-card title="客户转化漏斗" size="small">
                <n-steps vertical :current="4" :status="'process'">
                  <n-step title="潜在客户" :description="`${funnel.potential} 个`" />
                  <n-step title="联系中" :description="`${funnel.contacting} 个`" />
                  <n-step title="合作中" :description="`${funnel.cooperating} 个`" />
                  <n-step title="已完成交易" :description="`${funnel.completed} 个`" />
                </n-steps>

                <n-divider />

                <n-descriptions :column="1" bordered size="small">
                  <n-descriptions-item label="潜在→联系">
                    {{ funnel.potential_to_contact }}%
                  </n-descriptions-item>
                  <n-descriptions-item label="联系→合作">
                    {{ funnel.contact_to_cooperate }}%
                  </n-descriptions-item>
                  <n-descriptions-item label="合作→交易">
                    {{ funnel.cooperate_to_complete }}%
                  </n-descriptions-item>
                  <n-descriptions-item label="整体转化率">
                    {{ funnel.overall }}%
                  </n-descriptions-item>
                </n-descriptions>
              </n-card>
            </n-grid-item>

            <n-grid-item>
              <n-card title="转化率趋势" size="small">
                <n-empty description="暂无时间序列转化率数据" />
              </n-card>
            </n-grid-item>

            <n-grid-item :span="2">
              <n-card title="影响转化率的因素" size="small">
                <n-data-table
                  :columns="factorColumns"
                  :data="factorData"
                  :bordered="true"
                  size="small"
                />
              </n-card>
            </n-grid-item>
          </n-grid>
        </n-tab-pane>

        <!-- 业务员绩效对比 -->
        <n-tab-pane name="performance" tab="业务员绩效">
          <n-card title="业务员绩效排行榜" size="small" :bordered="false">
            <n-data-table
              :columns="performanceColumns"
              :data="performanceData"
              :bordered="true"
              size="small"
              :default-sort="{ key: 'score', order: 'descending' }"
            />
          </n-card>

          <n-grid :cols="2" :x-gap="16" :y-gap="16" :style="{ marginTop: '16px' }">
            <n-grid-item>
              <n-card title="客户获取对比" size="small">
                <n-empty description="暂无业务员客户获取聚合数据" />
              </n-card>
            </n-grid-item>

            <n-grid-item>
              <n-card title="邮件发送对比" size="small">
                <n-empty description="暂无业务员邮件发送聚合数据" />
              </n-card>
            </n-grid-item>
          </n-grid>
        </n-tab-pane>
      </n-tabs>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { h, ref, onMounted } from 'vue'
import { NProgress, NTag, useMessage } from 'naive-ui'
import {
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  People as PeopleIcon,
  Mail as MailIcon,
  Checkbox as CheckboxIcon,
} from '@vicons/ionicons5'
import type { DataTableColumns } from 'naive-ui'
import { getCustomerStats } from '@/api/customer'
import { getEmailStats } from '@/api/email'
import { getTaskStats } from '@/api/task'

const message = useMessage()

const dateRange = ref('30d')

const dateRangeOptions = [
  { label: '最近7天', value: '7d' },
  { label: '最近30天', value: '30d' },
  { label: '最近90天', value: '90d' },
  { label: '今年', value: 'year' },
  { label: '全部', value: 'all' },
]

const metrics = ref({
  total_customers: 0,
  cooperating_customers: 0,
  conversion_rate: 0,
  emails_sent: 0,
  tasks_completed: 0,
})

const countryData = ref<any[]>([])
const statusData = ref<any[]>([])
const taskStatusData = ref<any[]>([])

const countryColumns: DataTableColumns<any> = [
  { title: '国家', key: 'country' },
  { title: '客户数量', key: 'count', sorter: (a, b) => a.count - b.count },
  {
    title: '占比',
    key: 'rate',
    render: (row) => `${row.rate}%`,
    sorter: (a, b) => a.rate - b.rate,
  },
]

const statusColumns: DataTableColumns<any> = [
  { title: '状态', key: 'status' },
  { title: '客户数量', key: 'count', sorter: (a, b) => a.count - b.count },
  { title: '占比', key: 'rate', render: (row) => `${row.rate}%` },
]

const taskStatusColumns: DataTableColumns<any> = [
  { title: '状态', key: 'status' },
  { title: '任务数量', key: 'count', sorter: (a, b) => a.count - b.count },
]

const volumeData = ref<any[]>([])

const volumeColumns: DataTableColumns<any> = [
  { title: '月份', key: 'month' },
  { title: '新增客户', key: 'new_customers' },
  { title: '发送邮件', key: 'emails' },
  { title: '成功转化', key: 'conversions' },
  {
    title: '转化率',
    key: 'rate',
    render: (row) => `${((row.conversions / row.new_customers) * 100).toFixed(1)}%`,
  },
]

const funnel = ref({
  potential: 0,
  contacting: 0,
  cooperating: 0,
  completed: 0,
  potential_to_contact: 0,
  contact_to_cooperate: 0,
  cooperate_to_complete: 0,
  overall: 0,
})

const factorData = ref<any[]>([])

const factorColumns: DataTableColumns<any> = [
  { title: '因素', key: 'factor' },
  {
    title: '影响程度',
    key: 'impact',
    render: (row) => {
      const typeMap: Record<string, any> = { High: 'error', Medium: 'warning', Low: 'default' }
      const textMap: Record<string, string> = { High: '高', Medium: '中', Low: '低' }
      return row.impact
        ? h(NTag, { type: typeMap[row.impact] }, { default: () => textMap[row.impact] })
        : null
    },
  },
  { title: '转化率', key: 'conversion', render: (row) => `${row.conversion}%` },
]

const performanceData = ref<any[]>([])

const performanceColumns: DataTableColumns<any> = [
  { title: '排名', key: 'rank', render: (_, index) => index + 1 },
  { title: '业务员', key: 'name' },
  { title: '客户数', key: 'customers', sorter: (a, b) => a.customers - b.customers },
  { title: '发送邮件', key: 'emails', sorter: (a, b) => a.emails - b.emails },
  { title: '成功转化', key: 'conversions', sorter: (a, b) => a.conversions - b.conversions },
  {
    title: '综合得分',
    key: 'score',
    sorter: (a, b) => a.score - b.score,
    render: (row) =>
      h(NProgress, {
        type: 'line',
        percentage: row.score,
        indicatorPlacement: 'inside',
        processing: true,
      }),
  },
]

async function handleRefresh() {
  await loadAnalyticsData()
  message.success('数据已刷新')
}

async function loadAnalyticsData() {
  try {
    const [customerStats, emailStats, taskStats] = await Promise.all([
      getCustomerStats(),
      getEmailStats(),
      getTaskStats(),
    ])

    const byStatus = customerStats.by_status || {}
    const totalCustomers = customerStats.total || 0
    const cooperating = byStatus.cooperating || 0

    metrics.value = {
      total_customers: totalCustomers,
      cooperating_customers: cooperating,
      conversion_rate: calculateRate(cooperating, totalCustomers),
      emails_sent: emailStats.sent || 0,
      tasks_completed: taskStats.completed || 0,
    }

    countryData.value = Object.entries(customerStats.by_country || {})
      .map(([country, count]) => ({
        country,
        count,
        rate: calculateRate(Number(count), totalCustomers),
      }))
      .sort((left, right) => right.count - left.count)

    statusData.value = Object.entries(byStatus)
      .map(([status, count]) => ({
        status: getCustomerStatusText(status),
        count,
        rate: calculateRate(Number(count), totalCustomers),
      }))
      .sort((left, right) => right.count - left.count)

    taskStatusData.value = [
      { status: '待处理', count: taskStats.pending || 0 },
      { status: '进行中', count: taskStats.in_progress || 0 },
      { status: '已完成', count: taskStats.completed || 0 },
      { status: '逾期', count: taskStats.overdue || 0 },
      { status: '即将到期', count: taskStats.upcoming || 0 },
    ].filter(item => item.count > 0)

    funnel.value = {
      potential: byStatus.potential || 0,
      contacting: byStatus.contacting || 0,
      cooperating,
      completed: cooperating,
      potential_to_contact: calculateRate(byStatus.contacting || 0, byStatus.potential || 0),
      contact_to_cooperate: calculateRate(cooperating, byStatus.contacting || 0),
      cooperate_to_complete: cooperating > 0 ? 100 : 0,
      overall: calculateRate(cooperating, totalCustomers),
    }
  } catch (error: any) {
    message.error(error.message || '加载分析数据失败')
  }
}

function calculateRate(value: number, total: number) {
  if (!total) return 0
  return Number(((value / total) * 100).toFixed(1))
}

function getCustomerStatusText(status: string) {
  const map: Record<string, string> = {
    potential: '潜在客户',
    contacting: '联系中',
    cooperating: '合作中',
    paused: '暂停',
    lost: '流失',
  }
  return map[status] || status
}

onMounted(() => {
  loadAnalyticsData()
})
</script>

<style scoped>
.analytics-page {
  padding: 16px;
}

.metrics-grid {
  margin-bottom: 24px;
}

.metric-card {
  text-align: center;
}

.metric-change {
  margin-top: 8px;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.metric-change.positive {
  color: #18a058;
}

.metric-change.negative {
  color: #d03050;
}

.analytics-tabs {
  margin-top: 24px;
}

.map-container {
  min-height: 400px;
}

</style>
