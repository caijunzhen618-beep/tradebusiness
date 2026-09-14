<template>
  <el-dialog
    v-model="dialogVisible"
    title="批量导入客户"
    width="600px"
    @close="handleClose"
  >
    <el-alert
      title="支持 CSV 文件导入，Excel 文件请先另存为 CSV"
      type="info"
      :closable="false"
      style="margin-bottom: 20px"
    />

    <el-upload
      ref="uploadRef"
      :auto-upload="false"
      :limit="1"
      accept=".csv"
      @change="handleFileChange"
    >
      <el-button type="primary">选择文件</el-button>
      <template #tip>
        <div class="el-upload__tip">
          只能上传 csv 文件，且不超过 10MB。必填列：company_name、country_code、country
        </div>
      </template>
    </el-upload>

    <template #footer>
      <el-space>
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="importing" @click="handleImport">
          开始导入
        </el-button>
      </el-space>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import type { UploadFile } from 'element-plus'
import { batchImportCustomers } from '@/api/customer'

interface CustomerImportRow {
  company_name: string
  country_code: string
  country: string
  company_name_en?: string
  city?: string
  address?: string
  phone?: string
  email?: string
  website?: string
  business_type?: string
  status?: string
  priority?: number
  source?: string
  notes?: string
}

interface Props {
  modelValue: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const uploadRef = ref()
const importing = ref(false)
const selectedFile = ref<File | null>(null)

const dialogVisible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

function handleFileChange(file: UploadFile) {
  if (file.raw) {
    selectedFile.value = file.raw
  }
}

async function handleImport() {
  if (!selectedFile.value) {
    ElMessage.warning('请先选择文件')
    return
  }

  importing.value = true
  try {
    const customers = await parseCsvFile(selectedFile.value)
    const result = await batchImportCustomers({
      customers,
      overwrite: false,
    })
    ElMessage.success(result.message || `导入完成：${customers.length} 条`)
    emit('success')
    handleClose()
  } catch (error: any) {
    ElMessage.error(error.message || '导入失败')
  } finally {
    importing.value = false
  }
}

function handleClose() {
  selectedFile.value = null
  uploadRef.value?.clearFiles()
  emit('update:modelValue', false)
}

async function parseCsvFile(file: File): Promise<CustomerImportRow[]> {
  if (!file.name.toLowerCase().endsWith('.csv')) {
    throw new Error('当前仅支持 CSV 文件，请将 Excel 文件另存为 CSV 后导入')
  }
  if (file.size > 10 * 1024 * 1024) {
    throw new Error('文件大小不能超过 10MB')
  }

  const content = await file.text()
  const rows = parseCsv(content)
  if (rows.length < 2) {
    throw new Error('CSV 文件没有可导入的数据')
  }

  const headers = rows[0].map(header => normalizeHeader(header))
  const customers = rows
    .slice(1)
    .filter(row => row.some(cell => cell.trim()))
    .map((row, index) => mapCustomerRow(headers, row, index + 2))

  if (customers.length === 0) {
    throw new Error('CSV 文件没有可导入的数据')
  }

  return customers
}

function parseCsv(content: string): string[][] {
  const rows: string[][] = []
  let currentRow: string[] = []
  let currentCell = ''
  let inQuotes = false

  for (let index = 0; index < content.length; index += 1) {
    const char = content[index]
    const nextChar = content[index + 1]

    if (char === '"' && inQuotes && nextChar === '"') {
      currentCell += '"'
      index += 1
    } else if (char === '"') {
      inQuotes = !inQuotes
    } else if (char === ',' && !inQuotes) {
      currentRow.push(currentCell.trim())
      currentCell = ''
    } else if ((char === '\n' || char === '\r') && !inQuotes) {
      if (char === '\r' && nextChar === '\n') {
        index += 1
      }
      currentRow.push(currentCell.trim())
      rows.push(currentRow)
      currentRow = []
      currentCell = ''
    } else {
      currentCell += char
    }
  }

  if (currentCell || currentRow.length > 0) {
    currentRow.push(currentCell.trim())
    rows.push(currentRow)
  }

  return rows
}

function normalizeHeader(header: string): string {
  const aliasMap: Record<string, string> = {
    公司名称: 'company_name',
    英文名称: 'company_name_en',
    国家代码: 'country_code',
    国家: 'country',
    城市: 'city',
    地址: 'address',
    电话: 'phone',
    邮箱: 'email',
    网站: 'website',
    业务类型: 'business_type',
    状态: 'status',
    优先级: 'priority',
    来源: 'source',
    备注: 'notes',
  }
  const normalized = header.replace(/^\uFEFF/, '').trim()
  return aliasMap[normalized] || normalized
}

function mapCustomerRow(
  headers: string[],
  row: string[],
  lineNumber: number
): CustomerImportRow {
  const rawData = headers.reduce<Record<string, string>>((result, header, index) => {
    if (header) {
      result[header] = row[index]?.trim() || ''
    }
    return result
  }, {})

  const customer: CustomerImportRow = {
    company_name: rawData.company_name,
    country_code: rawData.country_code,
    country: rawData.country,
  }

  if (!customer.company_name || !customer.country_code || !customer.country) {
    throw new Error(`第 ${lineNumber} 行缺少必填字段：company_name、country_code、country`)
  }

  const optionalFields = [
    'company_name_en',
    'city',
    'address',
    'phone',
    'email',
    'website',
    'business_type',
    'status',
    'source',
    'notes',
  ] as const

  optionalFields.forEach(field => {
    if (rawData[field]) {
      customer[field] = rawData[field]
    }
  })

  if (rawData.priority) {
    const priority = Number(rawData.priority)
    if (!Number.isInteger(priority) || priority < 1 || priority > 5) {
      throw new Error(`第 ${lineNumber} 行优先级必须是 1-5 的整数`)
    }
    customer.priority = priority
  }

  return customer
}
</script>
