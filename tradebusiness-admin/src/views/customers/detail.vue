<template>
  <div class="customer-detail-container">
    <el-page-header @back="goBack" title="返回客户列表">
      <template #content>
        <span class="text-large font-600">客户详情</span>
      </template>
    </el-page-header>

    <el-card class="detail-card" v-loading="loading">
      <el-empty v-if="!customer" description="客户不存在" />
      <div v-else>
        <el-descriptions title="公司信息" :column="2" border>
          <el-descriptions-item label="公司名称">{{ customer.company_name }}</el-descriptions-item>
          <el-descriptions-item label="客户状态">{{ customer.status }}</el-descriptions-item>
          <el-descriptions-item label="国家">{{ customer.country }}</el-descriptions-item>
          <el-descriptions-item label="城市">{{ customer.city || '-' }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ customer.email }}</el-descriptions-item>
          <el-descriptions-item label="电话">{{ customer.phone || '-' }}</el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getCustomer } from '@/api/customer'
import type { CustomerResponse } from '@/types/customer'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const customer = ref<CustomerResponse | null>(null)

const goBack = () => {
  router.push({ name: 'Customers' })
}

onMounted(async () => {
  const id = route.params.id as string
  try {
    customer.value = await getCustomer(id)
  } catch (error) {
    ElMessage.error('客户详情加载失败')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.customer-detail-container {
  padding: 20px;
}

.detail-card {
  margin-top: 20px;
}

.text-large {
  font-size: 18px;
}

.font-600 {
  font-weight: 600;
}
</style>
