<template>
  <div class="tasks-page">
    <n-card title="任务管理" :bordered="false">
      <template #header-extra>
        <n-space>
          <n-button type="primary" @click="showCreateModal = true">
            <template #icon>
              <n-icon><AddIcon /></n-icon>
            </template>
            新建任务
          </n-button>
        </n-space>
      </template>

      <!-- 统计卡片 -->
      <n-grid :cols="5" :x-gap="16" class="stats-grid">
        <n-grid-item>
          <n-statistic label="全部任务" :value="stats.total || 0" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="待处理" :value="stats.pending || 0" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="进行中" :value="stats.in_progress || 0" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="已完成" :value="stats.completed || 0" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="今日任务" :value="stats.today || 0" />
        </n-grid-item>
      </n-grid>

      <!-- 筛选栏 -->
      <n-space class="filter-bar" vertical>
        <n-input
          v-model:value="searchKeyword"
          placeholder="搜索任务"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <n-icon><SearchIcon /></n-icon>
          </template>
        </n-input>

        <n-space>
          <n-select
            v-model:value="filterStatus"
            placeholder="筛选状态"
            clearable
            :style="{ width: '150px' }"
            :options="statusOptions"
          />
          <n-select
            v-model:value="filterPriority"
            placeholder="筛选优先级"
            clearable
            :style="{ width: '150px' }"
            :options="priorityOptions"
          />
          <n-button type="primary" @click="handleSearch">
            搜索
          </n-button>
          <n-button @click="handleReset">
            重置
          </n-button>
        </n-space>
      </n-space>

      <!-- 任务列表 -->
      <n-list v-if="!loading && tasks.length > 0" bordered>
        <n-list-item v-for="task in tasks" :key="task.id">
          <n-thing>
            <template #header>
              <n-space align="center" :size="8">
                <n-checkbox
                  :checked="task.status === 'completed'"
                  @update:checked="handleToggleComplete(task)"
                />
                <span
                  class="task-title"
                  :class="{ completed: task.status === 'completed' }"
                >
                  {{ task.title }}
                </span>
                <n-tag :type="getStatusType(task.status)" size="small">
                  {{ getTaskStatusText(task.status) }}
                </n-tag>
                <n-tag :type="getPriorityType(task.priority)" size="small">
                  {{ getPriorityText(task.priority) }}
                </n-tag>
              </n-space>
            </template>

            <template #description>
              <n-space vertical :size="4">
                <n-text v-if="task.description" depth="3">
                  {{ task.description }}
                </n-text>
                <n-space :size="8">
                  <span v-if="task.customer_id" class="task-meta">
                    <n-icon><PersonIcon /></n-icon>
                    关联客户
                  </span>
                  <span v-if="task.due_date" class="task-meta">
                    <n-icon><CalendarIcon /></n-icon>
                    {{ formatDate(task.due_date) }}
                  </span>
                  <span v-if="task.type" class="task-meta">
                    <n-icon><ListIcon /></n-icon>
                    {{ getTaskTypeText(task.type) }}
                  </span>
                </n-space>
              </n-space>
            </template>

            <template #action>
              <n-space>
                <n-button text type="primary" size="small" @click="handleEdit(task)">
                  编辑
                </n-button>
                <n-dropdown
                  :options="getDropdownOptions(task)"
                  @select="(key: string) => handleDropdownSelect(key, task)"
                >
                  <n-button text size="small">
                    <template #icon>
                      <n-icon><MoreIcon /></n-icon>
                    </template>
                  </n-button>
                </n-dropdown>
              </n-space>
            </template>
          </n-thing>
        </n-list-item>
      </n-list>

      <!-- 空状态 -->
      <n-empty v-else-if="!loading" description="还没有任务">
        <template #extra>
          <n-button size="small" type="primary" @click="showCreateModal = true">
            创建第一个任务
          </n-button>
        </template>
      </n-empty>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-wrapper">
        <n-spin size="large" />
      </div>
    </n-card>

    <!-- 创建/编辑任务对话框 -->
    <n-modal v-model:show="showCreateModal" preset="dialog" :title="editingTask ? '编辑任务' : '新建任务'">
      <n-form ref="formRef" :model="taskForm" label-placement="left" label-width="80px">
        <n-form-item label="任务标题" path="title" :rule="{ required: true, message: '请输入任务标题' }">
          <n-input v-model:value="taskForm.title" placeholder="任务标题" />
        </n-form-item>

        <n-form-item label="任务描述">
          <n-input v-model:value="taskForm.description" type="textarea" placeholder="任务描述" />
        </n-form-item>

        <n-form-item label="任务类型">
          <n-select
            v-model:value="taskForm.type"
            :options="typeOptions"
            placeholder="选择任务类型"
          />
        </n-form-item>

        <n-form-item label="优先级">
          <n-select
            v-model:value="taskForm.priority"
            :options="priorityOptions"
            placeholder="选择优先级"
          />
        </n-form-item>

        <n-form-item label="截止日期">
          <n-date-picker
            v-model:value="taskForm.due_date"
            type="datetime"
            placeholder="选择截止日期"
            :style="{ width: '100%' }"
          />
        </n-form-item>

        <n-form-item label="关联客户">
          <n-select
            v-model:value="taskForm.customer_id"
            :options="customerOptions"
            placeholder="选择关联客户（可选）"
            clearable
            filterable
          />
        </n-form-item>
      </n-form>

      <template #action>
        <n-space>
          <n-button @click="showCreateModal = false">取消</n-button>
          <n-button type="primary" :loading="submitting" @click="handleSubmit">
            确定
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useMessage, useDialog } from 'naive-ui'
import type { FormInst } from 'naive-ui'
import {
  Add as AddIcon,
  Search as SearchIcon,
  Person as PersonIcon,
  Calendar as CalendarIcon,
  List as ListIcon,
  EllipsisHorizontal as MoreIcon,
} from '@vicons/ionicons5'
import {
  completeTask,
  createTask,
  getTaskStats,
  getTasks,
  updateTask,
  type Task,
} from '@/api/task'
import { useUserStore } from '@/store/modules/user'

