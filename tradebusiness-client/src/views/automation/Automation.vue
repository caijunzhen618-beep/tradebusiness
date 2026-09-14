<template>
  <div class="automation-page">
    <n-card title="自动化管理" :bordered="false">
      <n-tabs v-model:value="activeTab" type="line" animated>
        <!-- 定时任务 -->
        <n-tab-pane name="scheduled" tab="定时任务">
          <n-card title="定时任务列表" size="small" :bordered="false">
            <template #header-extra>
              <n-button type="primary" size="small" @click="showCreateScheduledTask = true">
                新建任务
              </n-button>
            </template>

            <n-list bordered>
              <n-list-item v-for="task in scheduledTasks" :key="task.id">
                <n-thing>
                  <template #header>
                    <n-space align="center" :size="8">
                      <span class="task-name">{{ task.name }}</span>
                      <n-tag :type="task.enabled ? 'success' : 'default'" size="small">
                        {{ task.enabled ? '已启用' : '已禁用' }}
                      </n-tag>
                    </n-space>
                  </template>

                  <template #description>
                    <n-space vertical :size="4">
                      <n-text depth="3">{{ task.description }}</n-text>
                      <n-space :size="16">
                        <span class="task-meta">
                          <n-icon><TimeIcon /></n-icon>
                          {{ task.cron }}
                        </span>
                        <span class="task-meta">
                          <n-icon><CalendarIcon /></n-icon>
                          下次执行: {{ formatTime(task.next_run) }}
                        </span>
                        <span class="task-meta">
                          <n-icon><StatsIcon /></n-icon>
                          已执行: {{ task.execution_count }} 次
                        </span>
                      </n-space>
                    </n-space>
                  </template>

                  <template #action>
                    <n-space>
                      <n-switch
                        v-model:value="task.enabled"
                        size="small"
                        @update:value="handleToggleTask(task)"
                      />
                      <n-button text size="small" @click="handleViewTaskLog(task)">
                        日志
                      </n-button>
                      <n-button text size="small" @click="handleEditTask(task)">
                        编辑
                      </n-button>
                    </n-space>
                  </template>
                </n-thing>
              </n-list-item>
            </n-list>
          </n-card>
        </n-tab-pane>

        <!-- 节假日问候 -->
        <n-tab-pane name="greetings" tab="节假日问候">
          <n-card title="节假日自动问候" size="small" :bordered="false">
            <n-alert type="info" :show-icon="false">
              在节假日前自动向客户发送问候邮件，保持良好的客户关系。
            </n-alert>

            <n-form label-placement="left" label-width="120px" :style="{ marginTop: '16px' }">
              <n-form-item label="启用问候">
                <n-switch v-model:value="greetingSettings.enabled" />
              </n-form-item>

              <n-form-item label="发送时间">
                <n-input-number
                  v-model:value="greetingSettings.days_before"
                  :min="1"
                  :max="7"
                  :style="{ width: '100px' }"
                />
                <span style="margin-left: 8px">天前</span>
              </n-form-item>

              <n-form-item label="目标客户">
                <n-checkbox-group v-model:value="greetingSettings.target_customers">
                  <n-space vertical>
                    <n-checkbox value="cooperating">
                      合作中的客户
                    </n-checkbox>
                    <n-checkbox value="contacting">
                      联系中的客户
                    </n-checkbox>
                    <n-checkbox value="potential">
                      潜在客户
                    </n-checkbox>
                  </n-space>
                </n-checkbox-group>
              </n-form-item>

              <n-form-item label="问候类型">
                <n-checkbox-group v-model:value="greetingSettings.greeting_types">
                  <n-space vertical>
                    <n-checkbox value="public_holiday">
                      公共假期
                    </n-checkbox>
                    <n-checkbox value="religious">
                      宗教节日
                    </n-checkbox>
                    <n-checkbox value="company">
                      公司节日
                    </n-checkbox>
                  </n-space>
                </n-checkbox-group>
              </n-form-item>

              <n-form-item label="使用模板">
                <n-select
                  v-model:value="greetingSettings.template_id"
                  :options="greetingTemplateOptions"
                  placeholder="选择问候邮件模板"
                  :style="{ width: '300px' }"
                />
              </n-form-item>

              <n-form-item :show-label="false">
                <n-space>
                  <n-button type="primary" @click="handleSaveGreetings">
                    保存设置
                  </n-button>
                  <n-button @click="handlePreviewGreeting">
                    预览邮件
                  </n-button>
                </n-space>
              </n-form-item>
            </n-form>
          </n-card>
        </n-tab-pane>

        <!-- 自动回复 -->
        <n-tab-pane name="auto-reply" tab="自动回复">
          <n-card title="自动回复规则" size="small" :bordered="false">
            <template #header-extra>
              <n-button type="primary" size="small" @click="handleCreateReplyRule">
                新建规则
              </n-button>
            </template>

            <n-list bordered>
              <n-list-item v-for="rule in replyRules" :key="rule.id">
                <n-thing>
                  <template #header>
                    <n-space align="center" :size="8">
                      <span class="rule-name">{{ rule.name }}</span>
                      <n-tag :type="rule.enabled ? 'success' : 'default'" size="small">
                        {{ rule.enabled ? '已启用' : '已禁用' }}
                      </n-tag>
                      <n-tag size="small">
                        触发: {{ replyTriggerMap[rule.trigger] }}
                      </n-tag>
                    </n-space>
                  </template>

                  <template #description>
                    <n-space vertical :size="4">
                      <n-text depth="3">{{ rule.description }}</n-text>
                      <n-space :size="16">
                        <span class="rule-meta">
                          使用模板: {{ rule.template_name }}
                        </span>
                        <span class="rule-meta">
                          已发送: {{ rule.sent_count }} 次
                        </span>
                      </n-space>
                    </n-space>
                  </template>

                  <template #action>
                    <n-space>
                      <n-switch
                        v-model:value="rule.enabled"
                        size="small"
                      />
                      <n-button text size="small" @click="handleEditReplyRule(rule)">
                        编辑
                      </n-button>
                      <n-button text size="small" @click="handleTestReplyRule(rule)">
                        测试
                      </n-button>
                    </n-space>
                  </template>
                </n-thing>
              </n-list-item>
            </n-list>
          </n-card>
        </n-tab-pane>

        <!-- 任务执行日志 -->
        <n-tab-pane name="logs" tab="执行日志">
          <n-card title="任务执行日志" size="small" :bordered="false">
            <template #header-extra>
              <n-space>
                <n-select
                  v-model:value="logFilter.task_id"
                  :options="taskOptions"
                  placeholder="筛选任务"
                  clearable
                  :style="{ width: '200px' }"
                />
                <n-select
                  v-model:value="logFilter.status"
                  :options="logStatusOptions"
                  placeholder="筛选状态"
                  clearable
                  :style="{ width: '150px' }"
                />
                <n-button @click="fetchLogs">
                  刷新
                </n-button>
              </n-space>
            </template>

            <n-data-table
              :columns="logColumns"
              :data="logs"
              :loading="logsLoading"
              :pagination="logPagination"
              :bordered="true"
              size="small"
            />
          </n-card>
        </n-tab-pane>
      </n-tabs>
    </n-card>

    <!-- 创建定时任务对话框 -->
    <n-modal v-model:show="showCreateScheduledTask" preset="dialog" title="新建定时任务">
      <n-form label-placement="left" label-width="100px">
        <n-form-item label="任务名称" required>
          <n-input v-model:value="newTask.name" placeholder="任务名称" />
        </n-form-item>
        <n-form-item label="任务类型">
          <n-select v-model:value="newTask.type" :options="taskTypeOptions" />
        </n-form-item>
        <n-form-item label="Cron 表达式">
          <n-input v-model:value="newTask.cron" placeholder="* * * * *" />
          <n-text depth="3" :style="{ fontSize: '12px' }">
            格式: 分 时 日 月 周
          </n-text>
        </n-form-item>
        <n-form-item label="任务描述">
          <n-input v-model:value="newTask.description" type="textarea" />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space>
          <n-button @click="showCreateScheduledTask = false">取消</n-button>
          <n-button type="primary" @click="handleCreateTask">确定</n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, reactive, onMounted, h } from 'vue'
