<template>
  <div class="settings-page">
    <n-card title="系统设置" :bordered="false">
      <n-tabs type="line" animated placement="left" :style="{ minHeight: '500px' }">
        <!-- 个人设置 -->
        <n-tab-pane name="profile" tab="个人设置">
          <n-card title="个人信息" size="small">
            <n-form ref="profileFormRef" :model="profileForm" label-placement="left" label-width="100px">
              <n-form-item label="头像">
                <n-space align="center" :size="16">
                  <n-avatar :size="80" :src="userStore.userInfo?.avatar_url">
                    {{ userStore.userInfo?.username?.charAt(0).toUpperCase() }}
                  </n-avatar>
                  <n-upload
                    :custom-request="handleAvatarUpload"
                    :show-file-list="false"
                    accept="image/*"
                  >
                    <n-button size="small">更换头像</n-button>
                  </n-upload>
                </n-space>
              </n-form-item>

              <n-form-item label="用户名">
                <n-input v-model:value="profileForm.username" disabled />
              </n-form-item>

              <n-form-item label="姓名">
                <n-input v-model:value="profileForm.full_name" placeholder="您的姓名" />
              </n-form-item>

              <n-form-item label="邮箱">
                <n-input v-model:value="profileForm.email" placeholder="your@email.com" />
              </n-form-item>

              <n-form-item label="手机号">
                <n-input v-model:value="profileForm.phone" placeholder="+86 138 0000 0000" />
              </n-form-item>

              <n-form-item label="时区">
                <n-select
                  v-model:value="profileForm.timezone"
                  :options="timezoneOptions"
                  placeholder="选择时区"
                />
              </n-form-item>

              <n-form-item label="语言">
                <n-select
                  v-model:value="profileForm.language"
                  :options="languageOptions"
                  placeholder="选择语言"
                />
              </n-form-item>

              <n-form-item :show-label="false">
                <n-space>
                  <n-button type="primary" :loading="saving" @click="handleSaveProfile">
                    保存更改
                  </n-button>
                  <n-button @click="handleResetProfile">重置</n-button>
                </n-space>
              </n-form-item>
            </n-form>
          </n-card>

          <n-card title="修改密码" size="small" :style="{ marginTop: '16px' }">
            <n-form ref="passwordFormRef" :model="passwordForm" label-placement="left" label-width="100px">
              <n-form-item label="当前密码" path="old_password">
                <n-input
                  v-model:value="passwordForm.old_password"
                  type="password"
                  placeholder="请输入当前密码"
                  show-password-on="click"
                />
              </n-form-item>

              <n-form-item label="新密码" path="new_password">
                <n-input
                  v-model:value="passwordForm.new_password"
                  type="password"
                  placeholder="请输入新密码"
                  show-password-on="click"
                />
              </n-form-item>

              <n-form-item label="确认密码" path="confirm_password">
                <n-input
                  v-model:value="passwordForm.confirm_password"
                  type="password"
                  placeholder="请再次输入新密码"
                  show-password-on="click"
                />
              </n-form-item>

              <n-form-item :show-label="false">
                <n-space>
                  <n-button type="primary" :loading="changingPassword" @click="handleChangePassword">
                    修改密码
                  </n-button>
                  <n-button @click="handleResetPassword">重置</n-button>
                </n-space>
              </n-form-item>
            </n-form>
          </n-card>
        </n-tab-pane>

        <!-- 通知设置 -->
        <n-tab-pane name="notifications" tab="通知设置">
          <n-card title="通知偏好" size="small">
            <n-form label-placement="left" label-width="200px">
              <n-form-item label="邮件通知">
                <n-switch v-model:value="notificationSettings.email" />
                <template #feedback>
                  <n-text depth="3">接收重要更新的邮件通知</n-text>
                </template>
              </n-form-item>

              <n-form-item label="浏览器通知">
                <n-switch v-model:value="notificationSettings.browser" />
                <template #feedback>
                  <n-text depth="3">在浏览器中显示桌面通知</n-text>
                </template>
              </n-form-item>

              <n-form-item label="任务提醒">
                <n-switch v-model:value="notificationSettings.tasks" />
                <template #feedback>
                  <n-text depth="3">任务到期前提醒</n-text>
                </template>
              </n-form-item>

              <n-form-item label="客户动态">
                <n-switch v-model:value="notificationSettings.customers" />
                <template #feedback>
                  <n-text depth="3">客户状态变更时通知</n-text>
                </template>
              </n-form-item>

              <n-form-item label="邮件回复">
                <n-switch v-model:value="notificationSettings.email_replies" />
                <template #feedback>
                  <n-text depth="3">收到客户邮件回复时通知</n-text>
                </template>
              </n-form-item>

              <n-form-item label="节假日问候">
                <n-switch v-model:value="notificationSettings.holidays" />
                <template #feedback>
                  <n-text depth="3">节假日自动问候提醒</n-text>
                </template>
              </n-form-item>

              <n-form-item :show-label="false">
                <n-button type="primary" @click="handleSaveNotifications">
                  保存设置
                </n-button>
              </n-form-item>
            </n-form>
          </n-card>
        </n-tab-pane>

        <!-- SMTP设置 -->
        <n-tab-pane name="smtp" tab="邮件设置">
          <n-alert type="warning" :show-icon="false" style="margin-bottom: 16px">
            SMTP配置更改后需要重启服务才能生效
          </n-alert>

          <n-card title="SMTP服务器配置" size="small">
            <n-form ref="smtpFormRef" :model="smtpForm" label-placement="left" label-width="150px">
              <n-form-item label="SMTP服务器" path="host">
                <n-input v-model:value="smtpForm.host" placeholder="smtp.gmail.com" />
              </n-form-item>

              <n-form-item label="端口" path="port">
                <n-input-number v-model:value="smtpForm.port" :min="1" :max="65535" :style="{ width: '100%' }" />
              </n-form-item>

              <n-form-item label="用户名" path="user">
                <n-input v-model:value="smtpForm.user" placeholder="your@email.com" />
              </n-form-item>

              <n-form-item label="密码" path="password">
                <n-input
                  v-model:value="smtpForm.password"
                  type="password"
                  placeholder="SMTP密码"
                  show-password-on="click"
                />
              </n-form-item>

              <n-form-item label="发件人邮箱">
                <n-input v-model:value="smtpForm.from_email" placeholder="noreply@company.com" />
              </n-form-item>

              <n-form-item label="发件人名称">
                <n-input v-model:value="smtpForm.from_name" placeholder="Your Company" />
              </n-form-item>

              <n-form-item label="使用TLS">
                <n-switch v-model:value="smtpForm.use_tls" />
              </n-form-item>

              <n-form-item :show-label="false">
                <n-space>
                  <n-button type="primary" :loading="testingSmtp" @click="handleTestSmtp">
                    测试连接
                  </n-button>
                  <n-button type="primary" @click="handleSaveSmtp">
                    保存配置
                  </n-button>
                </n-space>
              </n-form-item>
            </n-form>
          </n-card>

          <n-card title="邮件模板" size="small" :style="{ marginTop: '16px' }">
            <n-list bordered>
              <n-list-item v-for="template in emailTemplates" :key="template.id">
                <n-thing>
                  <template #header>{{ template.name }}</template>
                  <template #description>
                    <n-text depth="3">{{ template.subject }}</n-text>
                  </template>
                </n-thing>
                <template #action>
                  <n-button size="small" @click="handleEditTemplate(template)">
                    编辑
                  </n-button>
                </template>
              </n-list-item>
            </n-list>
          </n-card>
        </n-tab-pane>

        <!-- 系统配置 -->
        <n-tab-pane name="system" tab="系统配置">
          <n-alert type="error" :show-icon="false" style="margin-bottom: 16px">
            系统配置更改需要管理员权限
          </n-alert>

          <n-card title="通用设置" size="small">
            <n-form label-placement="left" label-width="200px">
              <n-form-item label="系统名称">
                <n-input v-model:value="systemSettings.app_name" placeholder="TradeBusiness" />
              </n-form-item>

              <n-form-item label="默认语言">
                <n-select
                  v-model:value="systemSettings.default_language"
                  :options="languageOptions"
                />
              </n-form-item>

              <n-form-item label="时区">
                <n-select
                  v-model:value="systemSettings.default_timezone"
                  :options="timezoneOptions"
                />
              </n-form-item>

              <n-form-item label="每页显示数量">
                <n-input-number
                  v-model:value="systemSettings.page_size"
                  :min="10"
                  :max="100"
                  :step="10"
                />
              </n-form-item>

              <n-form-item label="启用自动保存">
                <n-switch v-model:value="systemSettings.auto_save" />
              </n-form-item>

              <n-form-item :show-label="false">
                <n-button type="primary" @click="handleSaveSystemSettings">
                  保存配置
                </n-button>
              </n-form-item>
            </n-form>
          </n-card>

          <n-card title="数据管理" size="small" :style="{ marginTop: '16px' }">
            <n-space vertical>
              <n-button @click="handleExportData">
                <template #icon>
                  <n-icon><DownloadIcon /></n-icon>
                </template>
                导出所有数据
              </n-button>

              <n-button @click="handleImportData">
                <template #icon>
                  <n-icon><UploadIcon /></n-icon>
                </template>
                导入数据
              </n-button>

              <n-popconfirm
                @positive-click="handleClearCache"
                positive-text="确定"
                negative-text="取消"
              >
                <template #trigger>
                  <n-button type="warning">
                    <template #icon>
                      <n-icon><RefreshIcon /></n-icon>
                    </template>
                    清除缓存
                  </n-button>
                </template>
                确定要清除系统缓存吗？
              </n-popconfirm>
            </n-space>
          </n-card>
        </n-tab-pane>

        <!-- 关于 -->
        <n-tab-pane name="about" tab="关于">
          <n-card title="系统信息" size="small">
            <n-descriptions :column="1" bordered>
              <n-descriptions-item label="系统名称">
                TradeBusiness Management System
              </n-descriptions-item>
              <n-descriptions-item label="版本">
                v1.0.0
              </n-descriptions-item>
              <n-descriptions-item label="构建时间">
                2026-04-03
              </n-descriptions-item>
              <n-descriptions-item label="Python版本">
                3.11+
              </n-descriptions-item>
              <n-descriptions-item label="数据库">
                MySQL 8.0+
              </n-descriptions-item>
              <n-descriptions-item label="许可证">
                MIT License
              </n-descriptions-item>
            </n-descriptions>

            <n-divider />

            <n-space vertical :style="{ textAlign: 'center' }">
              <n-text>© 2026 TradeBusiness. All rights reserved.</n-text>
              <n-text depth="3">
                货运代理业务管理系统 - 为非洲货运代理行业设计
              </n-text>
            </n-space>
          </n-card>
        </n-tab-pane>
      </n-tabs>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useMessage } from 'naive-ui'
