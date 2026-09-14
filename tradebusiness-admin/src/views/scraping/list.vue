<template>
  <div class="scraping-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>数据采集管理</h2>
          <div class="header-actions">
            <el-button @click="handleViewLeads">
              <el-icon><Document /></el-icon>
              查看采集线索
            </el-button>
            <el-button type="primary" @click="handleCreateTask">
              <el-icon><Plus /></el-icon>
              新建采集任务
            </el-button>
          </div>
        </div>
      </template>

      <!-- 数据源选择 -->
      <el-collapse v-model="activeSources" style="margin-bottom: 20px">
        <el-collapse-item title="可用数据源" name="sources">
          <el-checkbox-group v-model="selectedSources">
            <el-checkbox
              v-for="source in availableSources"
              :key="source.value"
              :value="source.value"
            >
              {{ source.label }}
            </el-checkbox>
          </el-checkbox-group>
          <div style="margin-top: 10px">
            <el-button size="small" @click="selectAllSources">全选</el-button>
            <el-button size="small" @click="clearSources">清空</el-button>
          </div>
        </el-collapse-item>
      </el-collapse>

      <!-- 任务列表 -->
      <el-table
        v-loading="loading"
        :data="taskList"
        style="width: 100%"
      >
        <el-table-column prop="name" label="任务名称" min-width="200" />
        <el-table-column prop="task_type" label="任务类型" width="120">
          <template #default="{ row }">
            <el-tag>{{ getTaskTypeText(row.task_type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="total_found" label="发现数据" width="100" />
        <el-table-column prop="total_saved" label="已保存" width="100">
          <template #default="{ row }">
            <el-button
              v-if="row.total_saved > 0"
              link
              type="primary"
              @click="handleViewTaskLeadsDirect(row)"
            >
              {{ row.total_saved }}
            </el-button>
            <span v-else>{{ row.total_saved || 0 }}</span>
          </template>
        </el-table-column>
        <el-table-column label="执行信息" min-width="220">
          <template #default="{ row }">
            <el-text v-if="row.status_message" truncated>
              {{ row.status_message }}
            </el-text>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="来源地址" min-width="180">
          <template #default="{ row }">
            <el-tooltip
              v-if="row.source_urls?.length"
              effect="dark"
              placement="top"
            >
              <template #content>
                <div class="source-tooltip">
                  <div v-for="url in row.source_urls" :key="url">{{ url }}</div>
                </div>
              </template>
              <el-tag size="small" type="info">{{ row.source_urls.length }} 个来源</el-tag>
            </el-tooltip>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column label="失败原因" min-width="180">
          <template #default="{ row }">
            <el-text v-if="row.error_message" type="danger" truncated>
              {{ row.error_message }}
            </el-text>
            <span v-else>-</span>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="150">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              link
              type="primary"
              size="small"
              @click="handleStart(row)"
            >
              启动
            </el-button>
            <el-button
              v-if="row.status === 'running'"
              link
              type="warning"
              size="small"
              @click="handleCancel(row)"
            >
              取消
            </el-button>
            <el-button
              link
              type="primary"
              size="small"
              @click="handleView(row)"
            >
              查看
            </el-button>
            <el-popconfirm
              title="确定删除此任务吗？"
              @confirm="handleDelete(row)"
            >
              <template #reference>
                <el-button link type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 空状态 -->
      <el-empty
        v-if="!loading && (!taskList || taskList.length === 0)"
        description="暂无采集任务"
      />
    </el-card>

    <!-- 新建任务对话框 -->
    <el-dialog
      v-model="dialogVisible"
      title="新建采集任务"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="formData.name" placeholder="请输入任务名称" />
        </el-form-item>
        <el-form-item label="任务类型" prop="task_type">
          <el-select v-model="formData.task_type" placeholder="请选择任务类型">
            <el-option
              v-for="source in availableSources"
              :key="source.value"
              :label="source.label"
              :value="source.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="关键词" prop="keywords">
          <el-input
            v-model="keywordInput"
            type="textarea"
            :rows="3"
            placeholder="请输入关键词，用逗号分隔"
          />
        </el-form-item>
        <el-form-item label="目标国家" prop="countries">
          <el-select v-model="formData.countries" multiple placeholder="请选择国家">
            <el-option label="尼日利亚" value="NG" />
            <el-option label="肯尼亚" value="KE" />
            <el-option label="南非" value="ZA" />
            <el-option label="加纳" value="GH" />
            <el-option label="埃及" value="EG" />
          </el-select>
        </el-form-item>
        <el-form-item label="来源地址">
          <el-input
            v-model="sourceUrlInput"
            type="textarea"
            :rows="3"
            placeholder="请输入采集数据来源地址，每行一个。例如：https://example.com/directory"
          />
        </el-form-item>
        <el-form-item label="最大并发数">
          <el-input-number v-model="formData.config.max_concurrent" :min="1" :max="20" />
        </el-form-item>
        <el-form-item label="延迟范围">
          <el-input-number v-model="formData.config.delay_min" :min="1" :max="10" />
          <span style="margin: 0 10px">-</span>
          <el-input-number v-model="formData.config.delay_max" :min="1" :max="10" />
          <span style="margin-left: 10px">秒</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">创建</el-button>
      </template>
    </el-dialog>

    <!-- 任务详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="任务详情"
      width="800px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="任务名称">
          {{ currentTask.name }}
        </el-descriptions-item>
        <el-descriptions-item label="任务类型">
          {{ getTaskTypeText(currentTask.task_type) }}
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentTask.status)">
            {{ getStatusText(currentTask.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="发现数据">
          {{ currentTask.total_found || 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="已保存">
          {{ currentTask.total_saved || 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="执行进度">
          {{ currentTask.progress_current || 0 }} / {{ currentTask.progress_total || 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="创建时间">
          {{ formatDate(currentTask.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item label="当前信息" :span="2">
          {{ currentTask.status_message || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="来源地址" :span="2">
          <div v-if="currentTask.source_urls?.length" class="source-list">
            <a
              v-for="url in currentTask.source_urls"
              :key="url"
              :href="url"
              target="_blank"
              rel="noopener noreferrer"
            >
              {{ url }}
            </a>
          </div>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item
          v-if="currentTask.error_message"
          label="失败原因"
          :span="2"
        >
          <el-alert
            :title="currentTask.error_message"
            type="error"
            :closable="false"
            show-icon
          />
        </el-descriptions-item>
      </el-descriptions>

      <!-- 进度条 -->
      <div v-if="currentTask.status === 'running'" style="margin-top: 20px">
        <el-progress
          :percentage="getProgress(currentTask)"
          :status="currentTask.total_saved > 0 ? 'success' : undefined"
        />
      </div>

      <div v-if="currentTask.last_run_summary" class="run-summary">
        <h3>执行摘要</h3>
        <el-alert
          v-for="item in currentTask.last_run_summary.diagnostics || []"
          :key="item"
          :title="item"
          type="warning"
          :closable="false"
          show-icon
        />
        <el-table
          v-if="currentTask.last_run_summary.source_checks?.length"
          :data="currentTask.last_run_summary.source_checks"
          size="small"
          border
        >
          <el-table-column label="来源地址" min-width="260">
            <template #default="{ row }">
              <a :href="row.url" target="_blank" rel="noopener noreferrer">{{ row.url }}</a>
            </template>
          </el-table-column>
          <el-table-column label="结果" width="90">
            <template #default="{ row }">
              <el-tag :type="row.ok ? 'success' : 'danger'">
                {{ row.ok ? '成功' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="reason" label="说明" min-width="180" />
          <el-table-column label="提取字段" min-width="160">
            <template #default="{ row }">
              <el-tag
                v-for="field in row.found_fields || []"
                :key="field"
                size="small"
                style="margin-right: 4px"
              >
                {{ field }}
              </el-tag>
              <span v-if="!row.found_fields?.length">-</span>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <div v-if="currentTask.execution_log?.length" class="execution-log">
        <h3>执行日志</h3>
        <el-timeline>
          <el-timeline-item
            v-for="item in currentTask.execution_log"
            :key="`${item.time}-${item.message}`"
            :timestamp="formatDate(item.time)"
            :type="getLogType(item.level)"
          >
            {{ item.message }}
          </el-timeline-item>
        </el-timeline>
      </div>

      <!-- 查看采集线索按钮 -->
      <div v-if="currentTask.total_saved > 0" style="margin-top: 20px; text-align: center">
        <el-button type="primary" @click="handleViewTaskLeads">
          <el-icon><Document /></el-icon>
          查看采集到的线索 ({{ currentTask.total_saved }})
        </el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import { Plus, Document } from '@element-plus/icons-vue'
import {
  getScrapingTasks,
  createScrapingTask,
  startScrapingTask,
  cancelScrapingTask,
  deleteScrapingTask,
  type ScrapingTask,
  type ScrapingTaskCreate,
} from '@/api/scraping'

const router = useRouter()

const loading = ref(false)
const taskList = ref<ScrapingTask[]>([])
const dialogVisible = ref(false)
const detailDialogVisible = ref(false)
const formRef = ref()
const keywordInput = ref('')
const sourceUrlInput = ref('')
const activeSources = ref(['sources'])
const selectedSources = ref<string[]>([])
const availableSources = [
  { label: 'Google 搜索', value: 'google' },
  { label: 'Kompass 商业目录', value: 'kompass' },
  { label: 'Yellow Pages', value: 'yellow_pages' },
  { label: '港口管理局', value: 'port_authorities' },
]

const createEmptyTask = (): ScrapingTask => ({
  id: '',
  name: '',
  task_type: 'google',
  status: 'pending',
  config: {
    max_concurrent: 5,
    delay_min: 2,
    delay_max: 5,
  },
  keywords: [],
  countries: [],
  source_urls: [],
  progress_current: 0,
  progress_total: 0,
  total_found: 0,
  total_saved: 0,
  status_message: '',
  last_run_summary: undefined,
  execution_log: [],
  created_at: '',
  updated_at: '',
})

const currentTask = ref<ScrapingTask>(createEmptyTask())

const formData = reactive({
  name: '',
  task_type: 'google',
  keywords: [] as string[],
  countries: [] as string[],
  source_urls: [] as string[],
  config: {
    max_concurrent: 5,
    delay_min: 2,
    delay_max: 5,
    sources: [] as string[],
    source_urls: [] as string[],
  },
})

const formRules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
  task_type: [{ required: true, message: '请选择任务类型', trigger: 'change' }],
}

// 加载任务列表
const loadTasks = async () => {
  try {
    loading.value = true
    const res = await getScrapingTasks()
    taskList.value = res?.items || []
    if (detailDialogVisible.value && currentTask.value.id) {
      const latest = taskList.value.find(task => task.id === currentTask.value.id)
      if (latest) {
        currentTask.value = latest
      }
    }
  } catch (error) {
    console.error('加载任务列表失败:', error)
    ElMessage.error('加载任务列表失败')
    taskList.value = []
  } finally {
    loading.value = false
  }
}

// 全选数据源
const selectAllSources = () => {
  selectedSources.value = availableSources.map(source => source.value)
}

// 清空数据源
const clearSources = () => {
  selectedSources.value = []
}

// 新建任务
const handleCreateTask = () => {
  dialogVisible.value = true
}

// 查看采集线索
const handleViewLeads = () => {
  router.push('/scraping/leads')
}

// 查看任务的采集线索
const handleViewTaskLeads = () => {
  router.push({
    path: '/scraping/leads',
    query: { task_id: currentTask.value.id },
  })
}

// 直接查看任务的采集线索（从列表）
const handleViewTaskLeadsDirect = (row: ScrapingTask) => {
  router.push({
    path: '/scraping/leads',
    query: { task_id: row.id },
  })
}

// 启动任务
const handleStart = async (row: ScrapingTask) => {
  try {
    await startScrapingTask(row.id)
    ElMessage.success('任务已启动')
    await loadTasks()
    startAutoRefresh()
  } catch (error) {
    console.error('启动失败:', error)
    ElMessage.error('启动失败')
  }
}

// 取消任务
const handleCancel = async (row: ScrapingTask) => {
  try {
    await cancelScrapingTask(row.id)
    ElMessage.success('任务已取消')
    loadTasks()
  } catch (error) {
    console.error('取消失败:', error)
    ElMessage.error('取消失败')
  }
}

// 查看详情
const handleView = (row: ScrapingTask) => {
  currentTask.value = row
  detailDialogVisible.value = true
  if (row.status === 'running') {
    startAutoRefresh()
  }
}

// 删除任务
const handleDelete = async (row: ScrapingTask) => {
  try {
    await deleteScrapingTask(row.id)
    ElMessage.success('删除成功')
    loadTasks()
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error('删除失败')
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()

    // 处理关键词
    const keywords = keywordInput.value
      .split(',')
      .map(k => k.trim())
      .filter(k => k)
    const sourceUrls = sourceUrlInput.value
      .split(/[\n,，]/)
      .map(url => url.trim())
      .filter(url => url)

    if (!keywords || keywords.length === 0) {
      ElMessage.warning('请输入至少一个关键词')
      return
    }

    formData.keywords = keywords
    formData.source_urls = sourceUrls
    formData.config.sources = [formData.task_type]
    formData.config.source_urls = sourceUrls

    // 提交抓取任务
    await createScrapingTask(formData as ScrapingTaskCreate)
    ElMessage.success('任务创建成功')
    dialogVisible.value = false
    loadTasks()
  } catch (error: any) {
    console.error('创建任务失败:', error)
    if (error?.response?.data?.message) {
      ElMessage.error(error.response.data.message)
    } else {
      ElMessage.error('创建任务失败')
    }
  }
}

// 对话框关闭
const handleDialogClose = () => {
  formRef.value?.resetFields()
  keywordInput.value = ''
  sourceUrlInput.value = ''
}

// 获取任务类型文本
const getTaskTypeText = (type: string) => {
  const map: Record<string, string> = {
    google: 'Google 搜索',
    kompass: 'Kompass 商业目录',
    yellow_pages: 'Yellow Pages',
    port_authorities: '港口管理局',
    directory: '商业目录',
    specific_site: '特定网站',
  }
  return map[type] || type
}

// 获取状态类型
const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info',
  }
  return map[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待处理',
    running: '运行中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消',
  }
  return map[status] || status
}

// 获取进度
const getProgress = (task: Partial<ScrapingTask>) => {
  if (task.progress_total && task.progress_total > 0) {
    return Math.min(100, Math.floor(((task.progress_current || 0) / task.progress_total) * 100))
  }
  if (!task.total_found || task.total_found === 0) return 0
  return Math.floor((task.total_saved || 0) / task.total_found * 100)
}

const getLogType = (level: string) => {
  const map: Record<string, any> = {
    success: 'success',
    warning: 'warning',
    error: 'danger',
    info: 'primary',
  }
  return map[level] || 'primary'
}

// 格式化日期
const formatDate = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

let refreshTimer: number | undefined

const startAutoRefresh = () => {
  if (refreshTimer) return
  refreshTimer = window.setInterval(async () => {
    await loadTasks()
    const hasRunning = taskList.value.some(task => task.status === 'running')
    if (!hasRunning) {
      stopAutoRefresh()
    }
  }, 3000)
}

const stopAutoRefresh = () => {
  if (!refreshTimer) return
  window.clearInterval(refreshTimer)
  refreshTimer = undefined
}

onMounted(() => {
  loadTasks()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.scraping-container {
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

.source-tooltip {
  max-width: 420px;
  word-break: break-all;
}

.source-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  word-break: break-all;
}

.run-summary,
.execution-log {
  margin-top: 20px;
}

.run-summary h3,
.execution-log h3 {
  margin: 0 0 12px;
  font-size: 15px;
}

.run-summary .el-alert {
  margin-bottom: 10px;
}
</style>