import { useMessage, NButton, NSpace } from 'naive-ui'
import {
  Time as TimeIcon,
  Calendar as CalendarIcon,
  BarChart as StatsIcon,
} from '@vicons/ionicons5'
import type { DataTableColumns } from 'naive-ui'
import {
  getEmailTemplates,
  previewEmailTemplate,
  type EmailTemplate,
} from '@/api/email'

const message = useMessage()
const activeTab = ref('scheduled')

const SCHEDULED_TASKS_KEY = 'client_scheduled_tasks'
const GREETING_SETTINGS_KEY = 'client_greeting_settings'
const REPLY_RULES_KEY = 'client_reply_rules'
const TASK_LOGS_KEY = 'client_task_logs'

// 定时任务
const scheduledTasks = ref<any[]>([])

const showCreateScheduledTask = ref(false)
const newTask = reactive({
  name: '',
  type: 'followup_reminder',
  cron: '',
  description: '',
})

const taskTypeOptions = [
  { label: '跟进提醒', value: 'followup_reminder' },
  { label: '节假日问候', value: 'greeting' },
  { label: '数据同步', value: 'data_sync' },
  { label: '邮件发送', value: 'email_send' },
  { label: '自定义', value: 'custom' },
]

// 节假日问候设置
const greetingSettings = reactive({
  enabled: true,
  days_before: 2,
  target_customers: ['cooperating', 'contacting'],
  greeting_types: ['public_holiday', 'religious'],
  template_id: null,
})

