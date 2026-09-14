<template>
  <div class="unassigned-customers-page">
    <n-card title="未分配客户" :bordered="false">
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

      <!-- 提示信息 -->
      <n-alert type="info" :show-icon="false" class="info-alert">
        这些客户还没有分配给业务员，您可以认领这些客户。分配后，这些客户将显示在"我的客户"列表中。
      </n-alert>

      <!-- 统计卡片 -->
      <n-grid :cols="3" :x-gap="16" class="stats-grid">
        <n-grid-item>
          <n-statistic label="未分配客户" :value="stats.unassigned || 0" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="潜在客户" :value="stats.by_status?.potential || 0" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="本周新增" :value="stats.this_week || 0" />
        </n-grid-item>
      </n-grid>

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
                <span v-if="customer.email" class="customer-email">
                  <n-icon><MailIcon /></n-icon>
                  {{ customer.email }}
                </span>
                <span v-if="customer.phone" class="customer-phone">
                  <n-icon><PhoneIcon /></n-icon>
                  {{ customer.phone }}
                </span>
                <span class="customer-country">
                  <n-icon><LocationIcon /></n-icon>
                  {{ customer.country }}
                </span>
                <span v-if="customer.source" class="customer-source">
                  来源: {{ customer.source }}
                </span>
              </n-space>
            </template>

            <template #action>
              <n-space>
                <n-button
                  type="primary"
                  size="small"
                  :loading="assigning[customer.id]"
                  @click="handleAssign(customer)"
                >
                  认领
                </n-button>
                <n-button text type="primary" size="small" @click="handleViewDetail(customer)">
                  查看详情
                </n-button>
              </n-space>
            </template>
          </n-thing>
        </n-list-item>
      </n-list>

      <!-- 空状态 -->
      <n-empty v-else-if="!loading" description="太棒了！所有客户都已分配">
        <template #extra>
          <n-button size="small" @click="$router.push('/customers/my')">
            查看我的客户
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
      :can-assign="true"
      @assigned="handleAssigned"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useMessage, useDialog } from 'naive-ui'
import {
  Refresh as RefreshIcon,
  Location as LocationIcon,
  CallOutline as PhoneIcon,
  Mail as MailIcon,
} from '@vicons/ionicons5'
import { getUnassignedCustomers, getCustomerStats, assignCustomer } from '@/api/customer'
import type { Customer, CustomerStatus, CustomerStats } from '@/types/customer'
import {
  BusinessTypeMap,
  CustomerStatusMap,
  CustomerStatusTypeMap,
} from '@/types/customer'
import CustomerDetailDrawer from './components/CustomerDetailDrawer.vue'

const message = useMessage()
const dialog = useDialog()

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

const assigning = ref<Record<string, boolean>>({})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const showDetailDrawer = ref(false)
const selectedCustomerId = ref('')

async function fetchCustomers() {
  loading.value = true
  try {
    const response = await getUnassignedCustomers({
      page: pagination.page,
      page_size: pagination.pageSize,
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

function handleAssign(customer: Customer) {
  dialog.info({
    title: '认领客户',
    content: `确定要认领客户 "${customer.company_name}" 吗？认领后该客户将分配给您。`,
    positiveText: '确定',
    negativeText: '取消',
    onPositiveClick: () => doAssign(customer.id),
  })
}

async function doAssign(customerId: string) {
  assigning.value[customerId] = true
  try {
    await assignCustomer(customerId)
    message.success('认领成功！')
    fetchCustomers()
    fetchStats()
  } catch (error: any) {
    message.error(error.message || '认领失败')
  } finally {
    assigning.value[customerId] = false
  }
}

function handleAssigned() {
  showDetailDrawer.value = false
  fetchCustomers()
  fetchStats()
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
.unassigned-customers-page {
  padding: 16px;
}

.info-alert {
  margin-bottom: 16px;
}

.stats-grid {
  margin-bottom: 24px;
}

.customer-email,
.customer-phone,
.customer-country,
.customer-source {
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

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 16px;
}
</style>
