<template>
  <div class="emails-inbox-page">
    <n-card title="邮件管理" :bordered="false">
      <template #header-extra>
        <n-space>
          <n-button type="primary" @click="handleCompose">
            <template #icon>
              <n-icon><CreateIcon /></n-icon>
            </template>
            写邮件
          </n-button>
          <n-button @click="handleRefresh">
            <template #icon>
              <n-icon><RefreshIcon /></n-icon>
            </template>
            刷新
          </n-button>
        </n-space>
      </template>

      <!-- 统计卡片 -->
      <n-grid :cols="5" :x-gap="16" class="stats-grid">
        <n-grid-item>
          <n-statistic label="总邮件" :value="stats.total || 0" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="已发送" :value="stats.sent || 0" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="已打开" :value="stats.opened || 0" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="已回复" :value="stats.replied || 0" />
        </n-grid-item>
        <n-grid-item>
          <n-statistic label="打开率" :value="`${stats.open_rate || 0}%`" />
        </n-grid-item>
      </n-grid>

      <!-- 筛选栏 -->
      <n-space class="filter-bar" vertical>
        <n-input
          v-model:value="searchKeyword"
          placeholder="搜索邮件主题或收件人"
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
          <n-select
            v-model:value="filterDirection"
            placeholder="筛选方向"
            clearable
            :style="{ width: '120px' }"
            :options="directionOptions"
          />
          <n-button type="primary" @click="handleSearch">
            搜索
          </n-button>
          <n-button @click="handleReset">
            重置
          </n-button>
        </n-space>
      </n-space>

      <!-- 邮件列表 -->
      <n-list v-if="!loading && emails.length > 0" bordered hoverable clickable>
        <n-list-item v-for="email in emails" :key="email.id" @click="handleViewEmail(email)">
          <n-thing>
            <template #header>
              <n-space align="center" :size="8">
                <n-tag :type="getStatusType(email.status)" size="small">
                  {{ EmailStatusMap[email.status] }}
                </n-tag>
                <n-tag v-if="email.direction" size="small" :type="email.direction === 'outgoing' ? 'info' : 'success'">
                  {{ EmailDirectionMap[email.direction] }}
                </n-tag>
                <span class="email-subject">{{ email.subject }}</span>
              </n-space>
            </template>

            <template #description>
              <n-space vertical :size="4">
                <div class="email-meta">
                  <span class="email-label">收件人:</span>
                  <span>{{ email.to_name || email.to_email }}</span>
                  <span class="email-label" style="margin-left: 16px">发件人:</span>
                  <span>{{ email.from_name || email.from_email }}</span>
                </div>
                <div v-if="email.template_name" class="email-meta">
                  <span class="email-label">模板:</span>
                  <n-tag size="tiny">{{ email.template_name }}</n-tag>
                </div>
              </n-space>
            </template>

            <template #action>
              <n-space>
                <n-button text type="primary" size="small" @click.stop="handleReply(email)">
                  回复
                </n-button>
                <n-button text size="small" @click.stop="handleForward(email)">
                  转发
                </n-button>
                <n-dropdown :options="getDropdownOptions(email)" @select="handleDropdownSelect">
                  <n-button text size="small">
                    <template #icon>
                      <n-icon><MoreIcon /></n-icon>
                    </template>
                  </n-button>
                </n-dropdown>
              </n-space>
            </template>
          </n-thing>

          <div v-if="email.sent_at" class="email-time">
            {{ formatTime(email.sent_at) }}
          </div>
        </n-list-item>
      </n-list>

      <!-- 空状态 -->
      <n-empty v-else-if="!loading" description="还没有邮件">
        <template #extra>
          <n-button size="small" type="primary" @click="handleCompose">
            发送第一封邮件
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

    <!-- 邮件详情抽屉 -->
    <n-drawer v-model:show="showDetailDrawer" :width="700" placement="right">
      <n-drawer-content :title="selectedEmail?.subject" closable>
        <div v-if="selectedEmail" class="email-detail">
          <n-descriptions :column="1" bordered>
            <n-descriptions-item label="发件人">
              {{ selectedEmail.from_name || selectedEmail.from_email }}
              <span class="email-address">&lt;{{ selectedEmail.from_email }}&gt;</span>
            </n-descriptions-item>
            <n-descriptions-item label="收件人">
              {{ selectedEmail.to_name || selectedEmail.to_email }}
              <span class="email-address">&lt;{{ selectedEmail.to_email }}&gt;</span>
            </n-descriptions-item>
            <n-descriptions-item label="发送时间">
              {{ selectedEmail.sent_at ? formatTime(selectedEmail.sent_at) : '-' }}
            </n-descriptions-item>
            <n-descriptions-item label="状态">
              <n-tag :type="getStatusType(selectedEmail.status)">
                {{ EmailStatusMap[selectedEmail.status] }}
              </n-tag>
            </n-descriptions-item>
            <n-descriptions-item v-if="selectedEmail.template_name" label="模板">
              {{ selectedEmail.template_name }}
            </n-descriptions-item>
          </n-descriptions>

          <n-divider />

          <div class="email-body" v-html="selectedEmail.body"></div>

          <n-divider />

          <!-- 统计信息 -->
          <n-space v-if="selectedEmail.opened_at || selectedEmail.replied_at" :size="16">
            <n-tag v-if="selectedEmail.opened_at" type="success" size="small">
              已打开: {{ formatTime(selectedEmail.opened_at) }}
            </n-tag>
            <n-tag v-if="selectedEmail.replied_at" type="info" size="small">
              已回复: {{ formatTime(selectedEmail.replied_at) }}
            </n-tag>
          </n-space>
        </div>

        <template #footer>
          <n-space>
            <n-button type="primary" @click="handleReply(selectedEmail!)">
              回复
            </n-button>
            <n-button @click="handleForward(selectedEmail!)">
              转发
            </n-button>
          </n-space>
        </template>
      </n-drawer-content>
    </n-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import {
  Create as CreateIcon,
  Refresh as RefreshIcon,
  Search as SearchIcon,
  EllipsisHorizontal as MoreIcon,
} from '@vicons/ionicons5'
import { deleteEmail, getEmails, getEmailStats, resendEmail } from '@/api/email'
import type { Email, EmailStatus, EmailDirection, EmailStats } from '@/types/email'
import {
  EmailStatusMap,
  EmailStatusTypeMap,
  EmailDirectionMap,
} from '@/types/email'

