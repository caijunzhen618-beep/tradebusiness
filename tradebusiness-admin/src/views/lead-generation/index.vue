<template>
  <div class="leadgen-page"><el-row :gutter="14" class="metric-row"><el-col :span="24"><div class="channel-strip"><span>渠道跟进</span><el-tag v-for="(count, channel) in channels" :key="channel" effect="plain">{{ channel }} {{ count }}</el-tag></div></el-col><el-col :span="6" v-for="metric in metrics" :key="metric.label"><el-card shadow="never"><div class="metric-label">{{ metric.label }}</div><div class="metric-value">{{ metric.value }}</div></el-card></el-col></el-row>
    <el-row :gutter="14" class="breakdown-row">
      <el-col :xs="24" :md="8" v-for="item in breakdowns" :key="item.title">
        <el-card shadow="never" class="breakdown-card">
          <template #header>{{ item.title }}</template>
          <div v-if="Object.keys(item.data).length" class="breakdown-list">
            <div v-for="(count, label) in item.data" :key="label" class="breakdown-item">
              <span>{{ label }}</span><strong>{{ count }}</strong>
            </div>
          </div>
          <el-empty v-else :image-size="48" description="暂无数据" />
        </el-card>
      </el-col>
    </el-row>
    <el-card>
      <template #header>
        <div class="card-header">
          <div>
            <h2>AI 获客</h2>
            <p>创建获客任务，导入官网，生成企业背调和开发信。</p>
          </div>
          <el-button type="primary" @click="taskDialogVisible = true">
            <el-icon><Plus /></el-icon>
            新建获客任务
          </el-button>
        </div>
      </template>

      <el-row :gutter="16">
        <el-col :xs="24" :lg="10">
          <div class="section-title">获客任务</div>
          <el-table v-loading="taskLoading" :data="tasks" height="420">
            <el-table-column prop="name" label="任务" min-width="160" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getTaskStatusType(row.status)">
                  {{ getTaskStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="total_found" label="新增" width="80" />
            <el-table-column label="操作" width="150" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="selectTask(row)">查看</el-button>
                <el-button v-if="row.status !== 'running'" link type="success" @click="handleRunTask(row)">{{ row.status === 'failed' ? '重试' : '运行' }}</el-button>
                <el-button v-else link type="danger" @click="handleCancelTask(row)">取消</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-col>

        <el-col :xs="24" :lg="14">
          <div class="section-title">潜客列表</div>
          <div class="toolbar">
            <el-input
              v-model="leadSearch"
              clearable
              placeholder="搜索公司、官网、国家或行业"
              @keyup.enter="loadLeads"
              @clear="loadLeads"
            />
            <el-button @click="loadLeads">搜索</el-button>
            <el-upload :show-file-list="false" accept=".csv" :http-request="handleCsvImport"><el-button>导入 CSV</el-button></el-upload>
            <el-button @click="leadDialogVisible = true">手动新增</el-button>
          </div>
          <el-table v-loading="leadLoading" :data="leads" height="360">
            <el-table-column prop="company_name" label="公司" min-width="160" />
            <el-table-column prop="country" label="国家" width="100" />
            <el-table-column prop="industry" label="行业" width="120" />
            <el-table-column prop="match_score" label="匹配分" width="90" />
            <el-table-column prop="status" label="状态" width="110">
              <template #default="{ row }">
                <el-tag :type="getLeadStatusType(row.status)">
                  {{ getLeadStatusText(row.status) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="230" fixed="right">
              <template #default="{ row }">
                <el-button link type="primary" @click="openLead(row)">详情</el-button>
                <el-button link type="success" @click="handleGenerateResearch(row)">背调</el-button>
                <el-button link type="warning" @click="handleGenerateCopy(row)">开发信</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-col>
      </el-row>
    </el-card>

    <el-dialog v-model="taskDialogVisible" title="新建获客任务" width="720px">
      <el-form ref="taskFormRef" :model="taskForm" :rules="taskRules" label-width="110px">
        <el-form-item label="任务名称" prop="name">
          <el-input v-model="taskForm.name" placeholder="例如：尼日利亚进口商开发" />
        </el-form-item>
        <el-form-item label="目标国家">
          <el-input v-model="taskForm.target_country" placeholder="例如：Nigeria" />
        </el-form-item>
        <el-form-item label="目标行业">
          <el-input v-model="taskForm.target_industry" placeholder="例如：Importer, logistics, FMCG" />
        </el-form-item>
        <el-form-item label="产品关键词">
          <el-input v-model="keywordInput" placeholder="用逗号分隔，例如 sea freight, customs clearance" />
        </el-form-item>
        <el-form-item label="排除关键词">
          <el-input v-model="excludeInput" placeholder="用逗号分隔" />
        </el-form-item>
        <el-form-item label="客户画像">
          <el-input
            v-model="taskForm.customer_profile"
            type="textarea"
            :rows="3"
            placeholder="描述你要找的客户类型、业务痛点和合作方向"
          />
        </el-form-item>
        <el-form-item label="官网列表" prop="websiteText">
          <el-input
            v-model="websiteText"
            type="textarea"
            :rows="6"
            placeholder="每行一个官网，例如：https://example.com"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="taskDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateTask">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="leadDialogVisible" title="手动新增潜客" width="620px">
      <el-form :model="leadForm" label-width="90px">
        <el-form-item label="公司名称">
          <el-input v-model="leadForm.company_name" />
        </el-form-item>
        <el-form-item label="官网">
          <el-input v-model="leadForm.website" />
        </el-form-item>
        <el-form-item label="国家">
          <el-input v-model="leadForm.country" />
        </el-form-item>
        <el-form-item label="行业">
          <el-input v-model="leadForm.industry" />
        </el-form-item>
        <el-form-item label="简介">
          <el-input v-model="leadForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="leadDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateLead">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="detailVisible" title="潜客详情" width="860px">
      <el-descriptions v-if="currentLead" :column="2" border>
        <el-descriptions-item label="公司">{{ currentLead.company_name }}</el-descriptions-item>
        <el-descriptions-item label="官网">{{ currentLead.website || '-' }}</el-descriptions-item>
        <el-descriptions-item label="国家">{{ currentLead.country || '-' }}</el-descriptions-item>
        <el-descriptions-item label="行业">{{ currentLead.industry || '-' }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ getLeadStatusText(currentLead.status) }}</el-descriptions-item>
        <el-descriptions-item label="匹配分">{{ currentLead.match_score || '-' }}</el-descriptions-item>
      </el-descriptions>

      <el-divider>企业背调</el-divider>
      <el-empty v-if="!research" description="暂无背调报告" />
      <el-descriptions v-else :column="1" border>
        <el-descriptions-item label="摘要">{{ research.summary }}</el-descriptions-item>
        <el-descriptions-item label="商业模式">{{ research.business_model }}</el-descriptions-item>
        <el-descriptions-item label="需求信号">{{ research.buying_signals }}</el-descriptions-item>
        <el-descriptions-item label="痛点">{{ research.pain_points }}</el-descriptions-item>
        <el-descriptions-item label="切入点">{{ research.recommended_angle }}</el-descriptions-item>
      </el-descriptions>

      <el-divider>开发信</el-divider>
      <div class="copy-options">
        <el-select v-model="copyForm.channel" style="width: 130px">
          <el-option label="Email" value="email" />
          <el-option label="WhatsApp" value="whatsapp" />
          <el-option label="LinkedIn" value="linkedin" />
        </el-select>
        <el-select v-model="copyForm.language" style="width: 110px">
          <el-option label="英文" value="en" />
          <el-option label="中文" value="zh" />
        </el-select>
        <el-select v-model="copyForm.agent_id" clearable placeholder="智能体" style="width: 150px" @change="loadTemplates"><el-option v-for="agent in agents" :key="agent.id" :label="agent.name" :value="agent.id" /></el-select><el-select v-model="copyForm.template_id" clearable placeholder="模板" style="width: 150px"><el-option v-for="template in templates" :key="template.id" :label="template.name" :value="template.id" /></el-select><el-button type="primary" @click="currentLead && handleGenerateCopy(currentLead)">生成</el-button>
      </div>
      <el-empty v-if="copies.length === 0" description="暂无开发信" />
      <el-collapse v-else>
        <el-collapse-item v-for="item in copies" :key="item.id" :title="item.subject || item.channel">
          <pre class="copy-content">{{ item.content }}</pre>
          <el-button size="small" @click="copyText(item.content)">复制内容</el-button>
        </el-collapse-item>
      </el-collapse>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
type TagType = 'primary' | 'success' | 'warning' | 'info' | 'danger'
import { Plus } from '@element-plus/icons-vue'
import { getSalesAgents, getAgentTemplates, type SalesAgent } from '@/api/salesAgents'
import {
  getLeadGenerationStats,
  createLead,
  importLeadsCsv,
  createLeadTask,
  generateCompanyResearch,
  generateSalesCopy,
  getCompanyResearch,
  getLeadTask,
  getLeadTasks,
  getLeads,
  getSalesCopies,
  runLeadTask,
  cancelLeadTask,
  type CompanyResearchReport,
  type Lead,
  type LeadSearchTask,
  type SalesCopy,
} from '@/api/leadGeneration'

const channels = ref<Record<string, number>>({})
const router = useRouter()
const breakdowns = ref([
  { title: '目标国家', data: {} as Record<string, number> },
  { title: '目标行业', data: {} as Record<string, number> },
  { title: '潜客状态', data: {} as Record<string, number> },
])
const metrics = ref([{ label: '潜客总数', value: 0 }, { label: '开发信生成', value: 0 }, { label: '跟进任务', value: 0 }, { label: '已完成跟进', value: 0 }])
const taskLoading = ref(false)
const leadLoading = ref(false)
const taskDialogVisible = ref(false)
const leadDialogVisible = ref(false)
const detailVisible = ref(false)
const taskFormRef = ref()
const tasks = ref<LeadSearchTask[]>([])
const leads = ref<Lead[]>([])
const currentTaskId = ref('')
const currentLead = ref<Lead | null>(null)
const research = ref<CompanyResearchReport | null>(null)
const copies = ref<SalesCopy[]>([])
const agents = ref<SalesAgent[]>([])
const templates = ref<{ id: string; name: string }[]>([])
const leadSearch = ref('')
const keywordInput = ref('')
const excludeInput = ref('')
const websiteText = ref('')

const taskForm = reactive({
  name: '',
  target_country: '',
  target_industry: '',
  customer_profile: '',
})

const leadForm = reactive({
  company_name: '',
  website: '',
  country: '',
  industry: '',
  description: '',
})

const copyForm = reactive({
  channel: 'email' as 'email' | 'whatsapp' | 'linkedin',
  language: 'en',
  tone: 'professional',
  agent_id: '',
  template_id: '',
})

const taskRules = {
  name: [{ required: true, message: '请输入任务名称', trigger: 'blur' }],
}

const splitInput = (value: string) =>
  value
    .split(/[\n,，]/)
    .map((item) => item.trim())
    .filter(Boolean)

const loadMetrics = async () => { const stats = await getLeadGenerationStats(); channels.value = stats.channels || {}; breakdowns.value = [{ title: '目标国家', data: stats.countries || {} }, { title: '目标行业', data: stats.industries || {} }, { title: '潜客状态', data: stats.statuses || {} }]; metrics.value = [{ label: '潜客总数', value: stats.leads }, { label: '开发信生成', value: stats.sales_copies }, { label: '跟进任务', value: stats.followups }, { label: '已完成跟进', value: stats.completed_followups }] }

const loadAgents = async () => { agents.value = await getSalesAgents() }

const loadTasks = async () => {
  taskLoading.value = true
  try {
    const res = await getLeadTasks({ limit: 50 })
    tasks.value = res.items || []
  } finally {
    taskLoading.value = false
  }
}

const loadLeads = async () => {
  leadLoading.value = true
  try {
    const res = await getLeads({
      limit: 50,
      task_id: currentTaskId.value || undefined,
      search: leadSearch.value || undefined,
    })
    leads.value = res.items || []
  } finally {
    leadLoading.value = false
  }
}

const handleCreateTask = async () => {
  await taskFormRef.value?.validate()
  await createLeadTask({
    ...taskForm,
    product_keywords: splitInput(keywordInput.value),
    exclude_keywords: splitInput(excludeInput.value),
    website_inputs: splitInput(websiteText.value),
  })
  ElMessage.success('获客任务已创建')
  taskDialogVisible.value = false
  Object.assign(taskForm, {
    name: '',
    target_country: '',
    target_industry: '',
    customer_profile: '',
  })
  keywordInput.value = ''
  excludeInput.value = ''
  websiteText.value = ''
  await loadTasks()
}

const handleRunTask = async (row: LeadSearchTask) => {
  await runLeadTask(row.id)
  ElMessage.success('任务已提交，正在后台处理')
  currentTaskId.value = row.id
  for (let attempt = 0; attempt < 20; attempt += 1) {
    await new Promise((resolve) => window.setTimeout(resolve, 1000))
    const latest = await getLeadTask(row.id)
    const index = tasks.value.findIndex((task) => task.id === row.id)
    if (index >= 0) tasks.value[index] = latest
    if (latest.status === 'completed' || latest.status === 'failed') break
  }
  await loadTasks()
  await loadLeads()
}

const handleCancelTask = async (row: LeadSearchTask) => {
  await cancelLeadTask(row.id)
  ElMessage.success('任务已取消')
  await loadTasks()
}

const selectTask = async (row: LeadSearchTask) => {
  currentTaskId.value = row.id
  await loadLeads()
}

const loadTemplates = async () => { templates.value = copyForm.agent_id ? await getAgentTemplates(copyForm.agent_id) : [] }

const handleCsvImport = async (options: { file: File }) => {
  try {
    const result = await importLeadsCsv(options.file, currentTaskId.value || undefined)
    ElMessage.success(`已导入 ${result.created} 条潜客`)
    await loadLeads()
  } catch (error) {
    console.error("导入 CSV 失败", error)
    ElMessage.error("CSV 导入失败，请检查文件格式")
  }
}
const handleCreateLead = async () => {
  if (!leadForm.company_name) {
    ElMessage.warning('请输入公司名称')
    return
  }
  await createLead({
    ...leadForm,
    task_id: currentTaskId.value || undefined,
    source: 'manual',
  })
  ElMessage.success('潜客已保存')
  leadDialogVisible.value = false
  Object.assign(leadForm, {
    company_name: '',
    website: '',
    country: '',
    industry: '',
    description: '',
  })
  await loadLeads()
}

const openLead = async (row: Lead) => {
  router.push({ name: 'LeadDetail', params: { id: row.id } })
  currentLead.value = row
  detailVisible.value = true
  research.value = await getCompanyResearch(row.id)
  copies.value = await getSalesCopies(row.id)
}

const handleGenerateResearch = async (row: Lead) => {
  research.value = await generateCompanyResearch(row.id)
  ElMessage.success('企业背调已生成')
  await loadLeads()
  if (!detailVisible.value) {
    await openLead(row)
  }
}

const handleGenerateCopy = async (row: Lead) => {
  await generateSalesCopy(row.id, copyForm)
  ElMessage.success('开发信已生成')
  copies.value = await getSalesCopies(row.id)
  await loadLeads()
  if (!detailVisible.value) {
    await openLead(row)
  }
}

const copyText = async (value: string) => {
  await navigator.clipboard.writeText(value)
  ElMessage.success('已复制')
}

const getTaskStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待运行',
    running: '运行中',
    completed: '已完成',
    failed: '失败',
    cancelled: '已取消',
  }
  return map[status] || status
}

const getTaskStatusType = (status: string): TagType => {
  const map: Record<string, TagType> = {
    pending: 'info',
    running: 'warning',
    completed: 'success',
    failed: 'danger',
    cancelled: 'info',
  }
  return map[status] || 'info'
}

const getLeadStatusText = (status: string) => {
  const map: Record<string, string> = {
    new: '新线索',
    researched: '已背调',
    copy_generated: '已生成话术',
    contacted: '已联系',
    replied: '已回复',
    invalid: '无效',
  }
  return map[status] || status
}

const getLeadStatusType = (status: string): TagType => {
  const map: Record<string, TagType> = {
    new: 'info',
    researched: 'success',
    copy_generated: 'warning',
    contacted: 'primary',
    replied: 'success',
    invalid: 'danger',
  }
  return map[status] || 'info'
}

onMounted(async () => {
  await loadMetrics()
  await loadAgents()
  await loadTasks()
  await loadLeads()
})
</script>

<style scoped>
.channel-strip{display:flex;align-items:center;gap:10px;margin-bottom:14px;color:#667085;font-size:13px}.metric-row{margin-bottom:18px}.metric-label{color:#667085;font-size:13px}.metric-value{margin-top:8px;font-size:28px;font-weight:700;color:#101828}.leadgen-page {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.card-header h2 {
  margin: 0;
  font-size: 22px;
}

.card-header p {
  margin: 6px 0 0;
  color: #667085;
  font-size: 13px;
}

.section-title {
  margin-bottom: 12px;
  font-weight: 600;
}

.toolbar {
  display: grid;
  grid-template-columns: minmax(220px, 1fr) auto auto;
  gap: 8px;
  margin-bottom: 12px;
}

.copy-options {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.copy-content {
  margin: 0 0 12px;
  padding: 12px;
  white-space: pre-wrap;
  background: #f6f8fa;
  border: 1px solid #ebeef5;
  border-radius: 6px;
  line-height: 1.6;
}

.breakdown-row {
  margin: 14px 0;
}

.breakdown-card {
  min-height: 150px;
}

.breakdown-list {
  display: grid;
  gap: 8px;
}

.breakdown-item {
  display: flex;
  justify-content: space-between;
  color: #606266;
}

.breakdown-item strong {
  color: #303133;
}
</style>








