<template>
  <div class="my-customers-page">
    <n-card title="我的客户" :bordered="false">
      <template #header-extra>
        <n-space>
          <n-button type="primary" @click="handleRefresh">
            <template #icon>
              <n-icon><RefreshIcon /></n-icon>
            </template>
            刷新
          </n-button>
        </n-space>
      </template>

      <!-- 统计卡片 -->
      <n-grid :cols="4" :x-gap="16" class="stats-grid">
        <n-grid-item>
          <n-statistic label="我的客户" :value="stats.my_customers || 0" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="联系中" :value="stats.by_status?.contacting || 0" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="合作中" :value="stats.by_status?.cooperating || 0" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="本周新增" :value="stats.this_week || 0" />
        </n-grid-item>
      </n-grid>

      <!-- 搜索筛选 -->
      <n-space class="search-space" vertical>
        <n-input
          v-model:value="searchKeyword"
          placeholder="搜索公司名称或邮箱"
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
          <n-button type="primary" @click="handleSearch">
            搜索
          </n-button>
          <n-button @click="handleReset">
            重置
          </n-button>
        </n-space>
      </n-space>

      <!-- 客户列表 -->
      <n-list v-if="!loading && customers.length > 0" bordered>
        <n-list-item v-for="customer in customers" :key="customer.id">
          <template #prefix>
            <n-avatar
              round
              :src="customer.logo_url"
              :fallback-src="getCompanyInitial(customer.company_name)"
            />
          </template>

          <n-thing :title="customer.company_name">
            <template #description>
              <n-space align="center" :size="8">
                <n-tag :type="getStatusType(customer.status)" size="small">
                  {{ CustomerStatusMap[customer.status] }}
                </n-tag>
                <n-tag v-if="customer.business_type" size="small">
                  {{ BusinessTypeMap[customer.business_type] }}
                </n-tag>
                <span class="customer-email">{{ customer.email || '-' }}</span>
                <span class="customer-country">
                  <n-icon><LocationIcon /></n-icon>
                  {{ customer.country }}
                </span>
              </n-space>
            </template>

            <template #action>
              <n-space>
                <n-button text type="primary" @click="handleViewDetail(customer)">
                  查看详情
                </n-button>
                <n-button text @click="handleContact(customer)">
                  联系
                </n-button>
                <n-dropdown :options="getDropdownOptions(customer)" @select="handleDropdownSelect">
                  <n-button text>
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
      <n-empty v-else-if="!loading" description="暂无客户数据">
        <template #extra>
          <n-button size="small" @click="$router.push('/customers/unassigned')">
            去分配客户
          </n-button>
        </template>
      </n-empty>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-wrapper">
        <n-spin size="large" />
      </div>

      <!-- 分页 -->
      <div v-if="pagination.total > 0" class="pagination-wrapper">
        <n-pagination
          v-model:page="pagination.page"
          v-model:page-size="pagination.pageSize"
          :item-count="pagination.total"
          :page-sizes="[10, 20, 50]"
          show-size-picker
          @update:page="handlePageChange"
          @update:page-size="handlePageSizeChange"
        />
      </div>
    </n-card>

    <!-- 客户详情抽屉 -->
    <customer-detail-drawer
      v-model:show="showDetailDrawer"
      :customer-id="selectedCustomerId"
    />

    <!-- 更新状态对话框 -->
    <n-modal v-model:show="showStatusModal" preset="dialog" title="更新客户状态">
      <n-space vertical>
        <n-select
          v-model:value="newStatus"
          :options="statusOptions"
          label="选择新状态"
        />
      </n-space>
      <template #action>
        <n-space>
          <n-button @click="showStatusModal = false">取消</n-button>
          <n-button type="primary" :loading="statusUpdating" @click="handleStatusUpdate">
            确定
          </n-button>
        </n-space>
      </template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import {
  Refresh as RefreshIcon,
  Search as SearchIcon,
  Location as LocationIcon,
  EllipsisHorizontal as MoreIcon,
} from '@vicons/ionicons5'
import {
  getMyCustomers,
  getCustomerStats,
  updateCustomerStatus,
  unassignCustomer,
} from '@/api/customer'
import type { Customer, CustomerStatus, CustomerStats } from '@/types/customer'
import {
  BusinessTypeMap,
  CustomerStatusMap,
  CustomerStatusTypeMap,
} from '@/types/customer'
import CustomerDetailDrawer from './components/CustomerDetailDrawer.vue'