const router = useRouter()
const message = useMessage()

const loading = ref(false)
const emails = ref<Email[]>([])
const stats = ref<EmailStats>({
  total: 0,
  sent: 0,
  opened: 0,
  clicked: 0,
  replied: 0,
  failed: 0,
  by_template: {},
  open_rate: 0,
  click_rate: 0,
  reply_rate: 0,
})

const searchKeyword = ref('')
const filterStatus = ref<EmailStatus | null>(null)
const filterDirection = ref<EmailDirection | null>(null)

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

const showDetailDrawer = ref(false)
const selectedEmail = ref<Email | null>(null)

const statusOptions = [
  { label: '草稿', value: 'draft' },
  { label: '队列中', value: 'queued' },
  { label: '已发送', value: 'sent' },
  { label: '失败', value: 'failed' },
  { label: '已打开', value: 'opened' },
  { label: '已回复', value: 'replied' },
]

const directionOptions = [
  { label: '发送', value: 'outgoing' },
  { label: '接收', value: 'incoming' },
]

async function fetchEmails() {
  loading.value = true
  try {
    const response = await getEmails({
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      search: searchKeyword.value || undefined,
      status: filterStatus.value || undefined,
      direction: filterDirection.value || undefined,
    })
    emails.value = response.items
    pagination.total = response.total
  } catch (error: any) {
    message.error(error.message || '获取邮件列表失败')
  } finally {
    loading.value = false
  }
}

async function fetchStats() {
  try {
    const response = await getEmailStats()
    stats.value = response
  } catch (error: any) {
    console.error('获取统计数据失败', error)
  }
}

function handleSearch() {
  pagination.page = 1
  fetchEmails()
}

function handleReset() {
  searchKeyword.value = ''
  filterStatus.value = null
  filterDirection.value = null
  pagination.page = 1
  fetchEmails()
}

function handleRefresh() {
  fetchEmails()
  fetchStats()
}

function handlePageChange(page: number) {
  pagination.page = page
  fetchEmails()
}

function handlePageSizeChange(pageSize: number) {
  pagination.pageSize = pageSize
  pagination.page = 1
  fetchEmails()
}

function handleCompose() {
  router.push('/emails/compose')
}

function handleViewEmail(email: Email) {
  selectedEmail.value = email
  showDetailDrawer.value = true
}

function handleReply(email: Email) {
  router.push(`/emails/compose?reply_to=${email.id}`)
}

function handleForward(email: Email) {
  router.push(`/emails/compose?forward=${email.id}`)
}

function getDropdownOptions(email: Email) {
  return [
    {
      label: '查看详情',
      key: 'view',
    },
    {
      label: '重新发送',
      key: 'resend',
      disabled: email.status !== 'failed',
    },
    {
      type: 'divider',
      key: 'd1',
    },
    {
      label: '删除',
      key: 'delete',
    },
  ]
}

async function handleDropdownSelect(key: string, email: Email) {
  if (key === 'view') {
    handleViewEmail(email)
  } else if (key === 'resend') {
    try {
      await resendEmail(email.id)
      message.success('邮件已重新发送')
      fetchEmails()
      fetchStats()
    } catch (error: any) {
      message.error(error.message || '重新发送失败')
    }
  } else if (key === 'delete') {
    if (!window.confirm(`确定要删除邮件 "${email.subject}" 吗？`)) return
    try {
      await deleteEmail(email.id)
      message.success('邮件已删除')
      fetchEmails()
      fetchStats()
    } catch (error: any) {
      message.error(error.message || '删除邮件失败')
    }
  }
}

function getStatusType(status: EmailStatus) {
  return EmailStatusTypeMap[status] || 'default'
}

function formatTime(time: string) {
  return new Date(time).toLocaleString('zh-CN')
}

onMounted(() => {
  fetchEmails()
  fetchStats()
})
</script>

<style scoped>
.emails-inbox-page {
  padding: 16px;
}

.stats-grid {
  margin-bottom: 24px;
}

.filter-bar {
  margin-bottom: 16px;
}

.email-subject {
  font-weight: 500;
  font-size: 15px;
}

.email-meta {
  font-size: 13px;
  color: #666;
}

.email-label {
  color: #999;
  margin-right: 4px;
}

.email-address {
  color: #999;
  font-size: 12px;
}

.email-time {
  font-size: 12px;
  color: #999;
}

.email-detail {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.email-body {
  min-height: 200px;
  max-height: 400px;
  overflow-y: auto;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 4px;
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
