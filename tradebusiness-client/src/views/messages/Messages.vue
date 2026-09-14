<template>
  <div class="messages-page">
    <n-card title="消息中心" :bordered="false">
      <template #header-extra>
        <n-space>
          <n-badge :value="unreadCount" :max="99">
            <n-button @click="handleMarkAllRead">
              全部已读
            </n-button>
          </n-badge>
        </n-space>
      </template>

      <!-- 消息统计 -->
      <n-grid :cols="4" :x-gap="16" class="stats-grid">
        <n-grid-item>
          <n-statistic label="全部消息" :value="stats.total || 0" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="未读" :value="unreadCount" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="邮件通知" :value="stats.email || 0" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="系统通知" :value="stats.system || 0" />
        </n-grid-item>
      </n-grid>

      <!-- 消息类型筛选 -->
      <n-space class="filter-bar">
        <n-button
          :type="filterType === 'all' ? 'primary' : 'default'"
          @click="filterType = 'all'"
        >
          全部
        </n-button>
        <n-button
          :type="filterType === 'email' ? 'primary' : 'default'"
          @click="filterType = 'email'"
        >
          邮件通知
        </n-button>
        <n-button
          :type="filterType === 'task' ? 'primary' : 'default'"
          @click="filterType = 'task'"
        >
          任务提醒
        </n-button>
        <n-button
          :type="filterType === 'customer' ? 'primary' : 'default'"
          @click="filterType = 'customer'"
        >
         客户动态
        </n-button>
        <n-button
          :type="filterType === 'system' ? 'primary' : 'default'"
          @click="filterType = 'system'"
        >
          系统通知
        </n-button>
      </n-space>

      <!-- 消息列表 -->
      <n-list v-if="!loading && filteredMessages.length > 0" hoverable clickable bordered>
        <n-list-item v-for="message in filteredMessages" :key="message.id" @click="handleViewMessage(message)">
          <n-thing>
            <template #header>
              <n-space align="center" :size="8">
                <n-badge v-if="!message.is_read" dot />
                <n-tag :type="getMessageTypeColor(message.category)" size="small">
                  {{ getMessageTypeText(message.category) }}
                </n-tag>
                <span class="message-title" :class="{ unread: !message.is_read }">
                  {{ message.title }}
                </span>
              </n-space>
            </template>

            <template #description>
              <n-text depth="3" class="message-content">
                {{ message.message }}
              </n-text>
            </template>

            <template #action>
              <n-space>
                <n-button text type="primary" size="small" @click.stop="handleAction(message)">
                  查看详情
                </n-button>
                <n-button text size="small" @click.stop="handleDelete(message)">
                  删除
                </n-button>
              </n-space>
            </template>
          </n-thing>

          <div class="message-time">
            {{ formatTime(message.created_at) }}
          </div>
        </n-list-item>
      </n-list>

      <!-- 空状态 -->
      <n-empty v-else-if="!loading" description="还没有消息">
        <template #extra>
          <n-text depth="3">当有新消息时，它们会显示在这里</n-text>
        </template>
      </n-empty>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-wrapper">
        <n-spin size="large" />
      </div>
    </n-card>

    <!-- 消息详情抽屉 -->
    <n-drawer v-model:show="showDetailDrawer" :width="600" placement="right">
      <n-drawer-content :title="selectedMessage?.title" closable>
        <div v-if="selectedMessage" class="message-detail">
          <n-descriptions :column="1" bordered>
            <n-descriptions-item label="类型">
              <n-tag :type="getMessageTypeColor(selectedMessage.category)">
                {{ getMessageTypeText(selectedMessage.category) }}
              </n-tag>
            </n-descriptions-item>
            <n-descriptions-item label="时间">
              {{ formatTime(selectedMessage.created_at) }}
            </n-descriptions-item>
          </n-descriptions>

          <n-divider />

          <div class="message-content-full">
            {{ selectedMessage.message }}
          </div>

          <n-divider />

          <!-- 相关操作 -->
          <n-space v-if="selectedMessage.action_url">
            <n-button type="primary" @click="handleGoToAction(selectedMessage)">
              查看详情
            </n-button>
          </n-space>
        </div>
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import {
  deleteNotification,
  getNotifications,
  getUnreadCount,
  markAllNotificationsRead,
  markNotificationRead,
  type Notification,
} from '@/api/notification'
import { useUserStore } from '@/store/modules/user'

interface MessageView extends Notification {
  category: string
  action_url?: string
}

const router = useRouter()
const message = useMessage()
const userStore = useUserStore()

const loading = ref(false)
const filterType = ref<string>('all')
const showDetailDrawer = ref(false)
const selectedMessage = ref<MessageView | null>(null)

const stats = ref({
  total: 0,
  unread: 0,
  email: 0,
  task: 0,
  customer: 0,
  system: 0,
})

const messages = ref<MessageView[]>([])

const unreadCount = computed(() => {
  return messages.value.filter(m => !m.is_read).length
})