const message = useMessage()
const dialog = useDialog()
const userStore = useUserStore()

const loading = ref(false)
const tasks = ref<Task[]>([])
const showCreateModal = ref(false)
const editingTask = ref<Task | null>(null)
const submitting = ref(false)
const formRef = ref<FormInst | null>(null)

const searchKeyword = ref('')
const filterStatus = ref<string | null>(null)
const filterPriority = ref<string | null>(null)

const stats = ref({
  total: 0,
  pending: 0,
  in_progress: 0,
  completed: 0,
  today: 0,
})

const taskForm = reactive({
  title: '',
  description: '',
  type: 'call',
  priority: 'medium',
  due_date: null as number | null,
  customer_id: null as string | null,
})

const statusOptions = [
  { label: '待处理', value: 'pending' },
  { label: '进行中', value: 'in_progress' },
  { label: '已完成', value: 'completed' },
]

const priorityOptions = [
  { label: '低', value: 'low' },
  { label: '中', value: 'medium' },
  { label: '高', value: 'high' },
  { label: '紧急', value: 'urgent' },
]

const typeOptions = [
  { label: '电话', value: 'call' },
  { label: '邮件', value: 'email' },
  { label: '会议', value: 'meeting' },
  { label: '跟进', value: 'followup' },
]

const customerOptions = ref<any[]>([])

async function fetchTasks() {
  loading.value = true
  try {
    const [taskResponse, taskStats] = await Promise.all([
      getTasks({
        limit: 100,
        status: filterStatus.value || undefined,
        priority: filterPriority.value || undefined,
      }),
      getTaskStats(),
    ])
    const keyword = searchKeyword.value.trim().toLowerCase()
    tasks.value = keyword
      ? taskResponse.items.filter(task =>
          task.title.toLowerCase().includes(keyword) ||
          (task.description || '').toLowerCase().includes(keyword)
        )
      : taskResponse.items
    stats.value = {
      total: taskStats.total,
      pending: taskStats.pending,
      in_progress: taskStats.in_progress,
      completed: taskStats.completed,
      today: taskStats.upcoming || 0,
    }
    updateStats()
  } catch (error: any) {
    message.error(error.message || '加载任务失败')
  } finally {
    loading.value = false
  }
}

function updateStats() {
  const today = new Date().toDateString()
  stats.value = {
    total: tasks.value.length,
    pending: tasks.value.filter(t => t.status === 'pending').length,
    in_progress: tasks.value.filter(t => t.status === 'in_progress').length,
    completed: tasks.value.filter(t => t.status === 'completed').length,
    today: tasks.value.filter(t => t.due_date && new Date(t.due_date).toDateString() === today).length,
  }
}