import type { UploadCustomRequestOptions } from 'naive-ui'
import { useUserStore } from '@/store/modules/user'
import { uploadLogo } from '@/api/file'
import { getEmailTemplates, previewEmailTemplate, type EmailTemplate } from '@/api/email'
import { changePassword, updateUser } from '@/api/user'
import request from '@/api/request'
import {
  Download as DownloadIcon,
  CloudUploadOutline as UploadIcon,
  Refresh as RefreshIcon,
} from '@vicons/ionicons5'

const message = useMessage()
const userStore = useUserStore()

const saving = ref(false)
const changingPassword = ref(false)
const testingSmtp = ref(false)

// 个人设置表单
const profileForm = reactive({
  username: '',
  full_name: '',
  email: '',
  phone: '',
  timezone: 'Africa/Lagos',
  language: 'zh',
})

// 密码表单
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

// 通知设置
const notificationSettings = reactive({
  email: true,
  browser: true,
  tasks: true,
  customers: true,
  email_replies: true,
  holidays: true,
})

// SMTP设置
const smtpForm = reactive({
  host: 'smtp.gmail.com',
  port: 587,
  user: '',
  password: '',
  from_email: '',
  from_name: 'TradeBusiness',
  use_tls: true,
})

// 系统设置
const systemSettings = reactive({
  app_name: 'TradeBusiness',
  default_language: 'zh',
  default_timezone: 'Africa/Lagos',
  page_size: 20,
  auto_save: true,
})