const filteredMessages = computed(() => {
  if (filterType.value === 'all') {
    return messages.value
  }
  return messages.value.filter(item => item.category === filterType.value)
})

let ws: WebSocket | null = null
let reconnectTimer: ReturnType<typeof setTimeout> | null = null

function getWebSocketBaseUrl() {
  const configuredUrl = import.meta.env.VITE_APP_WS_URL
  if (configuredUrl && configuredUrl !== 'wss://api.example.com') {
    return configuredUrl.replace(/\/$/, '')
  }

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${protocol}//${window.location.host}`
}

function connectWebSocket() {
  const userId = userStore.userInfo?.id
  if (!userId) return

  ws = new WebSocket(`${getWebSocketBaseUrl()}/api/v1/notifications/ws/${userId}`)
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    if (data.type === 'connected' || data.type === 'pong') return
    handleNewMessage(normalizeNotification(data))
  }
  ws.onclose = () => {
    reconnectTimer = setTimeout(connectWebSocket, 5000)
  }
}

function handleNewMessage(data: MessageView) {
  messages.value.unshift(data)
  updateStats()

  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification(data.title, {
      body: data.message,
      icon: '/logo.png',
    })
  }
}

async function fetchMessages() {
  loading.value = true
  try {
    const [response, unreadResponse] = await Promise.all([
      getNotifications({ skip: 0, limit: 100 }),
      getUnreadCount(),
    ])
    messages.value = response.items.map(normalizeNotification)
    updateStats(unreadResponse.count)
  } catch (error: any) {
    message.error(error.message || '加载消息失败')
  } finally {
    loading.value = false
  }
}

function updateStats(unread?: number) {
  stats.value = {
    total: messages.value.length,
    unread: unread ?? messages.value.filter(m => !m.is_read).length,
    email: messages.value.filter(m => m.category === 'email').length,
    task: messages.value.filter(m => m.category === 'task').length,
    customer: messages.value.filter(m => m.category === 'customer').length,
    system: messages.value.filter(m => m.category === 'system').length,
  }
}

async function handleViewMessage(msg: MessageView) {
  selectedMessage.value = msg
  showDetailDrawer.value = true

  if (!msg.is_read) {
    await markNotificationRead(msg.id)
    msg.is_read = true
    updateStats()
  }
}

function handleAction(msg: MessageView) {
  if (msg.action_url) {
    router.push(msg.action_url)
  }
}

function handleGoToAction(msg: MessageView) {
  showDetailDrawer.value = false
  handleAction(msg)
}

async function handleDelete(msg: MessageView) {
  await deleteNotification(msg.id)
  messages.value = messages.value.filter(item => item.id !== msg.id)
  updateStats()
  message.success('消息已删除')
}

async function handleMarkAllRead() {
  await markAllNotificationsRead()
  messages.value.forEach(item => {
    item.is_read = true
  })
  updateStats()
  message.success('已标记全部为已读')
}

function getMessageTypeText(type: string) {
  const map: Record<string, string> = {
    email: '邮件通知',
    task: '任务提醒',
    customer: '客户动态',
    system: '系统通知',
  }
  return map[type] || type
}

function getMessageTypeColor(type: string) {
  const map: Record<string, any> = {
    email: 'info',
    task: 'warning',
    customer: 'success',
    system: 'default',
  }
  return map[type] || 'default'
}

function formatTime(time: string) {
  return new Date(time).toLocaleString('zh-CN')
}

function normalizeNotification(notification: Notification): MessageView {
  return {
    ...notification,
    category: normalizeMessageCategory(notification.type),
    action_url: resolveActionUrl(notification),
  }
}

function normalizeMessageCategory(type: string) {
  if (type.includes('email')) return 'email'
  if (type.includes('task')) return 'task'
  if (type.includes('customer')) return 'customer'
  return 'system'
}

function resolveActionUrl(notification: Notification) {
  const data = notification.data || {}
  if (data.email_id || notification.type.includes('email')) return '/emails/inbox'
  if (data.task_id || notification.type.includes('task')) return '/tasks'
  if (data.customer_id || notification.type.includes('customer')) return '/customers/my'
  return undefined
}

onMounted(() => {
  fetchMessages()
  connectWebSocket()

  // 请求浏览器通知权限
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission()
  }
})

onUnmounted(() => {
  if (ws) {
    ws.close()
  }
  if (reconnectTimer) {
    clearTimeout(reconnectTimer)
  }
})
</script>

<style scoped>
.messages-page {
  padding: 16px;
}

.stats-grid {
  margin-bottom: 24px;
}

.filter-bar {
  margin-bottom: 16px;
}

.message-title {
  font-weight: 500;
  flex: 1;
}

.message-title.unread {
  font-weight: 600;
}

.message-content {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.message-time {
  font-size: 12px;
  color: #999;
}

.message-detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.message-content-full {
  padding: 16px;
  background: #f5f5f5;
  border-radius: 4px;
  white-space: pre-wrap;
  line-height: 1.6;
}

.loading-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}
</style>