const router = useRouter()
const message = useMessage()

const loading = ref(false)
const customers = ref<Customer[]>([])
const stats = ref<CustomerStats>({
  total: 0,
  by_status: {},
  by_country: {},
  by_assigned: {},
  my_customers: 0,
  unassigned: 0,
})

const searchKeyword = ref('')
const filterStatus = ref<CustomerStatus | null>(null)

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const showDetailDrawer = ref(false)
const selectedCustomerId = ref('')
const showStatusModal = ref(false)
const newStatus = ref<CustomerStatus>('potential')
const statusUpdating = ref(false)
const updatingCustomerId = ref('')

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
    const response = await getMyCustomers({
      page: pagination.page,
      page_size: pagination.pageSize,
      search: searchKeyword.value || undefined,
      status: filterStatus.value || undefined,
    })
    customers.value = response.items
    pagination.total = response.total
  } catch (error: any) {
    message.error(error.message || '获取客户列表失败')
  } finally {
    loading.value = false
  }
}

async function fetchStats() {
  try {
    const response = await getCustomerStats()
    stats.value = response
  } catch (error: any) {
    console.error('获取统计数据失败', error)
  }
}

function handleSearch() {
  pagination.page = 1
  fetchCustomers()
}

function handleReset() {
  searchKeyword.value = ''
  filterStatus.value = null
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

function handlePageSizeChange(pageSize: number) {
  pagination.pageSize = pageSize
  pagination.page = 1
  fetchCustomers()
}

function handleViewDetail(customer: Customer) {
  selectedCustomerId.value = customer.id
  showDetailDrawer.value = true
}

function handleContact(customer: Customer) {
  if (customer.whatsapp) {
    window.open(`https://wa.me/${customer.whatsapp.replace(/[^0-9]/g, '')}`, '_blank')
  } else if (customer.email) {
    window.open(`mailto:${customer.email}`, '_blank')
  } else {
    message.warning('该客户暂无联系方式')
  }
}

function getDropdownOptions(customer: Customer) {
  return [
    {
      label: '更新状态',
      key: 'update-status',
    },
    {
      label: '发送邮件',
      key: 'send-email',
      disabled: !customer.email,
    },
    {
      type: 'divider',
      key: 'd1',
    },
    {
      label: '取消分配',
      key: 'unassign',
    },
  ]
}

function handleDropdownSelect(key: string, customer: Customer) {
  if (key === 'update-status') {
    updatingCustomerId.value = customer.id
    newStatus.value = customer.status
    showStatusModal.value = true
  } else if (key === 'send-email') {
    router.push(`/emails/compose?customer_id=${customer.id}`)
  } else if (key === 'unassign') {
    unassignCustomer(customer.id)
      .then(() => {
        message.success('已取消分配')
        fetchCustomers()
        fetchStats()
      })
      .catch((error: any) => {
        message.error(error.message || '取消分配失败')
      })
  }
}

async function handleStatusUpdate() {
  statusUpdating.value = true
  try {
    await updateCustomerStatus(updatingCustomerId.value, newStatus.value)
    message.success('状态更新成功')
    showStatusModal.value = false
    fetchCustomers()
    fetchStats()
  } catch (error: any) {
    message.error(error.message || '状态更新失败')
  } finally {
    statusUpdating.value = false
  }
}

function getCompanyInitial(name: string) {
  return name.charAt(0).toUpperCase()
}

function getStatusType(status: CustomerStatus) {
  return CustomerStatusTypeMap[status] || 'default'
}

onMounted(() => {
  fetchCustomers()
  fetchStats()
})
</script>

<style scoped>
.my-customers-page {
  padding: 16px;
}

.stats-grid {
  margin-bottom: 24px;
}

.search-space {
  margin-bottom: 16px;
}

.customer-email {
  font-size: 13px;
  color: #666;
}

.customer-country {
  font-size: 13px;
  color: #999;
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

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}
</style>