// 邮件模板
const emailTemplates = ref<EmailTemplate[]>([])

const timezoneOptions = [
  { label: 'UTC+0 (伦敦)', value: 'Europe/London' },
  { label: 'UTC+1 (拉各斯)', value: 'Africa/Lagos' },
  { label: 'UTC+2 (开罗)', value: 'Africa/Cairo' },
  { label: 'UTC+3 (内罗毕)', value: 'Africa/Nairobi' },
  { label: 'UTC+8 (北京)', value: 'Asia/Shanghai' },
]

const languageOptions = [
  { label: '中文', value: 'zh' },
  { label: 'English', value: 'en' },
  { label: 'Français', value: 'fr' },
  { label: 'العربية', value: 'ar' },
]

async function handleAvatarUpload(options: UploadCustomRequestOptions) {
  const sourceFile = options.file.file as File | undefined
  const currentUser = userStore.userInfo
  if (!sourceFile || !currentUser?.id) {
    options.onError()
    return
  }

  try {
    const uploadedFile = await uploadLogo(sourceFile)
    const updatedUser = await updateUser(currentUser.id, {
      avatar_url: uploadedFile.url,
    })
    userStore.userInfo = updatedUser
    options.onFinish()
    message.success('头像已更新')
  } catch (error: any) {
    message.error(error.message || '头像上传失败')
    options.onError()
  }
}

