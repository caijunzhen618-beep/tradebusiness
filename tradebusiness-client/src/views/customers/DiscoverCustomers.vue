<template>
  <div class="discover-customers-page">
    <n-card title="发现客户" :bordered="false">
      <template #header-extra>
        <n-space>
          <n-button type="primary" @click="showSearchModal = true">
            <template #icon>
              <n-icon><SearchIcon /></n-icon>
            </template>
            新建搜索任务
          </n-button>
        </n-space>
      </template>

      <!-- 统计信息 -->
      <n-grid :cols="4" :x-gap="16" class="stats-grid">
        <n-grid-item>
          <n-statistic label="搜索任务" :value="taskStats.total || 0" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="进行中" :value="taskStats.running || 0" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="已完成" :value="taskStats.completed || 0" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="发现客户" :value="taskStats.customers_found || 0" />
        </n-grid-item>
      </n-grid>

      <!-- 搜索任务列表 -->
      <n-collapse v-if="tasks.length > 0" class="tasks-collapse">
        <n-collapse-item v-for="task in tasks" :key="task.id" :name="task.id">
          <template #header>
            <n-space align="center" :size="12">
              <n-badge :type="getTaskStatusType(task.status)" :dot="true" />
              <span class="task-title">{{ task.name }}</span>
              <n-tag :type="getTaskStatusType(task.status)" size="small">
                {{ getTaskStatusText(task.status) }}
              </n-tag>
              <span class="task-time">{{ formatTime(task.created_at) }}</span>
            </n-space>
          </template>

          <div class="task-detail">
            <n-descriptions :column="2" bordered>
              <n-descriptions-item label="国家">
                {{ formatCountries(task.countries) }}
              </n-descriptions-item>
              <n-descriptions-item label="关键词">
                {{ task.keywords.join(', ') }}
              </n-descriptions-item>
              <n-descriptions-item label="已发现">
                {{ task.total_saved || task.total_found || 0 }} 个客户
              </n-descriptions-item>
              <n-descriptions-item label="进度">
                <n-progress
                  type="line"
                  :percentage="getTaskProgress(task)"
                  :height="16"
                />
              </n-descriptions-item>
            </n-descriptions>

            <n-divider />

            <!-- 发现的客户列表 -->
            <!-- 操作按钮 -->
            <n-space :size="8" class="task-actions">
              <n-button
                v-if="task.status === 'running'"
                type="warning"
                size="small"
                @click="handleStopTask(task)"
              >
                停止任务
              </n-button>
            </n-space>
          </div>
        </n-collapse-item>
      </n-collapse>

      <!-- 空状态 -->
      <n-empty v-else description="还没有搜索任务">
        <template #extra>
          <n-button size="small" type="primary" @click="showSearchModal = true">
            创建第一个搜索任务
          </n-button>
        </template>
      </n-empty>
    </n-card>

    <!-- 新建搜索任务对话框 -->
    <n-modal v-model:show="showSearchModal" preset="dialog" title="新建搜索任务">
      <n-form ref="formRef" :model="searchForm" :rules="searchRules" label-placement="left">
        <n-form-item label="国家" path="country">
          <n-select
            v-model:value="searchForm.country"
            :options="countryOptions"
            placeholder="选择目标国家"
          />
        </n-form-item>
        <n-form-item label="关键词" path="keywords">
          <n-dynamic-tags v-model:value="searchForm.keywords" />
        </n-form-item>
        <n-form-item label="业务类型" path="business_type">
          <n-select
            v-model:value="searchForm.business_type"
            :options="businessTypeOptions"
            placeholder="选择业务类型"
          />
        </n-form-item>
        <n-form-item label="最大结果数" path="max_results">
          <n-input-number
            v-model:value="searchForm.max_results"
            :min="10"
            :max="500"
            :style="{ width: '100%' }"
          />
        </n-form-item>
      </n-form>
      <template #action>
        <n-space>
          <n-button @click="showSearchModal = false">取消</n-button>
          <n-button type="primary" :loading="creatingTask" @click="handleCreateSearch">
            开始搜索
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import { Search as SearchIcon } from '@vicons/ionicons5'
import type { FormInst, FormRules } from 'naive-ui'
import {
  cancelScrapingTask,
  createScrapingTask,
  getScrapingTasks,
  startScrapingTask,
  type ScrapingTask,
} from '@/api/scraping'

const message = useMessage()