const emailTemplates = ref<EmailTemplate[]>([])
const greetingTemplateOptions = computed(() =>
  emailTemplates.value.map((template) => ({
    label: template.name,
    value: template.id,
  }))
)

// 自动回复规则
const replyRules = ref<any[]>([])

const replyTriggerMap: Record<string, string> = {
  customer_created: '客户创建',
  email_received: '收到邮件',
  status_changed: '状态变更',
  custom: '自定义',
}

// 任务日志
const logs = ref<any[]>([])

const logsLoading = ref(false)
const logFilter = reactive({
  task_id: null,
  status: null,
})

const logStatusOptions = [
  { label: '成功', value: 'success' },
  { label: '失败', value: 'failed' },
  { label: '运行中', value: 'running' },
]

const taskOptions = computed(() =>
  scheduledTasks.value.map((task) => ({
    label: task.name,
    value: task.id,
  }))
)

const logColumns: DataTableColumns<any> = [
  { title: '任务名称', key: 'task_name' },
  {
    title: '状态',
    key: 'status',
    render: (row) => {
      const typeMap: Record<string, any> = {
        success: 'success',
        failed: 'error',
        running: 'warning',
      }
      const textMap: Record<string, string> = {
        success: '成功',
        failed: '失败',
        running: '运行中',
      }
      return h('n-tag', { type: typeMap[row.status] }, { default: () => textMap[row.status] })
    },
  },
  { title: '开始时间', key: 'started_at', render: (row) => formatTime(row.started_at) },
  { title: '耗时(秒)', key: 'duration' },
  { title: '结果', key: 'result' },
]

const logPagination = reactive({
  page: 1,
  pageSize: 20,
  itemCount: 0,
})

function handleToggleTask(task: any) {
  persistScheduledTasks()
  message.success(task.enabled ? '任务已启用' : '任务已禁用')
}

function handleViewTaskLog(task: any) {
  logFilter.task_id = task.id
  activeTab.value = 'logs'
  fetchLogs()
}

function handleEditTask(task: any) {
  Object.assign(newTask, {
    name: task.name,
    type: task.type,
    cron: task.cron,
    description: task.description,
  })
  scheduledTasks.value = scheduledTasks.value.filter((item) => item.id !== task.id)
  persistScheduledTasks()
  showCreateScheduledTask.value = true
}