function handleSearch() {
  fetchTasks()
}

function handleReset() {
  searchKeyword.value = ''
  filterStatus.value = null
  filterPriority.value = null
  fetchTasks()
}

function handleToggleComplete(task: Task) {
  if (task.status === 'completed') {
    message.info('已完成任务不能在此处恢复，请通过编辑修改状态')
    return
  }
  completeTask(task.id)
    .then(() => {
      message.success('任务已完成')
      fetchTasks()
    })
    .catch((error: any) => {
      message.error(error.message || '更新任务失败')
    })
}

function handleEdit(task: Task) {
  editingTask.value = task
  Object.assign(taskForm, {
    title: task.title,
    description: task.description || '',
    type: task.type || 'call',
    priority: task.priority,
    due_date: task.due_date ? new Date(task.due_date).getTime() : null,
    customer_id: task.customer_id || null,
  })
  showCreateModal.value = true
}

function handleSubmit() {
  if (!formRef.value) return

  formRef.value.validate((errors) => {
    if (!errors) {
      submitting.value = true

      const payload = {
        title: taskForm.title,
        description: taskForm.description,
        type: taskForm.type,
        priority: taskForm.priority,
        due_date: taskForm.due_date ? new Date(taskForm.due_date).toISOString() : null,
        customer_id: taskForm.customer_id,
      }

      const isEditing = Boolean(editingTask.value)
      const request = editingTask.value
        ? updateTask(editingTask.value.id, payload)
        : createTask({
            ...payload,
            assigned_to: userStore.userInfo?.id || '',
          })

      request
        .then(() => {
          message.success(isEditing ? '任务已更新' : '任务已创建')
          showCreateModal.value = false
          editingTask.value = null
          resetTaskForm()
          fetchTasks()
        })
        .catch((error: any) => {
          message.error(error.message || '保存任务失败')
        })
        .finally(() => {
          submitting.value = false
        })
    }
  })
}

function getDropdownOptions(task: Task) {
  return [
    {
      label: '标记完成',
      key: 'complete',
      disabled: task.status === 'completed',
    },
    {
      label: '删除',
      key: 'delete',
      disabled: true,
    },
  ]
}

function handleDropdownSelect(key: string, task: Task) {
  if (key === 'complete') {
    handleToggleComplete(task)
  } else if (key === 'delete') {
    dialog.warning({
      title: '删除任务',
      content: '删除任务需要管理员权限，请在管理端操作。',
      positiveText: '确定',
    })
  }
}

function getTaskStatusText(status: string) {
  const map: Record<string, string> = {
    pending: '待处理',
    in_progress: '进行中',
    completed: '已完成',
    cancelled: '已取消',
  }
  return map[status] || status
}

function getStatusType(status: string) {
  const map: Record<string, string> = {
    pending: 'default',
    in_progress: 'info',
    completed: 'success',
    cancelled: 'warning',
  }
  return map[status] || 'default'
}

function getPriorityText(priority: string) {
  const map: Record<string, string> = {
    low: '低',
    medium: '中',
    high: '高',
    urgent: '紧急',
  }
  return map[priority] || priority
}

function getPriorityType(priority: string) {
  const map: Record<string, string> = {
    low: 'info',
    medium: 'default',
    high: 'warning',
    urgent: 'error',
  }
  return map[priority] || 'default'
}

function getTaskTypeText(type: string) {
  const map: Record<string, string> = {
    call: '电话',
    email: '邮件',
    meeting: '会议',
    followup: '跟进',
  }
  return map[type] || type
}

function formatDate(dateStr: string) {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = date.getTime() - now.getTime()
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) return '今天'
  if (days === 1) return '明天'
  if (days === -1) return '昨天'

  return date.toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchTasks()
})

function resetTaskForm() {
  Object.assign(taskForm, {
    title: '',
    description: '',
    type: 'call',
    priority: 'medium',
    due_date: null,
    customer_id: null,
  })
}
</script>

<style scoped>
.tasks-page {
  padding: 16px;
}

.stats-grid {
  margin-bottom: 24px;
}

.filter-bar {
  margin-bottom: 16px;
}

.task-title {
  font-weight: 500;
  flex: 1;
}

.task-title.completed {
  text-decoration: line-through;
  color: #999;
}

.task-meta {
  font-size: 13px;
  color: #666;
  display: flex;
  align-items: center;
  gap: 4px;
}

.loading-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}
</style>
