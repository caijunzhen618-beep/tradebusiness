<template>
  <div class="emails-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>邮件管理</h2>
          <el-button :icon="Refresh" @click="handleRefresh">刷新</el-button>
        </div>
      </template>

      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="关键词">
          <el-input
            v-model="filters.search"
            placeholder="搜索主题"
            clearable
            @keyup.enter="handleSearch"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="filters.status" placeholder="全部状态" clearable>
            <el-option label="草稿" value="draft" />
            <el-option label="队列中" value="queued" />
            <el-option label="已发送" value="sent" />
            <el-option label="发送失败" value="failed" />
            <el-option label="已打开" value="opened" />
            <el-option label="已回复" value="replied" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table v-loading="loading" :data="emails" style="width: 100%">
        <el-table-column prop="subject" label="主题" min-width="240" />
        <el-table-column prop="to_email" label="收件人" min-width="220">
          <template #default="{ row }">
            {{ row.to_name || row.to_email || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="sent_at" label="发送时间" width="170">
          <template #default="{ row }">
            {{ row.sent_at ? formatTime(row.sent_at) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170">
          <template #default="{ row }">
            {{ formatTime(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-space>
              <el-button
                link
                type="primary"
                size="small"
                :disabled="row.status !== 'failed'"
                @click="handleResend(row)"
              >
                重发
              </el-button>
              <el-button link type="danger" size="small" @click="handleDelete(row)">
                删除
              </el-button>
            </el-space>
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { deleteEmail, getEmails, resendEmail, type Email } from '@/api/email'

const loading = ref(false)
const emails = ref<Email[]>([])

const filters = reactive({
  search: '',
  status: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

async function fetchEmails() {
  loading.value = true
  try {
    const response = await getEmails({
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      status: filters.status || undefined,
      search: filters.search || undefined,
    })
    emails.value = response.items || []
    pagination.total = response.total || 0
  } catch (error: any) {
    ElMessage.error(error.message || '加载邮件失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchEmails()
}

function handleReset() {
  filters.search = ''
  filters.status = ''
  pagination.page = 1
  fetchEmails()
}

function handleRefresh() {
  fetchEmails()
}

function handleSizeChange(size: number) {
  pagination.pageSize = size
  pagination.page = 1
  fetchEmails()
}

function handlePageChange(page: number) {
  pagination.page = page
  fetchEmails()
}

async function handleResend(email: Email) {
  try {
    await resendEmail(email.id)
    ElMessage.success('邮件已重新发送')
    fetchEmails()
  } catch (error: any) {
    ElMessage.error(error.message || '重新发送失败')
  }
}

function handleDelete(email: Email) {
  ElMessageBox.confirm(
    `确定要删除邮件 "${email.subject}" 吗？`,
    '删除邮件',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await deleteEmail(email.id)
      ElMessage.success('邮件已删除')
      fetchEmails()
    } catch (error: any) {
      ElMessage.error(error.message || '删除邮件失败')
    }
  })
}

function getStatusText(status: Email['status']) {
  const map: Record<string, string> = {
    draft: '草稿',
    queued: '队列中',
    sent: '已发送',
    failed: '发送失败',
    opened: '已打开',
    replied: '已回复',
  }
  return map[status] || status
}

type TagType = 'primary' | 'success' | 'warning' | 'info' | 'danger'

function getStatusType(status: Email['status']): TagType {
  const map: Record<string, TagType> = {
    draft: 'info',
    queued: 'warning',
    sent: 'success',
    failed: 'danger',
    opened: 'primary',
    replied: 'success',
  }
  return map[status] || 'info'
}

function formatTime(date: string) {
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchEmails()
})
</script>

<style scoped>
.emails-container {
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

.filter-form {
  margin-bottom: 16px;
}
</style>
