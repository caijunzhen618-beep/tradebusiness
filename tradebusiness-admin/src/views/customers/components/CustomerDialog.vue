<template>
  <el-dialog
    v-model="dialogVisible"
    :title="isEdit ? '编辑客户' : '新建客户'"
    width="800px"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      label-width="120px"
    >
      <el-tabs v-model="activeTab">
        <el-tab-pane label="基本信息" name="basic">
          <el-form-item label="公司名称" prop="company_name">
            <el-input v-model="formData.company_name" placeholder="请输入公司名称" />
          </el-form-item>
          <el-form-item label="英文名称">
            <el-input v-model="formData.company_name_en" placeholder="English name" />
          </el-form-item>
          <el-form-item label="网站">
            <el-input v-model="formData.website" placeholder="https://" />
          </el-form-item>
          <el-form-item label="成立年份">
            <el-input-number v-model="formData.established_year" :min="1800" :max="2100" />
          </el-form-item>
          <el-form-item label="公司规模">
            <el-input-number v-model="formData.company_size" :min="1" placeholder="员工数" />
          </el-form-item>
        </el-tab-pane>

        <el-tab-pane label="联系信息" name="contact">
          <el-form-item label="国家" prop="country">
            <el-select v-model="formData.country" placeholder="选择国家">
              <el-option
                v-for="country in countryOptions"
                :key="country.value"
                :label="country.label"
                :value="country.value"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="城市">
            <el-input v-model="formData.city" placeholder="城市" />
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="formData.email" placeholder="email@example.com" />
          </el-form-item>
          <el-form-item label="电话">
            <el-input v-model="formData.phone" placeholder="+xxx xxx xxx" />
          </el-form-item>
          <el-form-item label="WhatsApp">
            <el-input v-model="formData.whatsapp" />
          </el-form-item>
        </el-tab-pane>

        <el-tab-pane label="业务信息" name="business">
          <el-form-item label="业务类型">
            <el-select v-model="formData.business_type" placeholder="选择类型">
              <el-option label="海运" value="sea" />
              <el-option label="空运" value="air" />
              <el-option label="陆运" value="land" />
              <el-option label="多式联运" value="multimodal" />
            </el-select>
          </el-form-item>
          <el-form-item label="主要港口">
            <el-input v-model="portsText" type="textarea" placeholder="每行一个港口" />
          </el-form-item>
          <el-form-item label="状态">
            <el-select v-model="formData.status">
              <el-option label="潜在客户" value="potential" />
              <el-option label="联系中" value="contacting" />
              <el-option label="合作中" value="cooperating" />
              <el-option label="暂停" value="paused" />
              <el-option label="流失" value="lost" />
            </el-select>
          </el-form-item>
          <el-form-item label="优先级">
            <el-rate v-model="formData.priority" :max="5" />
          </el-form-item>
          <el-form-item label="备注">
            <el-input v-model="formData.notes" type="textarea" :rows="4" />
          </el-form-item>
        </el-tab-pane>
      </el-tabs>
    </el-form>

    <template #footer>
      <el-space>
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          确定
        </el-button>
      </el-space>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, reactive, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { createCustomer, updateCustomer } from '@/api/customer'
import type { Customer, CustomerCreate } from '@/types/customer'

interface Props {
  modelValue: boolean
  customer?: Customer | null
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const formRef = ref<FormInstance>()
const activeTab = ref('basic')
const submitting = ref(false)

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const isEdit = computed(() => !!props.customer?.id)

const formData = reactive<CustomerCreate>({
  company_name: '',
  country_code: 'NG',
  country: 'Nigeria',
  status: 'potential',
  priority: 3,
})

const portsText = computed({
  get: () => formData.main_ports?.join('\n') || '',
  set: (val: string) => {
    formData.main_ports = val.split('\n').filter(p => p.trim())
  },
})

const rules: FormRules = {
  company_name: [
    { required: true, message: '请输入公司名称', trigger: 'blur' },
  ],
  country: [
    { required: true, message: '请选择国家', trigger: 'change' },
  ],
  email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' },
  ],
}

const countryOptions = [
  { label: '尼日利亚', value: 'Nigeria' },
  { label: '南非', value: 'South Africa' },
  { label: '埃及', value: 'Egypt' },
  { label: '肯尼亚', value: 'Kenya' },
  { label: '摩洛哥', value: 'Morocco' },
  { label: '加纳', value: 'Ghana' },
]

watch(
  () => props.customer,
  (customer) => {
    if (customer) {
      Object.assign(formData, customer)
    } else {
      resetForm()
    }
  },
  { immediate: true }
)

function resetForm() {
  Object.assign(formData, {
    company_name: '',
    country_code: 'NG',
    country: 'Nigeria',
    status: 'potential',
    priority: 3,
  })
}

async function handleSubmit() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    submitting.value = true

    if (isEdit.value) {
      await updateCustomer(props.customer!.id!, formData)
      ElMessage.success('更新成功')
    } else {
      await createCustomer(formData)
      ElMessage.success('创建成功')
    }

    emit('success')
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

function handleClose() {
  emit('update:modelValue', false)
  resetForm()
}
</script>
