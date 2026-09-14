<template>
  <div class="cooperation-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>合作管理</h2>
          <el-button :icon="Refresh" @click="fetchCooperatingCustomers">刷新</el-button>
        </div>
      </template>

      <el-table v-loading="loading" :data="customers" style="width: 100%">
        <el-table-column prop="company_name" label="客户名称" min-width="220" />
        <el-table-column prop="country" label="国家" width="160">
          <template #default="{ row }">
            {{ row.country_code }} {{ row.country }}
          </template>
        </el-table-column>
        <el-table-column prop="business_type" label="业务类型" width="120">
          <template #default="{ row }">
            {{ row.business_type || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="cooperation_date" label="合作日期" width="140">
          <template #default="{ row }">
            {{ row.cooperation_date ? formatDate(row.cooperation_date) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="200">
          <template #default="{ row }">
            {{ row.email || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="phone" label="电话" width="160">
          <template #default="{ row }">
            {{ row.phone || '-' }}
          </template>
        </el-table-column>
      </el-table>

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
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { getCustomers } from '@/api/customer'

const loading = ref(false)
const customers = ref<any[]>([])

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

async function fetchCooperatingCustomers() {
  loading.value = true
  try {
    const response = await getCustomers({
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      status: 'cooperating',
    })
    customers.value = response.items || []
    pagination.total = response.total || 0
  } catch (error: any) {
    ElMessage.error(error.message || '加载合作客户失败')
  } finally {
    loading.value = false
  }
}

function handleSizeChange(size: number) {
  pagination.pageSize = size
  pagination.page = 1
  fetchCooperatingCustomers()
}

function handlePageChange(page: number) {
  pagination.page = page
  fetchCooperatingCustomers()
}

function formatDate(date: string) {
  return new Date(date).toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchCooperatingCustomers()
})
</script>

<style scoped>
.cooperation-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
}
</style>
