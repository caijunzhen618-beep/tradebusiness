<template>
  <div class="customers-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>客户管理</h2>
          <el-space>
            <el-button type="primary" :icon="Plus" @click="showCreateDialog = true">
              新建客户
            </el-button>
            <el-button :icon="Upload" @click="showImportDialog = true">
              批量导入
            </el-button>
            <el-button :icon="Refresh" @click="handleRefresh">
              刷新
            </el-button>
          </el-space>
        </div>
      </template>

      <!-- 统计卡片 -->
      <el-row :gutter="16" class="stats-row">
        <el-col :span="6">
          <el-statistic title="总客户数" :value="stats.total" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="潜在客户" :value="stats.by_status?.potential || 0" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="联系中" :value="stats.by_status?.contacting || 0" />
        </el-col>
        <el-col :span="6">
          <el-statistic title="合作中" :value="stats.by_status?.cooperating || 0" />
        </el-col>
      </el-row>

      <!-- 搜索筛选 -->
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="搜索">
          <el-input
            v-model="searchForm.search"
            placeholder="公司名称/邮箱"
            clearable
            @keyup.enter="handleSearch"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </el-form-item>
        <el-form-item label="国家">
          <el-select v-model="searchForm.country" placeholder="选择国家" clearable>
            <el-option
              v-for="country in countryOptions"
              :key="country.value"
              :label="country.label"
              :value="country.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="选择状态" clearable>
            <el-option
              v-for="status in statusOptions"
              :key="status.value"
              :label="status.label"
              :value="status.value"
            />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-space>
            <el-button type="primary" @click="handleSearch">搜索</el-button>
            <el-button @click="handleReset">重置</el-button>
          </el-space>
        </el-form-item>
      </el-form>

      <!-- 客户表格 -->
      <el-table
        v-loading="loading"
        :data="customers"
        style="width: 100%"
        @sort-change="handleSortChange"
      >
        <el-table-column prop="company_name" label="公司名称" width="200" fixed>
          <template #default="{ row }">
            <div class="company-cell">
              <div class="company-name">{{ row.company_name }}</div>
              <div v-if="row.email" class="company-email">{{ row.email }}</div>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="country" label="国家" width="120">
          <template #default="{ row }">
            {{ row.country_code }} {{ row.country }}
          </template>
        </el-table-column>

        <el-table-column prop="business_type" label="业务类型" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.business_type" type="info">
              {{ businessTypeMap[row.business_type] || row.business_type }}
            </el-tag>
            <span v-else>-</span>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="statusTypeMap[row.status]">
              {{ statusMap[row.status] }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="priority" label="优先级" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="priorityTypeMap[row.priority]" size="small">
              P{{ row.priority }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="创建时间" width="120" sortable="custom">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-space>
              <el-button link type="primary" size="small" @click="handleView(row)">
                查看
              </el-button>
              <el-button link type="primary" size="small" @click="handleEdit(row)">
                编辑
              </el-button>
              <el-dropdown @command="(cmd) => handleCommand(cmd, row)">
                <el-button link type="primary" size="small">
                  更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="status">更新状态</el-dropdown-item>
                    <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :page-sizes="[10, 20, 50, 100]"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next, jumper"
        @size-change="handleSizeChange"
        @current-change="handlePageChange"
      />
    </el-card>

    <!-- 创建/编辑对话框 -->
    <customer-dialog
      v-model="showCreateDialog"
      :customer="editingCustomer"
      @success="handleDialogSuccess"
    />

    <!-- 批量导入对话框 -->
    <import-dialog
      v-model="showImportDialog"
      @success="handleImportSuccess"
    />

    <!-- 客户详情抽屉 -->
    <customer-drawer
      v-model="showDetailDrawer"
      :customer-id="selectedCustomerId"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus, Upload, Refresh, Search, ArrowDown,
} from '@element-plus/icons-vue'
import {
  getCustomers,
  getCustomerStats,
  deleteCustomer,
  updateCustomerStatus,
} from '@/api/customer'
import type { Customer } from '@/types/customer'
import CustomerDialog from './components/CustomerDialog.vue'
import ImportDialog from './components/ImportDialog.vue'
import CustomerDrawer from './components/CustomerDrawer.vue'

const loading = ref(false)
const customers = ref<Customer[]>([])
const showCreateDialog = ref(false)
const showImportDialog = ref(false)
const showDetailDrawer = ref(false)
const editingCustomer = ref<Customer | null>(null)
const selectedCustomerId = ref('')

const stats = ref({
  total: 0,
  by_status: {} as Record<string, number>,
  by_country: {} as Record<string, number>,
})

const searchForm = reactive({
  search: '',
  country: '',
  status: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const businessTypeMap: Record<string, string> = {
  sea: '海运',
  air: '空运',
  land: '陆运',
  multimodal: '多式联运',
}

const statusMap: Record<string, string> = {
  potential: '潜在客户',
  contacting: '联系中',
  cooperating: '合作中',
  paused: '暂停',
  lost: '流失',
}

const statusTypeMap: Record<string, any> = {
  potential: '',
  contacting: 'info',
  cooperating: 'success',
  paused: 'warning',
  lost: 'danger',
}

const priorityTypeMap: Record<number, any> = {
  1: 'danger',
  2: 'warning',
  3: '',
  4: 'info',
  5: 'info',
}

const countryOptions = [
  { label: '尼日利亚', value: 'Nigeria' },
  { label: '南非', value: 'South Africa' },
  { label: '埃及', value: 'Egypt' },
  { label: '肯尼亚', value: 'Kenya' },
  { label: '摩洛哥', value: 'Morocco' },
  { label: '加纳', value: 'Ghana' },
]

const statusOptions = [
  { label: '潜在客户', value: 'potential' },
  { label: '联系中', value: 'contacting' },
  { label: '合作中', value: 'cooperating' },
  { label: '暂停', value: 'paused' },
  { label: '流失', value: 'lost' },
]

async function fetchCustomers() {
  loading.value = true
  try {
    const params = {
      ...searchForm,
      page: pagination.page,
      page_size: pagination.pageSize,
    }
    const response = await getCustomers(params)
    customers.value = response.items
    pagination.total = response.total
  } catch (error: any) {
    ElMessage.error(error.message || '获取客户列表失败')
  } finally {
    loading.value = false
  }
}

async function fetchStats() {
  try {
    const response = await getCustomerStats()
    stats.value = response
  } catch (error) {
    ElMessage.error('获取统计数据失败')
  }
}

function handleSearch() {
  pagination.page = 1
  fetchCustomers()
}

function handleReset() {
  searchForm.search = ''
  searchForm.country = ''
  searchForm.status = ''
  pagination.page = 1
  fetchCustomers()
}

function handleRefresh() {
  fetchCustomers()
  fetchStats()
}

function handlePageChange(page: number) {
  pagination.page = page
  fetchCustomers()
}

function handleSizeChange(size: number) {
  pagination.pageSize = size
  pagination.page = 1
  fetchCustomers()
}

function handleSortChange() {
  // 处理排序
  fetchCustomers()
}

function handleView(customer: Customer) {
  selectedCustomerId.value = customer.id
  showDetailDrawer.value = true
}

function handleEdit(customer: Customer) {
  editingCustomer.value = { ...customer }
  showCreateDialog.value = true
}

function handleDialogSuccess() {
  showCreateDialog.value = false
  editingCustomer.value = null
  fetchCustomers()
  fetchStats()
}

function handleImportSuccess() {
  showImportDialog.value = false
  fetchCustomers()
  fetchStats()
}

function handleCommand(command: string, customer: Customer) {
  if (command === 'delete') {
    ElMessageBox.confirm(
      `确定要删除客户 "${customer.company_name}" 吗？`,
      '删除客户',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    ).then(async () => {
      try {
        await deleteCustomer(customer.id)
        ElMessage.success('删除成功')
        fetchCustomers()
        fetchStats()
      } catch (error: any) {
        ElMessage.error(error.message || '删除失败')
      }
    })
  } else if (command === 'status') {
    ElMessageBox.prompt(
      '请输入新状态：potential/contacting/cooperating/paused/lost',
      '更新客户状态',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputValue: customer.status,
        inputPattern: /^(potential|contacting|cooperating|paused|lost)$/,
        inputErrorMessage: '状态必须是 potential、contacting、cooperating、paused 或 lost',
      }
    ).then(async ({ value }) => {
      try {
        await updateCustomerStatus(customer.id, value)
        ElMessage.success('状态已更新')
        fetchCustomers()
        fetchStats()
      } catch (error: any) {
        ElMessage.error(error.message || '状态更新失败')
      }
    })
  }
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchCustomers()
  fetchStats()
})
</script>

<style scoped>
.customers-container {
  padding: 0;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
}

.stats-row {
  margin-bottom: 24px;
}

.search-form {
  margin-bottom: 16px;
}

.company-cell {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.company-name {
  font-weight: 500;
}

.company-email {
  font-size: 12px;
  color: #999;
}
</style>
