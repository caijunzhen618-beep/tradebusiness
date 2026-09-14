<template>
  <div class="statistics-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #409eff">
              <el-icon><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalCustomers || 0 }}</div>
              <div class="stat-label">总客户数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #67c23a">
              <el-icon><Message /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalEmails || 0 }}</div>
              <div class="stat-label">邮件总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #e6a23c">
              <el-icon><List /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalTasks || 0 }}</div>
              <div class="stat-label">任务总数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background: #f56c6c">
              <el-icon><Warning /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.overdueTasks || 0 }}</div>
              <div class="stat-label">逾期任务</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 客户趋势 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>客户状态分布</span>
              <el-button text @click="refreshData">刷新</el-button>
            </div>
          </template>
          <div ref="customerChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>

      <!-- 邮件统计 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>邮件发送统计</span>
              <el-button text @click="refreshData">刷新</el-button>
            </div>
          </template>
          <div ref="emailChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <!-- 任务状态分布 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>任务状态分布</span>
              <el-button text @click="refreshData">刷新</el-button>
            </div>
          </template>
          <div ref="taskChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>

      <!-- 客户分布 -->
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>客户地区分布</span>
              <el-button text @click="refreshData">刷新</el-button>
            </div>
          </template>
          <div ref="regionChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 详细数据表格 -->
    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>业务员业绩排名</span>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="loadPerformanceData"
          />
        </div>
      </template>
      <el-table :data="performanceData" style="width: 100%" empty-text="暂无业绩聚合数据">
        <el-table-column type="index" label="排名" width="80" />
        <el-table-column prop="user_name" label="业务员" />
        <el-table-column prop="customer_count" label="新增客户" sortable />
        <el-table-column prop="email_count" label="发送邮件" sortable />
        <el-table-column prop="task_count" label="完成任务" sortable />
        <el-table-column label="业绩评分">
          <template #default="{ row }">
            <el-rate
              v-model="row.rating"
              disabled
              show-score
              text-color="#ff9900"
            />
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Message, List, Warning } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getCustomerStats } from '@/api/customer'
import { getEmailStats } from '@/api/email'
import { getTaskStats } from '@/api/task'

interface PerformanceRow {
  user_name: string
  customer_count: number
  email_count: number
  task_count: number
  rating: number
}

interface CustomerStats {
  total: number
  by_status: Record<string, number>
  by_country: Record<string, number>
  top_countries: Array<[string, number]>
}

interface ChartEntry {
  name: string
  value: number
}

const stats = ref({
  totalCustomers: 0,
  totalEmails: 0,
  totalTasks: 0,
  overdueTasks: 0,
})

const performanceData = ref<PerformanceRow[]>([])
const dateRange = ref()
const customerStatusData = ref<ChartEntry[]>([])
const emailStatusData = ref<ChartEntry[]>([])
const taskStatusData = ref<ChartEntry[]>([])
const countryData = ref<ChartEntry[]>([])

const customerChartRef = ref<HTMLElement>()
const emailChartRef = ref<HTMLElement>()
const taskChartRef = ref<HTMLElement>()
const regionChartRef = ref<HTMLElement>()

let customerChart: echarts.ECharts | null = null
let emailChart: echarts.ECharts | null = null
let taskChart: echarts.ECharts | null = null
let regionChart: echarts.ECharts | null = null

const loadStats = async () => {
  try {
    const [customerRes, emailRes, taskRes] = await Promise.all([
      getCustomerStats() as Promise<CustomerStats>,
      getEmailStats(),
      getTaskStats(),
    ])

    stats.value = {
      totalCustomers: customerRes.total || 0,
      totalEmails: emailRes.total || 0,
      totalTasks: taskRes.total || 0,
      overdueTasks: taskRes.overdue || 0,
    }

    customerStatusData.value = normalizeRecord(customerRes.by_status, getCustomerStatusText)
    emailStatusData.value = [
      { name: '已发送', value: emailRes.sent || 0 },
      { name: '已打开', value: emailRes.opened || emailRes.opened_count || 0 },
      { name: '已回复', value: emailRes.replied || 0 },
      { name: '失败', value: emailRes.failed || 0 },
    ].filter(item => item.value > 0)
    taskStatusData.value = [
      { name: '待处理', value: taskRes.pending || 0 },
      { name: '进行中', value: taskRes.in_progress || 0 },
      { name: '已完成', value: taskRes.completed || 0 },
      { name: '逾期', value: taskRes.overdue || 0 },
      { name: '即将到期', value: taskRes.upcoming || 0 },
    ].filter(item => item.value > 0)
    countryData.value = normalizeCountries(customerRes)

    renderCharts()
  } catch (error) {
    console.error('加载统计数据失败', error)
    ElMessage.error('加载统计数据失败')
  }
}

