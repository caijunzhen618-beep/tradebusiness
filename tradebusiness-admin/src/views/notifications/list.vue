<template>
  <div class="notifications-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>通知中心</h2>
          <div class="header-actions">
            <el-badge :value="unreadCount" :hidden="unreadCount === 0">
              <el-button @click="loadNotifications">刷新</el-button>
            </el-badge>
            <el-dropdown @command="handleBatchAction">
              <el-button>
                批量操作<el-icon class="el-icon--right"><arrow-down /></el-icon>
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="markAll">全部已读</el-dropdown-item>
                  <el-dropdown-item command="deleteRead">删除已读</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </template>

      <!-- 筛选 -->
      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="全部" name="all" />
        <el-tab-pane label="未读" name="unread">
          <template #label>
            <el-badge :value="unreadCount" :hidden="unreadCount === 0">
              未读
            </el-badge>
          </template>
        </el-tab-pane>
        <el-tab-pane label="已读" name="read" />
      </el-tabs>

      <!-- 通知列表 -->
      <div v-loading="loading" class="notification-list" style="margin-top: 20px">
        <div
          v-for="item in notificationList"
          :key="item.id"
          :class="['notification-item', { 'is-read': item.is_read }]"
        >
          <div class="notification-main" @click="handleClick(item)">
            <div class="notification-icon">
              <el-icon :color="getNotificationColor(item.type)">
                <component :is="getNotificationIcon(item.type)" />
              </el-icon>
            </div>
            <div class="notification-content">
              <div class="notification-header">
                <span class="notification-title">{{ item.title }}</span>
                <span class="notification-time">{{ formatTime(item.created_at) }}</span>
              </div>
              <div class="notification-message">{{ item.message }}</div>
            </div>
            <div v-if="!item.is_read" class="unread-dot"></div>
          </div>
          <div class="notification-actions">
            <el-button
              v-if="!item.is_read"
              link
              type="primary"
              size="small"
              @click="handleMarkRead(item)"
            >
              标为已读
            </el-button>
            <el-popconfirm
              title="确定删除此通知吗？"
              @confirm="handleDelete(item)"
            >
              <template #reference>
                <el-button link type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <el-empty
        v-if="!loading && notificationList.length === 0"
        description="暂无通知"
      />

      <!-- 分页 -->
      <el-pagination
        v-if="total > 0"
        v-model:current-page="queryParams.page"
        v-model:page-size="queryParams.pageSize"
        :total="total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        style="margin-top: 20px; justify-content: flex-end"
        @size-change="handlePageChange"
        @current-change="handlePageChange"
      />
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowDown, Bell, Warning, InfoFilled, SuccessFilled } from '@element-plus/icons-vue'
import {
  getNotifications,
  getUnreadCount,
  markAsRead,
  markAllAsRead,
  deleteNotification,
  deleteReadNotifications,
  type Notification,
} from '@/api/notification'
const loading = ref(false)
const notificationList = ref<Notification[]>([])
const total = ref(0)
const unreadCount = ref(0)
const activeTab = ref('all')

const queryParams = reactive({
  page: 1,
  pageSize: 20,
  type: '',
})

let refreshTimer: NodeJS.Timeout | null = null

// 将分页参数转换为后端需要的格式
const getParams = () => {
  const params: any = {
    skip: (queryParams.page - 1) * queryParams.pageSize,
    limit: queryParams.pageSize,
  }

  // 根据当前标签页添加筛选条件
  if (activeTab.value === 'unread') {
    params.unread_only = true
  }

  return params
}

// 加载通知列表
const loadNotifications = async () => {
  try {
    loading.value = true
    const params = getParams()
    const res = await getNotifications(params)
    notificationList.value = res.items
    total.value = res.total
  } catch (error) {
    ElMessage.error('加载通知列表失败')
  } finally {
    loading.value = false
  }
}

// 加载未读数量
const loadUnreadCount = async () => {
  try {
    const res = await getUnreadCount()
    unreadCount.value = res.count
  } catch (error) {
    console.error('加载未读数量失败', error)
  }
}

// Tab切换
const handleTabChange = () => {
  queryParams.page = 1
  loadNotifications()
}

// 分页变化
const handlePageChange = () => {
  loadNotifications()
}

// 点击通知
const handleClick = async (item: Notification) => {
  if (!item.is_read) {
    await handleMarkRead(item)
  }
}

// 标记已读
const handleMarkRead = async (item: Notification) => {
  try {
    await markAsRead(item.id)
    item.is_read = true
    item.read_at = new Date().toISOString()
    loadUnreadCount()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 删除
const handleDelete = async (item: Notification) => {
  try {
    await deleteNotification(item.id)
    ElMessage.success('删除成功')
    loadNotifications()
    loadUnreadCount()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// 批量操作
const handleBatchAction = async (command: string) => {
  try {
    if (command === 'markAll') {
      await markAllAsRead()
      ElMessage.success('已全部标记为已读')
    } else if (command === 'deleteRead') {
      await ElMessageBox.confirm('确定删除所有已读通知吗？', '提示', {
        type: 'warning',
      })
      await deleteReadNotifications()
      ElMessage.success('已删除所有已读通知')
    }
    loadNotifications()
    loadUnreadCount()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('操作失败')
    }
  }
}

// 获取通知图标
const getNotificationIcon = (type: string) => {
  const iconMap: Record<string, any> = {
    new_email: Bell,
    task_reminder: Warning,
    task_assigned: InfoFilled,
    system: SuccessFilled,
  }
  return iconMap[type] || Bell
}

// 获取通知颜色
const getNotificationColor = (type: string) => {
  const colorMap: Record<string, string> = {
    new_email: '#409EFF',
    task_reminder: '#E6A23C',
    task_assigned: '#67C23A',
    system: '#909399',
  }
  return colorMap[type] || '#409EFF'
}

// 格式化时间
const formatTime = (time: string) => {
  const date = new Date(time)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  if (diff < 60000) {
    return '刚刚'
  } else if (diff < 3600000) {
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) {
    return `${Math.floor(diff / 3600000)}小时前`
  } else if (diff < 604800000) {
    return `${Math.floor(diff / 86400000)}天前`
  } else {
    return date.toLocaleDateString('zh-CN')
  }
}

onMounted(() => {
  loadNotifications()
  loadUnreadCount()

  // 每30秒刷新一次未读数量
  refreshTimer = setInterval(() => {
    loadUnreadCount()
  }, 30000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.notifications-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.notification-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px;
  border-bottom: 1px solid #ebeef5;
  cursor: pointer;
  transition: background-color 0.3s;
}

.notification-item:hover {
  background-color: #f5f7fa;
}

.notification-item.is-read {
  opacity: 0.6;
}

.notification-main {
  display: flex;
  align-items: flex-start;
  gap: 15px;
  flex: 1;
}

.notification-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.notification-content {
  flex: 1;
  position: relative;
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.notification-title {
  font-weight: bold;
  font-size: 14px;
}

.notification-time {
  font-size: 12px;
  color: #909399;
}

.notification-message {
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}

.unread-dot {
  position: absolute;
  top: 5px;
  right: -10px;
  width: 8px;
  height: 8px;
  background-color: #f56c6c;
  border-radius: 50%;
}

.notification-actions {
  display: flex;
  gap: 5px;
  flex-shrink: 0;
}
</style>
