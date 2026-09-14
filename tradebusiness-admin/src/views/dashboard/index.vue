<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #409eff">
              <el-icon :size="30"><User /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalCustomers }}</div>
              <div class="stat-label">总客户数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #67c23a">
              <el-icon :size="30"><SuccessFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.cooperatingCustomers }}</div>
              <div class="stat-label">合作客户</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #e6a23c">
              <el-icon :size="30"><Message /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.emailsSent }}</div>
              <div class="stat-label">已发送邮件</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" style="background-color: #f56c6c">
              <el-icon :size="30"><UserFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalUsers }}</div>
              <div class="stat-label">业务员数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>客户地区分布</span>
            </div>
          </template>
          <div ref="countryChartRef" style="height: 300px" />
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最近活动</span>
            </div>
          </template>
          <el-timeline v-if="recentActivities.length > 0">
            <el-timeline-item
              v-for="activity in recentActivities"
              :key="activity.id"
              :timestamp="activity.timestamp"
            >
              {{ activity.content }}
            </el-timeline-item>
          </el-timeline>
          <el-empty v-else description="暂无最近活动" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User, SuccessFilled, Message, UserFilled } from '@element-plus/icons-vue'
import * as echarts from 'echarts'
import { getCustomerStats } from '@/api/customer'
import { getEmailStats } from '@/api/email'
import { getUserList } from '@/api/user'

interface CustomerStats {
  total: number
  by_status: Record<string, number>
  by_country: Record<string, number>
  top_countries: Array<[string, number]>
}

interface Activity {
  id: string
  content: string
  timestamp: string
}

interface CountryChartItem {
  name: string
  value: number
}

const stats = ref({
  totalCustomers: 0,
  cooperatingCustomers: 0,
  emailsSent: 0,
  totalUsers: 0,
})

const recentActivities = ref<Activity[]>([])
const countryChartRef = ref<HTMLElement>()
const countryData = ref<CountryChartItem[]>([])

let countryChart: echarts.ECharts | null = null

const fetchStats = async () => {
  try {
    const [customerRes, emailRes, userRes] = await Promise.all([
      getCustomerStats() as Promise<CustomerStats>,
      getEmailStats(),
      getUserList({ skip: 0, limit: 1 }),
    ])

    stats.value = {
      totalCustomers: customerRes.total || 0,
      cooperatingCustomers: customerRes.by_status?.cooperating || 0,
      emailsSent: emailRes.sent || 0,
      totalUsers: userRes.total || 0,
    }

    countryData.value = normalizeCountries(customerRes)
    renderCountryChart()
  } catch (error) {
    console.error('加载统计数据失败', error)
    ElMessage.error('加载统计数据失败')
  }
}

const initCountryChart = () => {
  if (!countryChartRef.value) return
  countryChart = echarts.init(countryChartRef.value)
  renderCountryChart()
}

const renderCountryChart = () => {
  if (!countryChart) return
  if (countryData.value.length === 0) {
    countryChart.setOption({
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
      series: [],
    })
    return
  }

  countryChart.setOption({
    tooltip: {
      trigger: 'item',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
    },
    series: [
      {
        name: '客户数量',
        type: 'pie',
        radius: ['40%', '65%'],
        center: ['58%', '50%'],
        data: countryData.value,
      },
    ],
  })
}

const normalizeCountries = (source: CustomerStats) => {
  const entries = Array.isArray(source.top_countries) && source.top_countries.length > 0
    ? source.top_countries.map(([name, value]) => ({ name, value }))
    : Object.entries(source.by_country || {}).map(([name, value]) => ({ name, value }))

  return entries.filter(item => item.name && item.value > 0)
}

const handleResize = () => {
  countryChart?.resize()
}

onMounted(() => {
  initCountryChart()
  fetchStats()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  countryChart?.dispose()
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.stat-card {
  cursor: pointer;
  transition: all 0.3s;
}

.stat-card:hover {
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.2);
}

.stat-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  border-radius: 8px;
  color: #111111;
}

.stat-info {
  text-align: right;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  margin-top: 5px;
  font-size: 14px;
  color: #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
}
</style>