function handleCreateTask() {
  if (!newTask.name || !newTask.cron) {
    message.warning('请填写任务名称和 Cron 表达式')
    return
  }
  scheduledTasks.value.push({
    id: Date.now().toString(),
    ...newTask,
    enabled: false,
    next_run: null,
    execution_count: 0,
  })
  logs.value.unshift({
    id: Date.now().toString(),
    task_name: newTask.name,
    task_id: scheduledTasks.value[scheduledTasks.value.length - 1].id,
    status: 'success',
    started_at: new Date().toISOString(),
    duration: 0,
    result: '任务配置已保存',
  })
  persistScheduledTasks()
  persistLogs()
  showCreateScheduledTask.value = false
  Object.assign(newTask, {
    name: '',
    type: 'followup_reminder',
    cron: '',
    description: '',
  })
  message.success('任务已创建')
}

function handleSaveGreetings() {
  localStorage.setItem(GREETING_SETTINGS_KEY, JSON.stringify(greetingSettings))
  message.success('节假日问候设置已保存')
}

async function handlePreviewGreeting() {
  if (!greetingSettings.template_id) {
    message.warning('请先选择问候邮件模板')
    return
  }
  try {
    const preview = await previewEmailTemplate(greetingSettings.template_id, {})
    message.info(`${preview.subject}: ${preview.body.replace(/<[^>]+>/g, '').slice(0, 80)}`)
  } catch (error: any) {
    message.error(error.message || '预览邮件失败')
  }
}

function handleCreateReplyRule() {
  replyRules.value.push({
    id: Date.now().toString(),
    name: '新自动回复规则',
    description: '请编辑此规则的触发条件和模板',
    trigger: 'customer_created',
    enabled: false,
    template_name: '-',
    sent_count: 0,
  })
  persistReplyRules()
  message.success('规则已创建')
}

function handleEditReplyRule(rule: any) {
  rule.enabled = !rule.enabled
  persistReplyRules()
  message.success(rule.enabled ? '规则已启用' : '规则已禁用')
}

function handleTestReplyRule(rule: any) {
  logs.value.unshift({
    id: Date.now().toString(),
    task_name: rule.name,
    task_id: rule.id,
    status: 'success',
    started_at: new Date().toISOString(),
    duration: 0,
    result: '规则测试已记录',
  })
  persistLogs()
  message.success(`规则测试已记录: ${rule.name}`)
}

function fetchLogs() {
  logsLoading.value = true
  const savedLogs = localStorage.getItem(TASK_LOGS_KEY)
  logs.value = savedLogs ? JSON.parse(savedLogs) : []
  logPagination.itemCount = logs.value.length
  logsLoading.value = false
  message.success('日志已刷新')
}

function formatTime(time: string | null) {
  if (!time) return '-'
  return new Date(time).toLocaleString('zh-CN')
}

onMounted(() => {
  loadLocalAutomation()
  loadGreetingTemplates()
})

function persistScheduledTasks() {
  localStorage.setItem(SCHEDULED_TASKS_KEY, JSON.stringify(scheduledTasks.value))
}

function persistReplyRules() {
  localStorage.setItem(REPLY_RULES_KEY, JSON.stringify(replyRules.value))
}

function persistLogs() {
  localStorage.setItem(TASK_LOGS_KEY, JSON.stringify(logs.value))
  logPagination.itemCount = logs.value.length
}

function loadLocalAutomation() {
  scheduledTasks.value = JSON.parse(localStorage.getItem(SCHEDULED_TASKS_KEY) || '[]')
  replyRules.value = JSON.parse(localStorage.getItem(REPLY_RULES_KEY) || '[]')
  logs.value = JSON.parse(localStorage.getItem(TASK_LOGS_KEY) || '[]')
  Object.assign(
    greetingSettings,
    JSON.parse(localStorage.getItem(GREETING_SETTINGS_KEY) || '{}')
  )
  logPagination.itemCount = logs.value.length
}

async function loadGreetingTemplates() {
  try {
    emailTemplates.value = await getEmailTemplates({ category: 'greeting' })
    if (!emailTemplates.value.length) {
      emailTemplates.value = await getEmailTemplates()
    }
  } catch (error: any) {
    message.error(error.message || '加载邮件模板失败')
  }
}
</script>

<style scoped>
.automation-page {
  padding: 16px;
}

.task-name,
.rule-name {
  font-weight: 500;
}

.task-meta,
.rule-meta {
  font-size: 13px;
  color: #666;
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
