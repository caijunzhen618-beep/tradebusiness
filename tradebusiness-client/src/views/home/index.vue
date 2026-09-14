<template>
  <div class="home">
    <n-space vertical :size="24">
      <!-- 欢迎卡片 -->
      <n-card>
        <n-h2>欢迎, {{ userStore.fullName }}!</n-h2>
        <n-p>今天是个好日子，开始你的一天吧！</n-P>
      </n-card>

      <!-- 统计数据 -->
      <n-grid :cols="4" :x-gap="16">
        <n-gi>
          <n-card>
            <n-statistic label="我的客户" :value="stats.myCustomers" />
          </n-card>
        </n-gi>
        <n-gi>
          <n-card>
            <n-statistic label="今日任务" :value="stats.todayTasks" />
          </n-card>
        </n-gi>
        <n-gi>
          <n-card>
            <n-statistic label="未读消息" :value="stats.unreadMessages" />
          </n-card>
        </n-gi>
        <n-gi>
          <n-card>
            <n-statistic label="待跟进客户" :value="stats.pendingFollowups" />
          </n-card>
        </n-gi>
      </n-grid>

      <!-- 快速操作 -->
      <n-card title="快速操作">
        <n-space :size="16">
          <n-button type="primary" @click="router.push({ name: 'DiscoverCustomers' })">
            发现新客户
          </n-button>
          <n-button type="warning" @click="router.push({ name: 'LeadGenerationOverview' })">
            AI 获客
          </n-button>
          <n-button type="info" @click="router.push({ name: 'ComposeEmail' })">
            写邮件
          </n-button>
          <n-button type="success" @click="router.push({ name: 'Tasks' })">
            查看任务
          </n-button>
        </n-space>
      </n-card>

      <!-- 最近活动 -->
      <n-card title="最近活动">
        <n-timeline>
          <n-timeline-item
            v-for="activity in recentActivities"
            :key="activity.id"
            :type="activity.type"
            :title="activity.title"
            :time="activity.time"
          />
        </n-timeline>
      </n-card>
    </n-space>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getCustomerStats, getMyCustomers } from '@/api/customer'
import { get } from '@/api/request'
import { useUserStore } from '@/store/modules/user'

const router = useRouter()
const userStore = useUserStore()

interface TaskStats {
  pending?: number
  upcoming?: number
}

interface UnreadCount {
  count: number
}

const stats = ref({
  myCustomers: 0,
  todayTasks: 0,
  unreadMessages: 0,
  pendingFollowups: 0,
})

const recentActivities = ref([
  {
    id: 1,
    type: 'success',
    title: '新增客户：尼日利亚 Lagos 货运公司',
    time: '2 小时前',
  },
  {
    id: 2,
    type: 'info',
    title: '发送 20 封营销邮件',
    time: '4 小时前',
  },
  {
    id: 3,
    type: 'warning',
    title: '收到 3 封客户回复',
    time: '昨天',
  },
])

onMounted(async () => {
  try {
    const [myCustomers, customerStats, taskStats, unreadCount] = await Promise.all([
      getMyCustomers({ page: 1, page_size: 1 }),
      getCustomerStats(),
      get<TaskStats>('/api/v1/tasks/stats'),
      get<UnreadCount>('/api/v1/notifications/unread-count'),
    ])

    stats.value = {
      myCustomers: myCustomers.total,
      todayTasks: (taskStats.pending || 0) + (taskStats.upcoming || 0),
      unreadMessages: unreadCount.count,
      pendingFollowups: customerStats.by_status?.contacting || 0,
    }
  } catch (error) {
    console.error('加载首页统计失败:', error)
  }
})
</script>

<style scoped>
.home {
  max-width: 1200px;
}
</style>
