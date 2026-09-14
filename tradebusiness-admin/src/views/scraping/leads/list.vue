<template>
  <div class="leads-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <h2>采集线索管理</h2>
            <div class="quick-filters">
              <el-button
                size="small"
                :type="filters.status === 'pending' ? 'primary' : 'default'"
                @click="filterByStatus('pending')"
              >
                待审核 ({{ statistics.pending }})
              </el-button>
              <el-button
                size="small"
                :type="filters.status === 'approved' ? 'success' : 'default'"
                @click="filterByStatus('approved')"
              >
                已通过 ({{ statistics.approved }})
              </el-button>
              <el-button
                size="small"
                :type="filters.status === 'imported' ? 'warning' : 'default'"
                @click="filterByStatus('imported')"
              >
                已导入 ({{ statistics.imported }})
              </el-button>
              <el-button
                size="small"
                @click="filterByStatus('')"
              >
                全部 ({{ statistics.total }})
              </el-button>
            </div>
          </div>
          <div class="header-actions">
            <el-button :icon="Download" @click="handleExport">
              导出CSV
            </el-button>
            <el-button
              type="success"
              :disabled="selectedLeads.length === 0"
              @click="handleBulkImport"
            >
              <el-icon><Upload /></el-icon>
              批量导入 ({{ selectedLeads.length }})
            </el-button>
            <el-button
              type="primary"
              :disabled="selectedLeads.length === 0"
              @click="handleBulkApprove(true)"
            >
              <el-icon><Check /></el-icon>
              批量通过
            </el-button>
            <el-button
              type="danger"
              :disabled="selectedLeads.length === 0"
              @click="handleBulkReject"
            >
              <el-icon><Close /></el-icon>
              批量拒绝
            </el-button>
          </div>
        </div>
      </template>

      <!-- 筛选器 -->
      <div class="filters-section">
        <!-- 基础筛选 -->
        <div class="filter-row">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索公司名称、邮箱、电话..."
            clearable
            @change="handleSearch"
            style="width: 250px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>

          <el-select
            v-model="filters.status"
            placeholder="状态筛选"
            clearable
            @change="handleFilterChange"
            style="width: 130px"
          >
            <el-option label="待审核" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已拒绝" value="rejected" />
            <el-option label="已导入" value="imported" />
          </el-select>

          <el-select
            v-model="filters.data_source"
            placeholder="数据源"
            clearable
            @change="handleFilterChange"
            style="width: 130px"
          >
            <el-option label="Google" value="google" />
            <el-option label="商业目录" value="directory" />
            <el-option label="示例" value="example_scraper" />
          </el-select>

          <el-select
            v-model="filters.country_code"
            placeholder="国家"
            clearable
            @change="handleFilterChange"
            style="width: 130px"
          >
            <el-option label="尼日利亚" value="NG" />
            <el-option label="肯尼亚" value="KE" />
            <el-option label="南非" value="ZA" />
            <el-option label="加纳" value="GH" />
            <el-option label="埃及" value="EG" />
          </el-select>

          <el-select
            v-model="filters.business_type"
            placeholder="业务类型"
            clearable
            @change="handleFilterChange"
            style="width: 140px"
          >
            <el-option label="海运" value="Sea Freight" />
            <el-option label="空运" value="Air Freight" />
            <el-option label="陆运" value="Land Freight" />
            <el-option label="多式联运" value="Multimodal" />
            <el-option label="仓储" value="Warehousing" />
          </el-select>

          <el-button type="primary" :icon="Refresh" @click="loadLeads">
            刷新
          </el-button>

          <el-button :icon="Filter" @click="toggleAdvancedFilters">
            高级筛选
          </el-button>
        </div>

        <!-- 高级筛选 -->
        <el-collapse-transition>
          <div v-show="showAdvancedFilters" class="advanced-filters">
            <el-divider content-position="left">高级筛选</el-divider>

            <div class="filter-row">
              <div class="filter-item">
                <label>可信度范围</label>
                <div class="range-inputs">
                  <el-input-number
                    v-model="filters.confidence_min"
                    :min="0"
                    :max="100"
                    placeholder="最低"
                    style="width: 100px"
                  />
                  <span class="range-separator">-</span>
                  <el-input-number
                    v-model="filters.confidence_max"
                    :min="0"
                    :max="100"
                    placeholder="最高"
                    style="width: 100px"
                  />
                </div>
              </div>

              <div class="filter-item">
                <label>采集时间</label>
                <el-date-picker
                  v-model="dateRange"
                  type="daterange"
                  range-separator="至"
                  start-placeholder="开始日期"
                  end-placeholder="结束日期"
                  value-format="YYYY-MM-DD"
                  @change="handleDateRangeChange"
                  style="width: 280px"
                />
              </div>

              <div class="filter-item">
                <label>任务ID</label>
                <el-input
                  v-model="filters.scraping_task_id"
                  placeholder="输入任务ID"
                  clearable
                  style="width: 180px"
                />
              </div>

              <div class="filter-item">
                <label>排序方式</label>
                <el-select
                  v-model="sortBy"
                  @change="handleSortChange"
                  style="width: 150px"
                >
                  <el-option label="采集时间 ↓" value="created_at_desc" />
                  <el-option label="采集时间 ↑" value="created_at_asc" />
                  <el-option label="可信度 ↓" value="confidence_desc" />
                  <el-option label="可信度 ↑" value="confidence_asc" />
                  <el-option label="公司名称" value="company_name" />
                </el-select>
              </div>

              <el-button type="primary" @click="applyAdvancedFilters">
                应用筛选
              </el-button>
              <el-button @click="resetFilters">
                重置
              </el-button>
            </div>
          </div>
        </el-collapse-transition>
      </div>

      <!-- 统计信息 -->
      <div class="statistics-bar">
        <div class="stat-item">
          <el-icon><Document /></el-icon>
          <span class="stat-label">总计:</span>
          <span class="stat-value">{{ statistics.total }}</span>
        </div>
        <div class="stat-item stat-pending">
          <el-icon><Clock /></el-icon>
          <span class="stat-label">待审核:</span>
          <span class="stat-value">{{ statistics.pending }}</span>
        </div>
        <div class="stat-item stat-approved">
          <el-icon><CircleCheck /></el-icon>
          <span class="stat-label">已通过:</span>
          <span class="stat-value">{{ statistics.approved }}</span>
        </div>
        <div class="stat-item stat-rejected">
          <el-icon><CircleClose /></el-icon>
          <span class="stat-label">已拒绝:</span>
          <span class="stat-value">{{ statistics.rejected }}</span>
        </div>
        <div class="stat-item stat-imported">
          <el-icon><CircleCheck /></el-icon>
          <span class="stat-label">已导入:</span>
          <span class="stat-value">{{ statistics.imported }}</span>
        </div>
        <div class="stat-item">
          <el-icon><TrendCharts /></el-icon>
          <span class="stat-label">平均可信度:</span>
          <span class="stat-value">{{ statistics.avg_confidence }}%</span>
        </div>
      </div>

      <!-- 线索列表 -->
      <el-table
        v-loading="loading"
        :data="leadList"
        style="width: 100%; margin-top: 20px"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />

        <el-table-column prop="company_name" label="公司名称" min-width="200">
          <template #default="{ row }">
            <div>
              <div>{{ row.company_name }}</div>
              <div v-if="row.company_name_en" class="text-secondary">
                {{ row.company_name_en }}
              </div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="country" label="国家/地区" width="120">
          <template #default="{ row }">
            <el-tag size="small">{{ row.country_code }}</el-tag>
            <div class="text-secondary">{{ row.city || '-' }}</div>
          </template>
        </el-table-column>

        <el-table-column prop="contact" label="联系方式" min-width="200">
          <template #default="{ row }">
            <div v-if="row.email" class="contact-item">
              <el-icon><Message /></el-icon>
              {{ row.email }}
            </div>
            <div v-if="row.phone" class="contact-item">
              <el-icon><Phone /></el-icon>
              {{ row.phone }}
            </div>
            <div v-if="row.whatsapp" class="contact-item">
              <el-icon><ChatDotRound /></el-icon>
              {{ row.whatsapp }}
            </div>
            <div v-if="row.website" class="contact-item">
              <el-icon><Link /></el-icon>
              <a :href="row.website" target="_blank">{{ row.website }}</a>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="business_type" label="业务类型" width="120">
          <template #default="{ row }">
            {{ row.business_type || '-' }}
          </template>
        </el-table-column>

        <el-table-column prop="data_source" label="数据源" width="100">
          <template #default="{ row }">
            <el-tag size="small" type="info">{{ row.data_source }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="confidence_score" label="可信度" width="80">
          <template #default="{ row }">
            <el-progress
              :percentage="row.confidence_score"
              :color="getConfidenceColor(row.confidence_score)"
              :show-text="false"
              style="width: 50px"
            />
            <span class="confidence-text">{{ row.confidence_score }}</span>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="采集时间" width="150">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'pending'"
              link
              type="success"
              size="small"
              @click="handleApprove(row)"
            >
              <el-icon><Check /></el-icon>
              通过
            </el-button>
            <el-button
              v-if="row.status === 'pending'"
              link
              type="danger"
              size="small"
              @click="handleReject(row)"
            >
              <el-icon><Close /></el-icon>
              拒绝
            </el-button>
            <el-button
              link
              type="primary"
              size="small"
              @click="handleViewDetail(row)"
            >
              <el-icon><View /></el-icon>
              详情
            </el-button>
            <el-button
              v-if="row.status === 'approved'"
              link
              type="primary"
              size="small"
              @click="handleImport(row)"
            >
              <el-icon><Upload /></el-icon>
              导入
            </el-button>
            <el-button
              v-if="row.status === 'rejected'"
              link
              type="danger"
              size="small"
              @click="handleDelete(row)"
            >
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>

      <!-- 空状态 -->
      <el-empty
        v-if="!loading && (!leadList || leadList.length === 0)"
        description="暂无采集线索"
      />
    </el-card>

    <!-- 线索详情对话框 -->
    <el-dialog
      v-model="detailDialogVisible"
      title="线索详情"
      width="900px"
    >
      <el-descriptions :column="2" border>
        <el-descriptions-item label="公司名称" :span="2">
          {{ currentLead.company_name }}
        </el-descriptions-item>
        <el-descriptions-item v-if="currentLead.company_name_en" label="英文名称" :span="2">
          {{ currentLead.company_name_en }}
        </el-descriptions-item>
        <el-descriptions-item label="国家">
          {{ currentLead.country }} ({{ currentLead.country_code }})
        </el-descriptions-item>
        <el-descriptions-item label="城市">
          {{ currentLead.city || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="邮箱">
          {{ currentLead.email || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="电话">
          {{ currentLead.phone || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="WhatsApp">
          {{ currentLead.whatsapp || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="网站">
          <a v-if="currentLead.website" :href="currentLead.website" target="_blank">
            {{ currentLead.website }}
          </a>
          <span v-else>-</span>
        </el-descriptions-item>
        <el-descriptions-item label="业务类型">
          {{ currentLead.business_type || '-' }}
        </el-descriptions-item>
        <el-descriptions-item label="数据源">
          <el-tag size="small">{{ currentLead.data_source }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="可信度">
          <el-progress
            :percentage="currentLead.confidence_score"
            :color="getConfidenceColor(currentLead.confidence_score)"
          />
        </el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentLead.status)">
            {{ getStatusText(currentLead.status) }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item v-if="currentLead.rejection_reason" label="拒绝原因" :span="2">
          {{ currentLead.rejection_reason }}
        </el-descriptions-item>
        <el-descriptions-item v-if="currentLead.description" label="公司描述" :span="2">
          {{ currentLead.description }}
        </el-descriptions-item>
        <el-descriptions-item label="采集时间" :span="2">
          {{ formatDate(currentLead.created_at) }}
        </el-descriptions-item>
        <el-descriptions-item v-if="currentLead.source_url" label="来源URL" :span="2">
          <a :href="currentLead.source_url" target="_blank">{{ currentLead.source_url }}</a>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 原始数据 -->
      <el-divider>原始数据</el-divider>
      <el-card>
        <pre class="raw-data">{{ JSON.stringify(currentLead.raw_data, null, 2) }}</pre>
      </el-card>
    </el-dialog>

    <!-- 拒绝原因对话框 -->
    <el-dialog
      v-model="rejectDialogVisible"
      title="拒绝线索"
      width="500px"
    >
      <el-form>
        <el-form-item label="拒绝原因">
          <el-input
            v-model="rejectionReason"
            type="textarea"
            :rows="4"
            placeholder="请输入拒绝原因（可选）"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="rejectDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmReject">确认拒绝</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRoute } from 'vue-router'
import {
  Check,
  Close,
  View,
  Delete,
  Upload,
  Message,
  Phone,
  ChatDotRound,
  Link,
  Search,
  Refresh,
  Filter,
  Document,
  Clock,
  CircleCheck,
  CircleClose,
  TrendCharts,
  Download,
} from '@element-plus/icons-vue'
import {
  getScrapedLeads,
  approveScrapedLead,
  rejectScrapedLead,
  bulkApproveLeads,
  importLeadsToCustomers,
  deleteScrapedLead,
  checkDuplicate,
  type ScrapedLead,
} from '@/api/leads'

const route = useRoute()

const loading = ref(false)
const leadList = ref<ScrapedLead[]>([])
const selectedLeads = ref<ScrapedLead[]>([])
const detailDialogVisible = ref(false)
const rejectDialogVisible = ref(false)
const rejectionReason = ref('')
const createEmptyLead = (): ScrapedLead => ({
  id: '',
  raw_data: {},
  data_source: '',
  company_name: '',
  country: '',
  country_code: '',
  confidence_score: 0,
  status: 'pending',
  scraping_task_id: '',
  created_at: '',
  updated_at: '',
})

const currentLead = ref<ScrapedLead>(createEmptyLead())

const searchKeyword = ref('')
const showAdvancedFilters = ref(false)
const dateRange = ref<[string, string] | null>(null)
const sortBy = ref('created_at_desc')

const filters = reactive({
  status: '',
  data_source: '',
  country_code: '',
  scraping_task_id: '',
  business_type: '',
  confidence_min: undefined as number | undefined,
  confidence_max: undefined as number | undefined,
  created_after: '',
  created_before: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

// 统计数据
const statistics = computed(() => {
  const total = leadList.value.length
  const pending = leadList.value.filter(l => l.status === 'pending').length
  const approved = leadList.value.filter(l => l.status === 'approved').length
  const rejected = leadList.value.filter(l => l.status === 'rejected').length
  const imported = leadList.value.filter(l => l.status === 'imported').length
  const avgConfidence = total > 0
    ? Math.round(leadList.value.reduce((sum, l) => sum + l.confidence_score, 0) / total)
    : 0

  return {
    total: pagination.total,
    pending,
    approved,
    rejected,
    imported,
    avg_confidence: avgConfidence,
  }
})

// 加载线索列表
const loadLeads = async () => {
  try {
    loading.value = true
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      ...filters,
    }
    const res = await getScrapedLeads(params)
    leadList.value = res?.items || []
    pagination.total = res?.total || 0
  } catch (error) {
    console.error('加载线索列表失败:', error)
    ElMessage.error('加载线索列表失败')
    leadList.value = []
  } finally {
    loading.value = false
  }
}

// 筛选变化
const handleFilterChange = () => {
  pagination.page = 1
  loadLeads()
}

// 搜索功能
const handleSearch = () => {
  pagination.page = 1
  loadLeads()
}

// 切换高级筛选
const toggleAdvancedFilters = () => {
  showAdvancedFilters.value = !showAdvancedFilters.value
}

// 日期范围变化
const handleDateRangeChange = (dates: [string, string] | null) => {
  if (dates && dates.length === 2) {
    filters.created_after = dates[0]
    filters.created_before = dates[1]
  } else {
    filters.created_after = ''
    filters.created_before = ''
  }
}

// 应用高级筛选
const applyAdvancedFilters = () => {
  pagination.page = 1
  loadLeads()
  ElMessage.success('筛选已应用')
}

// 重置筛选
const resetFilters = () => {
  searchKeyword.value = ''
  filters.status = ''
  filters.data_source = ''
  filters.country_code = ''
  filters.scraping_task_id = ''
  filters.business_type = ''
  filters.confidence_min = undefined
  filters.confidence_max = undefined
  filters.created_after = ''
  filters.created_before = ''
  dateRange.value = null
  sortBy.value = 'created_at_desc'
  pagination.page = 1
  loadLeads()
  ElMessage.success('筛选已重置')
}

// 排序变化
const handleSortChange = () => {
  // 在前端排序（如果后端不支持）
  if (leadList.value.length > 0) {
    const sorted = [...leadList.value]
    switch (sortBy.value) {
      case 'created_at_desc':
        sorted.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        break
      case 'created_at_asc':
        sorted.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime())
        break
      case 'confidence_desc':
        sorted.sort((a, b) => b.confidence_score - a.confidence_score)
        break
      case 'confidence_asc':
        sorted.sort((a, b) => a.confidence_score - b.confidence_score)
        break
      case 'company_name':
        sorted.sort((a, b) => a.company_name.localeCompare(b.company_name))
        break
    }
    leadList.value = sorted
  }
}

// 导出数据
const handleExport = () => {
  if (leadList.value.length === 0) {
    ElMessage.warning('没有数据可导出')
    return
  }

  // 准备导出数据
  const exportData: Array<Record<string, string | number>> = leadList.value.map(lead => ({
    '公司名称': lead.company_name,
    '英文名称': lead.company_name_en || '',
    '国家': lead.country,
    '国家代码': lead.country_code,
    '城市': lead.city || '',
    '邮箱': lead.email || '',
    '电话': lead.phone || '',
    'WhatsApp': lead.whatsapp || '',
    '网站': lead.website || '',
    '业务类型': lead.business_type || '',
    '可信度': lead.confidence_score,
    '状态': getStatusText(lead.status),
    '数据源': lead.data_source,
    '采集时间': formatDate(lead.created_at),
  }))

  // 转换为CSV
  const headers = Object.keys(exportData[0])
  const csvContent = [
    headers.join(','),
    ...exportData.map(row => headers.map(header => `"${row[header]}"`).join(',')),
  ].join('\n')

  // 创建下载链接
  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  const url = URL.createObjectURL(blob)
  link.setAttribute('href', url)
  link.setAttribute('download', `scraped_leads_${new Date().toISOString().split('T')[0]}.csv`)
  link.style.visibility = 'hidden'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)

  ElMessage.success(`已导出 ${exportData.length} 条数据`)
}

// 快速筛选状态
const filterByStatus = (status: string) => {
  filters.status = status
  handleFilterChange()
}

// 分页大小变化
const handleSizeChange = () => {
  pagination.page = 1
  loadLeads()
}

// 当前页变化
const handleCurrentChange = () => {
  loadLeads()
}

// 选择变化
const handleSelectionChange = (selection: ScrapedLead[]) => {
  selectedLeads.value = selection
}

// 查看详情
const handleViewDetail = (row: ScrapedLead) => {
  currentLead.value = row
  detailDialogVisible.value = true
}

// 通过单个线索
const handleApprove = async (row: ScrapedLead) => {
  try {
    await approveScrapedLead(row.id)
    ElMessage.success('审核通过')
    loadLeads()
  } catch (error) {
    console.error('审核失败:', error)
    ElMessage.error('审核失败')
  }
}

// 拒绝单个线索
const handleReject = (row: ScrapedLead) => {
  currentLead.value = row
  rejectionReason.value = ''
  rejectDialogVisible.value = true
}

// 确认拒绝
const confirmReject = async () => {
  try {
    await rejectScrapedLead(currentLead.value.id!, rejectionReason.value || undefined)
    ElMessage.success('已拒绝')
    rejectDialogVisible.value = false
    loadLeads()
  } catch (error) {
    console.error('拒绝失败:', error)
    ElMessage.error('拒绝失败')
  }
}

// 批量通过
const handleBulkApprove = async (approved: boolean) => {
  try {
    const leadIds = selectedLeads.value.map(l => l.id)
    await bulkApproveLeads({
      lead_ids: leadIds,
      approved,
    })
    ElMessage.success(`已${approved ? '通过' : '拒绝'} ${selectedLeads.value.length} 条线索`)
    selectedLeads.value = []
    loadLeads()
  } catch (error: any) {
    console.error('批量操作失败:', error)
    ElMessage.error(error?.response?.data?.message || '批量操作失败')
  }
}

// 批量拒绝
const handleBulkReject = () => {
  ElMessageBox.prompt('请输入拒绝原因', '批量拒绝', {
    inputType: 'textarea',
    confirmButtonText: '确认',
    cancelButtonText: '取消',
  }).then(() => {
    handleBulkApprove(false)
  }).catch(() => {
    // 用户取消
  })
}

// 导入单个线索
const handleImport = async (row: ScrapedLead) => {
  try {
    // 先检查是否重复
    const duplicateCheck = await checkDuplicate(row.id)
    if (duplicateCheck.is_duplicate) {
      ElMessageBox.confirm(
        `该线索可能与现有客户重复（相似度: ${duplicateCheck.similarity_score}%），是否继续导入？`,
        '重复检测警告',
        {
          confirmButtonText: '继续导入',
          cancelButtonText: '取消',
          type: 'warning',
        }
      ).then(() => {
        doImport([row.id])
      }).catch(() => {
        // 用户取消
      })
    } else {
      doImport([row.id])
    }
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error('导入失败')
  }
}

// 批量导入
const handleBulkImport = () => {
  const approvedLeads = selectedLeads.value.filter(l => l.status === 'approved')
  if (approvedLeads.length === 0) {
    ElMessage.warning('请选择已通过审核的线索')
    return
  }

  ElMessageBox.confirm(
    `确定要导入 ${approvedLeads.length} 条线索到客户表吗？`,
    '批量导入',
    {
      confirmButtonText: '确认导入',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    doImport(approvedLeads.map(l => l.id))
  }).catch(() => {
    // 用户取消
  })
}

// 执行导入
const doImport = async (leadIds: string[]) => {
  try {
    const result = await importLeadsToCustomers({ lead_ids: leadIds })
    ElMessage.success(
      `导入完成：成功 ${result.imported_count} 条，重复 ${result.duplicate_count} 条`
    )
    selectedLeads.value = []
    loadLeads()
  } catch (error: any) {
    console.error('导入失败:', error)
    if (error?.response?.data?.errors?.length > 0) {
      ElMessage.error(`导入失败：${error.response.data.errors.join(', ')}`)
    } else {
      ElMessage.error('导入失败')
    }
  }
}

// 删除线索
const handleDelete = async (row: ScrapedLead) => {
  try {
    await deleteScrapedLead(row.id)
    ElMessage.success('删除成功')
    loadLeads()
  } catch (error) {
    console.error('删除失败:', error)
    ElMessage.error('删除失败')
  }
}

// 获取状态类型
const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    pending: 'info',
    approved: 'success',
    rejected: 'danger',
    imported: 'warning',
  }
  return map[status] || 'info'
}

// 获取状态文本
const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待审核',
    approved: '已通过',
    rejected: '已拒绝',
    imported: '已导入',
  }
  return map[status] || status
}

// 获取可信度颜色
const getConfidenceColor = (score: number) => {
  if (score >= 80) return '#67c23a'
  if (score >= 60) return '#e6a23c'
  return '#f56c6c'
}

// 格式化日期
const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  // Check for query parameters
  if (route.query.task_id) {
    filters.scraping_task_id = route.query.task_id as string
  }
  if (route.query.status) {
    filters.status = route.query.status as string
  }
  loadLeads()
})
</script>

<style scoped>
.leads-container {
  padding: 20px;
  background: #f5f7fa;
  min-height: calc(100vh - 40px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  flex-wrap: wrap;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.header-left h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.quick-filters {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.header-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

/* 筛选区域 */
.filters-section {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.filter-row {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

.advanced-filters {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.filter-item label {
  font-size: 13px;
  color: #606266;
  font-weight: 500;
}

.range-inputs {
  display: flex;
  align-items: center;
  gap: 8px;
}

.range-separator {
  color: #909399;
  font-weight: 500;
}

/* 统计信息栏 */
.statistics-bar {
  display: flex;
  gap: 20px;
  padding: 16px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #fff;
  font-size: 14px;
}

.stat-item .el-icon {
  font-size: 18px;
  opacity: 0.9;
}

.stat-label {
  opacity: 0.9;
  font-weight: 400;
}

.stat-value {
  font-weight: 700;
  font-size: 18px;
}

.stat-pending {
  padding-left: 20px;
  border-left: 2px solid rgba(255, 255, 255, 0.3);
}

.stat-approved {
  padding-left: 20px;
  border-left: 2px solid rgba(255, 255, 255, 0.3);
}

.stat-rejected {
  padding-left: 20px;
  border-left: 2px solid rgba(255, 255, 255, 0.3);
}

.stat-imported {
  padding-left: 20px;
  border-left: 2px solid rgba(255, 255, 255, 0.3);
}

/* 表格样式 */
.contact-item {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-bottom: 5px;
  font-size: 12px;
  line-height: 1.5;
}

.contact-item:last-child {
  margin-bottom: 0;
}

.contact-item a {
  color: #409eff;
  text-decoration: none;
  word-break: break-all;
}

.contact-item a:hover {
  text-decoration: underline;
}

.text-secondary {
  color: #909399;
  font-size: 12px;
}

.confidence-text {
  margin-left: 5px;
  font-size: 12px;
  font-weight: 600;
}

/* 分页 */
.pagination {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* 原始数据 */
.raw-data {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 6px;
  max-height: 300px;
  overflow-y: auto;
  font-size: 12px;
  line-height: 1.6;
  font-family: 'Courier New', monospace;
  color: #303133;
  border: 1px solid #dcdfe6;
}

.raw-data::-webkit-scrollbar {
  width: 8px;
}

.raw-data::-webkit-scrollbar-thumb {
  background: #dcdfe6;
  border-radius: 4px;
}

.raw-data::-webkit-scrollbar-thumb:hover {
  background: #c0c4cc;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .card-header {
    flex-direction: column;
    align-items: stretch;
  }

  .header-actions {
    justify-content: flex-start;
  }

  .statistics-bar {
    gap: 15px;
  }

  .stat-item {
    font-size: 13px;
  }

  .stat-value {
    font-size: 16px;
  }
}

@media (max-width: 768px) {
  .leads-container {
    padding: 10px;
  }

  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-row > * {
    width: 100% !important;
  }

  .quick-filters {
    flex-direction: column;
  }

  .quick-filters .el-button {
    width: 100%;
  }

  .statistics-bar {
    flex-direction: column;
    gap: 10px;
  }

  .stat-item {
    padding-left: 0 !important;
    border-left: none !important;
  }
}

/* 动画效果 */
.el-table {
  transition: all 0.3s ease;
}

.el-table:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.el-button {
  transition: all 0.3s ease;
}

.el-button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

/* 状态徽章优化 */
.el-tag {
  font-weight: 500;
  padding: 4px 10px;
  border-radius: 12px;
}

/* 进度条优化 */
.el-progress {
  display: inline-block;
}

/* 对话框优化 */
.el-dialog {
  border-radius: 8px;
  overflow: hidden;
}

.el-dialog__header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  padding: 20px;
}

.el-dialog__title {
  color: #fff;
  font-weight: 600;
}

/* 空状态优化 */
.el-empty {
  padding: 40px 20px;
}
</style>
