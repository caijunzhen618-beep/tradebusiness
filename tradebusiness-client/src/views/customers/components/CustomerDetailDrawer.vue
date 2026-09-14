<template>
  <n-drawer v-model:show="visible" :width="800" placement="right">
    <n-drawer-content :title="customer ? customer.company_name : '客户详情'" :native-scrollbar="false">
      <template #footer>
        <n-space>
          <n-button @click="handleClose">关闭</n-button>
          <n-button v-if="customer && canAssign" type="primary" :loading="assigning" @click="handleAssign">
            认领客户
          </n-button>
          <n-button v-if="customer" type="primary" ghost @click="handleSendEmail">
            发送邮件
          </n-button>
        </n-space>
      </template>

      <div v-if="loading" class="loading-wrapper">
        <n-spin size="large" />
      </div>

      <div v-else-if="customer" class="customer-detail">
        <!-- 基本信息 -->
        <n-card title="基本信息" size="small" class="detail-card">
          <n-descriptions :column="2" bordered>
            <n-descriptions-item label="公司名称">
              {{ customer.company_name }}
            </n-descriptions-item>
            <n-descriptions-item label="英文名称">
              {{ customer.company_name_en || '-' }}
            </n-descriptions-item>
            <n-descriptions-item label="网站">
              <n-a v-if="customer.website" :href="customer.website" target="_blank">
                {{ customer.website }}
              </n-a>
              <span v-else>-</span>
            </n-descriptions-item>
            <n-descriptions-item label="成立年份">
              {{ customer.established_year || '-' }}
            </n-descriptions-item>
            <n-descriptions-item label="公司规模">
              {{ customer.company_size ? `${customer.company_size} 人` : '-' }}
            </n-descriptions-item>
            <n-descriptions-item label="注册资金">
              {{ customer.registered_capital || '-' }}
            </n-descriptions-item>
          </n-descriptions>
        </n-card>

        <!-- 联系信息 -->
        <n-card title="联系信息" size="small" class="detail-card">
          <n-descriptions :column="2" bordered>
            <n-descriptions-item label="国家">
              {{ customer.country }} ({{ customer.country_code }})
            </n-descriptions-item>
            <n-descriptions-item label="城市">
              {{ customer.city || '-' }}
            </n-descriptions-item>
            <n-descriptions-item label="地址">
              {{ customer.address || '-' }}
            </n-descriptions-item>
            <n-descriptions-item label="邮箱">
              <n-space v-if="customer.email" :size="8">
                <span>{{ customer.email }}</span>
                <n-button text type="primary" size="tiny" @click="copyToClipboard(customer.email)">
                  复制
                </n-button>
              </n-space>
              <span v-else>-</span>
            </n-descriptions-item>
            <n-descriptions-item label="电话">
              <n-space v-if="customer.phone" :size="8">
                <span>{{ customer.phone }}</span>
                <n-button text type="primary" size="tiny" @click="copyToClipboard(customer.phone!)">
                  复制
                </n-button>
              </n-space>
              <span v-else>-</span>
            </n-descriptions-item>
            <n-descriptions-item label="WhatsApp">
              <n-space v-if="customer.whatsapp" :size="8">
                <span>{{ customer.whatsapp }}</span>
                <n-button text type="primary" size="tiny" @click="openWhatsApp(customer.whatsapp)">
                  打开
                </n-button>
              </n-space>
              <span v-else>-</span>
            </n-descriptions-item>
          </n-descriptions>
        </n-card>

        <!-- 业务信息 -->
        <n-card title="业务信息" size="small" class="detail-card">
          <n-descriptions :column="2" bordered>
            <n-descriptions-item label="业务类型">
              <n-tag v-if="customer.business_type" size="small">
                {{ BusinessTypeMap[customer.business_type] }}
              </n-tag>
              <span v-else>-</span>
            </n-descriptions-item>
            <n-descriptions-item label="预估年货量">
              {{ customer.estimated_volume ? `${customer.estimated_volume} TEU` : '-' }}
            </n-descriptions-item>
            <n-descriptions-item label="主要港口" :span="2">
              <n-tag v-for="port in customer.main_ports" :key="port" size="small" class="port-tag">
                {{ port }}
              </n-tag>
              <span v-if="!customer.main_ports || customer.main_ports.length === 0">-</span>
            </n-descriptions-item>
            <n-descriptions-item label="航线覆盖" :span="2">
              <n-tag
                v-for="route in customer.route_coverage"
                :key="route"
                size="small"
                class="port-tag"
              >
                {{ route }}
              </n-tag>
              <span v-if="!customer.route_coverage || customer.route_coverage.length === 0">-</span>
            </n-descriptions-item>
            <n-descriptions-item label="货物专长" :span="2">
              <n-tag
                v-for="cargo in customer.cargo_specialization"
                :key="cargo"
                size="small"
                class="port-tag"
              >
                {{ cargo }}
              </n-tag>
              <span v-if="!customer.cargo_specialization || customer.cargo_specialization.length === 0">
                -
              </span>
            </n-descriptions-item>
          </n-descriptions>
        </n-card>

        <!-- 客户管理 -->
        <n-card title="客户管理" size="small" class="detail-card">
          <n-descriptions :column="2" bordered>
            <n-descriptions-item label="状态">
              <n-tag :type="getStatusType(customer.status)">
                {{ CustomerStatusMap[customer.status] }}
              </n-tag>
            </n-descriptions-item>
            <n-descriptions-item label="优先级">
              <n-rate :value="6 - customer.priority" readonly size="small" />
              <span class="priority-text">({{ PriorityMap[customer.priority] }})</span>
            </n-descriptions-item>
            <n-descriptions-item label="分配给">
              {{ customer.assigned_to ? '我' : '未分配' }}
            </n-descriptions-item>
            <n-descriptions-item label="数据来源">
              {{ customer.source || '-' }}
            </n-descriptions-item>
            <n-descriptions-item label="数据可信度">
              <n-progress
                v-if="customer.data_confidence"
                type="line"
                :percentage="customer.data_confidence"
                :height="16"
              />
              <span v-else>-</span>
            </n-descriptions-item>
            <n-descriptions-item label="创建时间">
              {{ formatDate(customer.created_at) }}
            </n-descriptions-item>
            <n-descriptions-item label="标签" :span="2">
              <n-space v-if="customer.tags && customer.tags.length > 0">
                <n-tag v-for="tag in customer.tags" :key="tag" type="info" size="small">
                  {{ tag }}
                </n-tag>
              </n-space>
              <span v-else>-</span>
            </n-descriptions-item>
            <n-descriptions-item label="备注" :span="2">
              {{ customer.notes || '-' }}
            </n-descriptions-item>
          </n-descriptions>
        </n-card>
      </div>

      <n-empty v-else description="未找到客户信息" />
    </n-drawer-content>
  </n-drawer>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { getCustomer, assignCustomer } from '@/api/customer'