const tasks = ref<ScrapingTask[]>([])
const taskStats = ref({
  total: 0,
  running: 0,
  completed: 0,
  customers_found: 0,
})

const showSearchModal = ref(false)
const creatingTask = ref(false)
const formRef = ref<FormInst | null>(null)

const searchForm = reactive({
  country: 'NG',
  keywords: ['freight forwarder'],
  business_type: 'sea',
  max_results: 50,
})

const searchRules: FormRules = {
  country: {
    required: true,
    message: '请选择国家',
    trigger: 'change',
  },
  keywords: {
    type: 'array',
    required: true,
    message: '请输入关键词',
    trigger: 'change',
  },
}

const countryOptions = [
  { label: '尼日利亚', value: 'NG' },
  { label: '南非', value: 'ZA' },
  { label: '埃及', value: 'EG' },
  { label: '肯尼亚', value: 'KE' },
  { label: '摩洛哥', value: 'MA' },
  { label: '加纳', value: 'GH' },
  { label: '埃塞俄比亚', value: 'ET' },
  { label: '坦桑尼亚', value: 'TZ' },
]

const businessTypeOptions = [
  { label: '海运', value: 'sea' },
  { label: '空运', value: 'air' },
  { label: '陆运', value: 'land' },
  { label: '多式联运', value: 'multimodal' },
]

async function handleCreateSearch() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    creatingTask.value = true

    const task = await createScrapingTask({
      name: `${getCountryLabel(searchForm.country)} - ${searchForm.keywords[0]}`,
      task_type: 'google',
      keywords: searchForm.keywords,
      countries: [searchForm.country],
      config: {
        business_type: searchForm.business_type,
        max_results: searchForm.max_results,
        max_concurrent: 5,
        delay_min: 2,
        delay_max: 5,
      },
    })
    await startScrapingTask(task.id)

    showSearchModal.value = false
    message.success('搜索任务已创建')
    await loadTasks()
  } catch (error: any) {
    message.error(error.message || '创建任务失败')
  } finally {
    creatingTask.value = false
  }
}

async function handleStopTask(task: ScrapingTask) {
  try {
    await cancelScrapingTask(task.id)
    message.info('任务已取消')
    await loadTasks()
  } catch (error: any) {
    message.error(error.message || '取消任务失败')
  }
}

function updateStats() {
  taskStats.value = {
    total: tasks.value.length,
    running: tasks.value.filter(t => t.status === 'running').length,
    completed: tasks.value.filter(t => t.status === 'completed').length,
    customers_found: tasks.value.reduce((sum, t) => sum + (t.total_saved || t.total_found || 0), 0),
  }
}

function getTaskStatusType(status: string) {
  const typeMap: Record<string, string> = {
    running: 'success',
    completed: 'info',
    cancelled: 'warning',
    failed: 'error',
  }
  return typeMap[status] || 'default'
}

function getTaskStatusText(status: string) {
  const textMap: Record<string, string> = {
    running: '进行中',
    completed: '已完成',
    cancelled: '已取消',
    failed: '失败',
  }
  return textMap[status] || status
}

function formatTime(time: string) {
  return new Date(time).toLocaleString('zh-CN')
}

function getCountryLabel(value: string) {
  return countryOptions.find(option => option.value === value)?.label || value
}

function formatCountries(countries: string[]) {
  return countries.map(getCountryLabel).join(', ')
}

function getTaskProgress(task: ScrapingTask) {
  if (task.status === 'completed') return 100
  if (task.status === 'running') return 50
  if (task.status === 'failed' || task.status === 'cancelled') return 100
  return 0
}

async function loadTasks() {
  try {
    const response = await getScrapingTasks({ limit: 50 })
    tasks.value = response.items
  } catch (error: any) {
    message.error(error.message || '加载搜索任务失败')
  }
  updateStats()
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.discover-customers-page {
  padding: 16px;
}

.stats-grid {
  margin-bottom: 24px;
}

.tasks-collapse {
  margin-top: 16px;
}

.task-title {
  font-weight: 500;
  flex: 1;
}

.task-time {
  font-size: 12px;
  color: #999;
}

.task-detail {
  padding: 16px 0;
}

.found-customers {
  margin-top: 16px;
}

.found-customers h4 {
  margin-bottom: 12px;
  font-weight: 500;
}

.task-actions {
  margin-top: 16px;
}
</style>
