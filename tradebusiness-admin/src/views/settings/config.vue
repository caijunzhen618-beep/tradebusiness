<template>
  <div class="settings-container">
    <el-row :gutter="20">
      <el-col :span="4">
        <el-card>
          <el-menu
            :default-active="activeTab"
            @select="handleTabSelect"
          >
            <el-menu-item index="profile">
              <el-icon><User /></el-icon>
              <span>个人信息</span>
            </el-menu-item>
            <el-menu-item index="security">
              <el-icon><Lock /></el-icon>
              <span>安全设置</span>
            </el-menu-item>
            <el-menu-item index="notification">
              <el-icon><Bell /></el-icon>
              <span>通知设置</span>
            </el-menu-item>
            <el-menu-item index="system">
              <el-icon><Setting /></el-icon>
              <span>系统配置</span>
            </el-menu-item>
            <el-menu-item index="email">
              <el-icon><Message /></el-icon>
              <span>邮件模板</span>
            </el-menu-item>
          </el-menu>
        </el-card>
      </el-col>

      <el-col :span="20">
        <!-- 个人信息 -->
        <el-card v-if="activeTab === 'profile'">
          <template #header>
            <span>个人信息</span>
          </template>
          <el-form
            ref="profileFormRef"
            :model="profileForm"
            :rules="profileRules"
            label-width="100px"
          >
            <el-form-item label="头像">
              <el-avatar :size="80" :src="profileForm.avatar_url">
                <el-icon><UserFilled /></el-icon>
              </el-avatar>
              <el-button style="margin-left: 20px" size="small">更换头像</el-button>
            </el-form-item>
            <el-form-item label="用户名" prop="username">
              <el-input v-model="profileForm.username" disabled />
            </el-form-item>
            <el-form-item label="姓名" prop="full_name">
              <el-input v-model="profileForm.full_name" placeholder="请输入姓名" />
            </el-form-item>
            <el-form-item label="邮箱" prop="email">
              <el-input v-model="profileForm.email" placeholder="请输入邮箱" />
            </el-form-item>
            <el-form-item label="手机号" prop="phone">
              <el-input v-model="profileForm.phone" placeholder="请输入手机号" />
            </el-form-item>
            <el-form-item label="部门" prop="department">
              <el-input v-model="profileForm.department" placeholder="请输入部门" />
            </el-form-item>
            <el-form-item label="备注">
              <el-input
                v-model="profileForm.notes"
                type="textarea"
                :rows="3"
                placeholder="请输入备注"
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleUpdateProfile">保存</el-button>
              <el-button @click="handleResetProfile">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 安全设置 -->
        <el-card v-if="activeTab === 'security'">
          <template #header>
            <span>安全设置</span>
          </template>
          <el-form
            ref="passwordFormRef"
            :model="passwordForm"
            :rules="passwordRules"
            label-width="100px"
          >
            <el-form-item label="当前密码" prop="old_password">
              <el-input
                v-model="passwordForm.old_password"
                type="password"
                placeholder="请输入当前密码"
                show-password
              />
            </el-form-item>
            <el-form-item label="新密码" prop="new_password">
              <el-input
                v-model="passwordForm.new_password"
                type="password"
                placeholder="请输入新密码"
                show-password
              />
            </el-form-item>
            <el-form-item label="确认密码" prop="confirm_password">
              <el-input
                v-model="passwordForm.confirm_password"
                type="password"
                placeholder="请再次输入新密码"
                show-password
              />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleUpdatePassword">修改密码</el-button>
              <el-button @click="handleResetPassword">重置</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 通知设置 -->
        <el-card v-if="activeTab === 'notification'">
          <template #header>
            <span>通知设置</span>
          </template>
          <el-form label-width="150px">
            <el-form-item label="邮件通知">
              <el-switch v-model="notificationSettings.email" />
              <span class="form-tip">接收重要邮件通知</span>
            </el-form-item>
            <el-form-item label="任务提醒">
              <el-switch v-model="notificationSettings.taskReminder" />
              <span class="form-tip">任务即将到期时提醒</span>
            </el-form-item>
            <el-form-item label="系统通知">
              <el-switch v-model="notificationSettings.system" />
              <span class="form-tip">接收系统更新通知</span>
            </el-form-item>
            <el-form-item label="客户更新">
              <el-switch v-model="notificationSettings.customerUpdate" />
              <span class="form-tip">客户信息变更通知</span>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleSaveNotification">保存设置</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 系统配置 -->
        <el-card v-if="activeTab === 'system'">
          <template #header>
            <span>系统配置</span>
          </template>
          <el-alert
            v-if="!isAdmin"
            title="仅管理员可修改系统配置"
            type="warning"
            :closable="false"
            style="margin-bottom: 20px"
          />
          <el-form label-width="150px">
            <el-form-item label="系统名称">
              <el-input v-model="systemConfig.appName" :disabled="!isAdmin" />
            </el-form-item>
            <el-form-item label="每页显示数">
              <el-input-number v-model="systemConfig.pageSize" :min="10" :max="100" :disabled="!isAdmin" />
            </el-form-item>
            <el-form-item label="启用自动保存">
              <el-switch v-model="systemConfig.autoSave" :disabled="!isAdmin" />
            </el-form-item>
            <el-form-item label="自动保存间隔">
              <el-select v-model="systemConfig.autoSaveInterval" :disabled="!isAdmin || !systemConfig.autoSave">
                <el-option label="30秒" :value="30" />
                <el-option label="1分钟" :value="60" />
                <el-option label="5分钟" :value="300" />
                <el-option label="10分钟" :value="600" />
              </el-select>
            </el-form-item>
            <el-form-item label="启用调试模式">
              <el-switch v-model="systemConfig.debug" :disabled="!isAdmin" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :disabled="!isAdmin" @click="handleSaveSystem">保存配置</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 邮件模板 -->
        <el-card v-if="activeTab === 'email'">
          <template #header>
            <div class="card-header">
              <span>邮件模板</span>
              <el-button type="primary" size="small" @click="handleCreateTemplate">
                新建模板
              </el-button>
            </div>
          </template>
          <el-table :data="emailTemplates" style="width: 100%">
            <el-table-column prop="name" label="模板名称" />
            <el-table-column prop="subject" label="主题" />
            <el-table-column prop="category" label="类型">
              <template #default="{ row }">
                <el-tag>{{ row.category || 'default' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="updated_at" label="更新时间">
              <template #default="{ row }">
                {{ formatDate(row.updated_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="{ row }">
                <el-button link type="primary" size="small" @click="handleEditTemplate(row)">
                  编辑
                </el-button>
                <el-button link type="primary" size="small" @click="handlePreviewTemplate(row)">
                  预览
                </el-button>
                <el-popconfirm
                  title="确定删除此模板吗？"
                  @confirm="handleDeleteTemplate(row)"
                >
                  <template #reference>
                    <el-button link type="danger" size="small">删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  User,
  Lock,
  Bell,
  Setting,
  Message,
  UserFilled,
} from '@element-plus/icons-vue'
import { useUserStore } from '@/store/modules/user'
import { changePassword, updateUser } from '@/api/user'
import {
  createEmailTemplate,
  deleteEmailTemplate,
  getEmailTemplates,
  previewEmailTemplate,
  updateEmailTemplate,
  type EmailTemplate,
} from '@/api/email'

const userStore = useUserStore()
const activeTab = ref('profile')
const isAdmin = ref(userStore.isAdmin)

// 个人信息表单
const profileFormRef = ref()
const profileForm = reactive({
  username: '',
  full_name: '',
  email: '',
  phone: '',
  department: '',
  avatar_url: '',
  notes: '',
})

const profileRules = {
  full_name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' },
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' },
  ],
}

// 密码表单
const passwordFormRef = ref()
const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

const passwordRules = {
  old_password: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (_rule: any, value: string, callback: any) => {
        if (value !== passwordForm.new_password) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

// 通知设置
const notificationSettings = reactive({
  email: true,
  taskReminder: true,
  system: true,
  customerUpdate: false,
})

// 系统配置
const systemConfig = reactive({
  appName: 'TradeBusiness',
  pageSize: 20,
  autoSave: true,
  autoSaveInterval: 60,
  debug: false,
})

// 邮件模板
const emailTemplates = ref<EmailTemplate[]>([])

// Tab切换
const handleTabSelect = (key: string) => {
  activeTab.value = key
}

// 加载个人信息
const loadProfile = () => {
  const user = userStore.userInfo
  if (user) {
    Object.assign(profileForm, {
      username: user.username,
      full_name: user.full_name || '',
      email: user.email || '',
      phone: user.phone || '',
      department: user.department || '',
      avatar_url: user.avatar_url || '',
      notes: user.notes || '',
    })
  }
}

// 更新个人信息
const handleUpdateProfile = async () => {
  try {
    await profileFormRef.value.validate()
    const user = userStore.userInfo
    if (!user?.id) {
      ElMessage.error('当前用户信息不存在')
      return
    }
    const updatedUser = await updateUser(user.id, {
      full_name: profileForm.full_name,
      email: profileForm.email,
      phone: profileForm.phone,
      department: profileForm.department,
      notes: profileForm.notes,
    })
    userStore.userInfo = updatedUser
    ElMessage.success('个人信息更新成功')
  } catch (error: any) {
    ElMessage.error(error.message || '请检查表单')
  }
}

// 重置个人信息
const handleResetProfile = () => {
  loadProfile()
}

// 更新密码
const handleUpdatePassword = async () => {
  try {
    await passwordFormRef.value.validate()
    await changePassword({
      old_password: passwordForm.old_password,
      new_password: passwordForm.new_password,
    })
    ElMessage.success('密码修改成功，请重新登录')
    // 清空表单
    Object.assign(passwordForm, {
      old_password: '',
      new_password: '',
      confirm_password: '',
    })
  } catch (error: any) {
    ElMessage.error(error.message || '请检查表单')
  }
}

// 重置密码表单
const handleResetPassword = () => {
  passwordFormRef.value?.resetFields()
}

// 保存通知设置
const handleSaveNotification = () => {
  localStorage.setItem('admin_notification_settings', JSON.stringify(notificationSettings))
  ElMessage.success('通知设置已保存')
}

// 保存系统配置
const handleSaveSystem = () => {
  localStorage.setItem('admin_system_config', JSON.stringify(systemConfig))
  ElMessage.success('系统配置已保存')
}

// 新建邮件模板
const handleCreateTemplate = async () => {
  try {
    const { value: name } = await ElMessageBox.prompt('请输入模板名称', '新建模板')
    const { value: subject } = await ElMessageBox.prompt('请输入邮件主题', '新建模板')
    const { value: body } = await ElMessageBox.prompt('请输入邮件正文', '新建模板', {
      inputType: 'textarea',
    })
    await createEmailTemplate({
      name,
      subject,
      body,
      category: 'default',
      language: 'zh',
      variables: {},
      is_active: true,
    })
    ElMessage.success('模板已创建')
    await loadEmailTemplates()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '创建模板失败')
    }
  }
}

// 编辑邮件模板
const handleEditTemplate = async (row: EmailTemplate) => {
  try {
    const { value: subject } = await ElMessageBox.prompt('请输入邮件主题', '编辑模板', {
      inputValue: row.subject,
    })
    const { value: body } = await ElMessageBox.prompt('请输入邮件正文', '编辑模板', {
      inputType: 'textarea',
      inputValue: row.body,
    })
    await updateEmailTemplate(row.id, { subject, body })
    ElMessage.success('模板已更新')
    await loadEmailTemplates()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '更新模板失败')
    }
  }
}

// 预览邮件模板
const handlePreviewTemplate = async (row: EmailTemplate) => {
  try {
    const preview = await previewEmailTemplate(row.id, {})
    ElMessageBox.alert(preview.body, preview.subject, {
      dangerouslyUseHTMLString: true,
    })
  } catch (error: any) {
    ElMessage.error(error.message || '预览模板失败')
  }
}

// 删除邮件模板
const handleDeleteTemplate = async (row: EmailTemplate) => {
  try {
    await deleteEmailTemplate(row.id)
    ElMessage.success('删除成功')
    await loadEmailTemplates()
  } catch (error: any) {
    ElMessage.error(error.message || '删除模板失败')
  }
}

// 格式化日期
const formatDate = (date: string) => {
  if (!date) return '-'
  return new Date(date).toLocaleString('zh-CN')
}

const loadLocalSettings = () => {
  const savedNotifications = localStorage.getItem('admin_notification_settings')
  if (savedNotifications) {
    Object.assign(notificationSettings, JSON.parse(savedNotifications))
  }

  const savedSystemConfig = localStorage.getItem('admin_system_config')
  if (savedSystemConfig) {
    Object.assign(systemConfig, JSON.parse(savedSystemConfig))
  }
}

const loadEmailTemplates = async () => {
  try {
    emailTemplates.value = await getEmailTemplates()
  } catch (error: any) {
    ElMessage.error(error.message || '加载邮件模板失败')
  }
}

onMounted(() => {
  loadLocalSettings()
  loadProfile()
  loadEmailTemplates()
})
</script>

<style scoped>
.settings-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.form-tip {
  margin-left: 10px;
  font-size: 12px;
  color: #909399;
}
</style>