import type { Customer, CustomerStatus } from '@/types/customer'
import {
  BusinessTypeMap,
  CustomerStatusMap,
  CustomerStatusTypeMap,
  PriorityMap,
} from '@/types/customer'

interface Props {
  show: boolean
  customerId: string
  canAssign?: boolean
}

interface Emits {
  (e: 'update:show', value: boolean): void
  (e: 'assigned'): void
}

const props = withDefaults(defineProps<Props>(), {
  canAssign: false,
})

const emit = defineEmits<Emits>()
const message = useMessage()
const router = useRouter()

const loading = ref(false)
const customer = ref<Customer | null>(null)
const assigning = ref(false)

const visible = computed({
  get: () => props.show,
  set: (val) => emit('update:show', val),
})

async function fetchCustomer() {
  if (!props.customerId) return

  loading.value = true
  try {
    customer.value = await getCustomer(props.customerId)
  } catch (error: any) {
    message.error(error.message || '获取客户详情失败')
  } finally {
    loading.value = false
  }
}

function handleClose() {
  visible.value = false
}

async function handleAssign() {
  if (!customer.value) return

  assigning.value = true
  try {
    await assignCustomer(customer.value.id)
    message.success('认领成功！')
    emit('assigned')
    handleClose()
  } catch (error: any) {
    message.error(error.message || '认领失败')
  } finally {
    assigning.value = false
  }
}

function handleSendEmail() {
  if (!customer.value) return
  router.push({
    path: '/emails/compose',
    query: { customer_id: customer.value.id },
  })
}

function copyToClipboard(text: string) {
  navigator.clipboard.writeText(text)
  message.success('已复制到剪贴板')
}

function openWhatsApp(phone: string) {
  const cleanPhone = phone.replace(/[^0-9]/g, '')
  window.open(`https://wa.me/${cleanPhone}`, '_blank')
}

function getStatusType(status: CustomerStatus) {
  return CustomerStatusTypeMap[status] || 'default'
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString('zh-CN')
}

watch(
  () => props.show,
  (show) => {
    if (show) {
      fetchCustomer()
    } else {
      customer.value = null
    }
  }
)
</script>

<style scoped>
.customer-detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.detail-card {
  margin-bottom: 0;
}

.port-tag {
  margin-right: 4px;
  margin-bottom: 4px;
}

.priority-text {
  margin-left: 8px;
  font-size: 12px;
  color: #999;
}

.loading-wrapper {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}
</style>