async function handleSaveProfile() {
  const currentUser = userStore.userInfo
  if (!currentUser?.id) {
    message.error('当前用户信息不存在')
    return
  }

  saving.value = true
  try {
    const updatedUser = await updateUser(currentUser.id, {
      email: profileForm.email,
      full_name: profileForm.full_name,
      phone: profileForm.phone,
    })
    userStore.userInfo = updatedUser
    message.success('个人信息已保存')
  } catch (error: any) {
    message.error(error.message || '保存个人信息失败')
  } finally {
    saving.value = false
  }
}

function handleResetProfile() {
  syncProfileForm()
}

async function handleChangePassword() {
  if (!passwordForm.old_password || !passwordForm.new_password) {
    message.warning('请填写当前密码和新密码')
    return
  }
  if (passwordForm.new_password !== passwordForm.confirm_password) {
    message.warning('两次输入的新密码不一致')
    return
  }

  changingPassword.value = true
  try {
    await changePassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password,
    })
    message.success('密码已修改')
    handleResetPassword()
  } catch (error: any) {
    message.error(error.message || '修改密码失败')
  } finally {
    changingPassword.value = false
  }
}

function handleResetPassword() {
  passwordForm.old_password = ''
  passwordForm.new_password = ''
  passwordForm.confirm_password = ''
}

function handleSaveNotifications() {
  localStorage.setItem('client_notification_settings', JSON.stringify(notificationSettings))
  message.success('通知偏好已保存')
}

async function handleTestSmtp() {
  testingSmtp.value = false
  message.info('SMTP 测试需要管理员在服务端配置接口后启用')
}

function handleSaveSmtp() {
  message.info('SMTP 配置由服务端环境变量管理，请在后端配置后重启服务')
}

async function handleEditTemplate(template: EmailTemplate) {
  try {
    const preview = await previewEmailTemplate(template.id, {})
    message.info(`${preview.subject}: ${preview.body.replace(/<[^>]+>/g, '').slice(0, 80)}`)
  } catch (error: any) {
    message.error(error.message || '预览模板失败')
  }
}

function handleSaveSystemSettings() {
  localStorage.setItem('client_system_settings', JSON.stringify(systemSettings))
  message.success('系统配置已保存')
}

async function handleExportData() {
  try {
    const data = await request<Blob>({
      url: '/api/v1/export/stats',
      method: 'get',
      params: { format: 'xlsx' },
      responseType: 'blob',
    })
    const downloadUrl = URL.createObjectURL(data)
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = `customer_stats_${new Date().toISOString().slice(0, 10)}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(downloadUrl)
  } catch (error: any) {
    message.error(error.message || '导出失败')
  }
}

function handleImportData() {
  message.info('请在客户管理的批量导入页面导入客户数据')
}

function handleClearCache() {
  localStorage.removeItem('client_notification_settings')
  localStorage.removeItem('client_system_settings')
  message.success('系统缓存已清除')
}

function syncProfileForm() {
  const currentUser = userStore.userInfo
  if (!currentUser) return

  profileForm.username = currentUser.username || ''
  profileForm.full_name = currentUser.full_name || ''
  profileForm.email = currentUser.email || ''
  profileForm.phone = currentUser.phone || ''
}

function loadLocalSettings() {
  const savedNotifications = localStorage.getItem('client_notification_settings')
  if (savedNotifications) {
    Object.assign(notificationSettings, JSON.parse(savedNotifications))
  }

  const savedSystemSettings = localStorage.getItem('client_system_settings')
  if (savedSystemSettings) {
    Object.assign(systemSettings, JSON.parse(savedSystemSettings))
  }
}

async function loadEmailTemplates() {
  try {
    emailTemplates.value = await getEmailTemplates()
  } catch (error: any) {
    message.error(error.message || '加载邮件模板失败')
  }
}

onMounted(() => {
  loadLocalSettings()
  syncProfileForm()
  loadEmailTemplates()
})
</script>

<style scoped>
.settings-page {
  padding: 16px;
}
</style>
