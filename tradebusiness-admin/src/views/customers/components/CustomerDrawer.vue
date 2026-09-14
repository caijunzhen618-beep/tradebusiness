<template>
  <el-drawer
    v-model="drawerVisible"
    title="客户详情"
    size="50%"
    @close="handleClose"
  >
    <el-descriptions v-loading="loading" :column="2" border>
      <el-descriptions-item label="公司名称">
        {{ customer?.company_name }}
      </el-descriptions-item>
      <el-descriptions-item label="英文名称">
        {{ customer?.company_name_en || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="国家">
        {{ customer?.country_code }} {{ customer?.country }}
      </el-descriptions-item>
      <el-descriptions-item label="城市">
        {{ customer?.city || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="邮箱">
        {{ customer?.email || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="电话">
        {{ customer?.phone || '-' }}
      </el-descriptions-item>
      <el-descriptions-item label="业务类型">
        <el-tag v-if="customer?.business_type" type="info">
          {{ businessTypeMap[customer.business_type] }}
        </el-tag>
        <span v-else>-</span>
      </el-descriptions-item>
      <el-descriptions-item label="状态">
        <el-tag :type="getStatusType(customer?.status)">
          {{ getStatusText(customer?.status) }}
        </el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="优先级">
        <el-rate :model-value="Number(customer?.priority || 3)" disabled />
      </el-descriptions-item>
      <el-descriptions-item label="创建时间" :span="2">
        {{ formatDate(customer?.created_at) }}
      </el-descriptions-item>
      <el-descriptions-item label="主要港口" :span="2">
        <el-tag
          v-for="port in customer?.main_ports"
          :key="port"
          style="margin-right: 5px"
        >
          {{ port }}
        </el-tag>
        <span v-if="!customer?.main_ports?.length">-</span>
      </el-descriptions-item>
      <el-descriptions-item label="备注" :span="2">
        {{ customer?.notes || '-' }}
      </el-descriptions-item>
    </el-descriptions>

    <template #footer>
      <el-space>
        <el-button @click="handleClose">关闭</el-button>
        <el-button type="primary" @click="handleEdit">编辑</el-button>
      </el-space>
    </template>
  </el-drawer>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { getCustomer } from '@/api/customer'
import type { Customer } from '@/types/customer'

interface Props {
  modelValue: boolean
  customerId: string
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'edit'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const loading = ref(false)
const customer = ref<Customer | null>(null)

const drawerVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
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

function getStatusText(status?: string) {
  return status ? statusMap[status] || status : '-'
}

function getStatusType(status?: string) {
  return status ? statusTypeMap[status] || 'info' : 'info'
}

async function fetchCustomer() {
  if (!props.customerId) return

  loading.value = true
  try {
    customer.value = await getCustomer(props.customerId)
  } catch (error) {
    console.error('Failed to fetch customer:', error)
  } finally {
    loading.value = false
  }
}

function formatDate(dateStr?: string) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

function handleClose() {
  emit('update:modelValue', false)
}

function handleEdit() {
  emit('edit')
}

// 监听 customerId 变化
// 简化处理，实际应该用 watch
fetchCustomer()
</script>