const initCustomerChart = () => {
  if (!customerChartRef.value) return

  customerChart = echarts.init(customerChartRef.value)
  renderCustomerChart()
}

const renderCustomerChart = () => {
  if (!customerChart) return
  if (customerStatusData.value.length === 0) {
    customerChart.setOption(getEmptyOption())
    return
  }

  customerChart.setOption({
    tooltip: {
      trigger: 'item',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
    },
    series: [
      {
        name: '客户状态',
        type: 'pie',
        radius: '60%',
        data: customerStatusData.value,
      },
    ],
  })
}

const initEmailChart = () => {
  if (!emailChartRef.value) return

  emailChart = echarts.init(emailChartRef.value)
  renderEmailChart()
}

const renderEmailChart = () => {
  if (!emailChart) return
  if (emailStatusData.value.length === 0) {
    emailChart.setOption(getEmptyOption())
    return
  }

  emailChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
    },
    xAxis: {
      type: 'category',
      data: emailStatusData.value.map(item => item.name),
    },
    yAxis: {
      type: 'value',
    },
    series: [
      {
        name: '邮件数量',
        type: 'bar',
        data: emailStatusData.value.map(item => item.value),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#67c23a' },
            { offset: 1, color: '#85ce61' },
          ]),
        },
      },
    ],
  })
}

const initTaskChart = () => {
  if (!taskChartRef.value) return

  taskChart = echarts.init(taskChartRef.value)
  renderTaskChart()
}

const renderTaskChart = () => {
  if (!taskChart) return
  if (taskStatusData.value.length === 0) {
    taskChart.setOption(getEmptyOption())
    return
  }

  taskChart.setOption({
    tooltip: {
      trigger: 'item',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
    },
    series: [
      {
        name: '任务状态',
        type: 'pie',
        radius: '60%',
        data: taskStatusData.value,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
      },
    ],
  })
}

const initRegionChart = () => {
  if (!regionChartRef.value) return

  regionChart = echarts.init(regionChartRef.value)
  renderRegionChart()
}

const renderRegionChart = () => {
  if (!regionChart) return
  if (countryData.value.length === 0) {
    regionChart.setOption(getEmptyOption())
    return
  }

  regionChart.setOption({
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
    },
    xAxis: {
      type: 'value',
    },
    yAxis: {
      type: 'category',
      data: countryData.value.map(item => item.name),
    },
    series: [
      {
        name: '客户数量',
        type: 'bar',
        data: countryData.value.map(item => item.value),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
            { offset: 0, color: '#409eff' },
            { offset: 1, color: '#66b1ff' },
          ]),
        },
      },
    ],
  })
}

const loadPerformanceData = async () => {
  performanceData.value = []
}

const refreshData = async () => {
  await loadStats()
  ElMessage.success('数据已刷新')
}

const handleResize = () => {
  customerChart?.resize()
  emailChart?.resize()
  taskChart?.resize()
  regionChart?.resize()
}

const renderCharts = () => {
  renderCustomerChart()
  renderEmailChart()
  renderTaskChart()
  renderRegionChart()
}

const normalizeRecord = (
  source: Record<string, number> | undefined,
  labelFormatter?: (key: string) => string
) => {
  return Object.entries(source || {})
    .map(([name, value]) => ({
      name: labelFormatter ? labelFormatter(name) : name,
      value,
    }))
    .filter(item => item.value > 0)
}

const normalizeCountries = (source: CustomerStats) => {
  const entries = Array.isArray(source.top_countries) && source.top_countries.length > 0
    ? source.top_countries.map(([name, value]) => ({ name, value }))
    : normalizeRecord(source.by_country)

  return entries
    .filter(item => item.name && item.value > 0)
    .sort((left, right) => left.value - right.value)
}

const getCustomerStatusText = (status: string) => {
  const map: Record<string, string> = {
    potential: '潜在客户',
    contacted: '已联系',
    interested: '有意向',
    quoted: '已报价',
    customer: '成交客户',
    lost: '已流失',
  }
  return map[status] || status
}

const getEmptyOption = () => ({
  title: {
    text: '暂无数据',
    left: 'center',
    top: 'middle',
    textStyle: {
      color: '#909399',
      fontSize: 14,
      fontWeight: 'normal',
    },
  },
  xAxis: { show: false },
  yAxis: { show: false },
  series: [],
})

onMounted(() => {
  setTimeout(() => {
    initCustomerChart()
    initEmailChart()
    initTaskChart()
    initRegionChart()
    loadStats()
    loadPerformanceData()
  }, 100)

  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  customerChart?.dispose()
  emailChart?.dispose()
  taskChart?.dispose()
  regionChart?.dispose()

  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.statistics-container {
  padding: 20px;
}

.stat-card {
  cursor: pointer;
  transition: transform 0.3s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 30px;
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
