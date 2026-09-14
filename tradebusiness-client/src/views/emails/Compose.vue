<template>
  <div class="emails-compose-page">
    <n-card title="写邮件" :bordered="false">
      <template #header-extra>
        <n-button text @click="$router.back()">
          <template #icon>
            <n-icon><ArrowBackIcon /></n-icon>
          </template>
          返回
        </n-button>
      </template>

      <n-form ref="formRef" :model="emailForm" label-placement="left" label-width="80px">
        <!-- 收件人 -->
        <n-form-item label="收件人" path="to_email" :rule="toEmailRule">
          <n-input
            v-model:value="emailForm.to_email"
            placeholder="recipient@example.com"
          />
        </n-form-item>

        <n-form-item label="收件人姓名">
          <n-input v-model:value="emailForm.to_name" placeholder="可选" />
        </n-form-item>

        <!-- 模板选择 -->
        <n-form-item label="使用模板">
          <n-space vertical :style="{ width: '100%' }">
            <n-select
              v-model:value="selectedTemplateId"
              :options="templateOptions"
              placeholder="选择邮件模板（可选）"
              clearable
              @update:value="handleTemplateChange"
            />
            <n-button
              v-if="selectedTemplateId"
              text
              type="primary"
              size="small"
              @click="handlePreviewTemplate"
            >
              预览模板
            </n-button>
          </n-space>
        </n-form-item>

        <!-- 主题 -->
        <n-form-item label="主题" path="subject" :rule="{ required: true, message: '请输入邮件主题' }">
          <n-input
            v-model:value="emailForm.subject"
            placeholder="邮件主题"
          />
        </n-form-item>

        <!-- 邮件正文 -->
        <n-form-item label="正文" path="body">
          <div class="editor-wrapper">
            <n-input
              v-model:value="emailForm.body"
              type="textarea"
              placeholder="在此输入邮件正文（支持 HTML）..."
              :rows="12"
            />
            <n-space v-if="availableVariables.length > 0" class="variables-hint">
              <n-text depth="3">可用变量:</n-text>
              <n-tag
                v-for="variable in availableVariables"
                :key="variable.key"
                size="small"
                type="info"
                @click="insertVariable(variable.key)"
              >
                {{ variable.key }}
              </n-tag>
            </n-space>
          </div>
        </n-form-item>

        <!-- 模板变量 -->
        <n-form-item v-if="templateVariables.length > 0" label="模板变量">
          <n-space vertical>
            <n-form-item
              v-for="variable in templateVariables"
              :key="variable.key"
              :label="variable.key"
              :style="{ marginBottom: '8px' }"
            >
              <n-input
                v-model:value="emailForm.template_variables![variable.key]"
                :placeholder="variable.description || `输入 ${variable.key} 的值`"
              />
            </n-form-item>
          </n-space>
        </n-form-item>

        <!-- 附件 -->
        <n-form-item label="附件">
          <n-upload
            :custom-request="handleUpload"
            :show-file-list="true"
            :file-list="uploadFileList"
            @update:file-list="handleFileListChange"
          >
            <n-button>
              <template #icon>
                <n-icon><AttachIcon /></n-icon>
              </template>
              选择文件
            </n-button>
          </n-upload>
        </n-form-item>

        <!-- 操作按钮 -->
        <n-form-item :show-label="false">
          <n-space>
            <n-button type="primary" :loading="sending" @click="handleSend">
              发送邮件
            </n-button>
            <n-button @click="handleSaveDraft">
              保存草稿
            </n-button>
            <n-button @click="$router.back()">
              取消
            </n-button>
          </n-space>
        </n-form-item>
      </n-form>
    </n-card>

    <!-- 模板预览对话框 -->
    <n-modal v-model:show="showTemplatePreview" preset="card" title="模板预览" :style="{ width: '700px' }">
      <div v-if="templatePreview" class="template-preview">
        <n-descriptions :column="1" bordered>
          <n-descriptions-item label="主题">
            {{ templatePreview.subject }}
          </n-descriptions-item>
        </n-descriptions>
        <n-divider />
        <div class="preview-body" v-html="templatePreview.body"></div>
      </div>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useMessage } from 'naive-ui'
import type { FormInst, UploadCustomRequestOptions, UploadFileInfo } from 'naive-ui'
import {
  ArrowBack as ArrowBackIcon,
  Attach as AttachIcon,
} from '@vicons/ionicons5'
import {
  sendEmail,
  saveEmailDraft,
  getEmail,
  getEmailTemplates,
  previewEmailTemplate,
} from '@/api/email'
import { getCustomer } from '@/api/customer'
import { uploadAttachment } from '@/api/file'
import type { Email, EmailAttachment, EmailTemplate, SendEmailParams } from '@/types/email'
import type { Customer } from '@/types/customer'
import { TemplateCategoryMap } from '@/types/email'

const router = useRouter()
const route = useRoute()
const message = useMessage()

const formRef = ref<FormInst | null>(null)
const sending = ref(false)
const showTemplatePreview = ref(false)

const templates = ref<EmailTemplate[]>([])
const selectedTemplateId = ref<string | null>(null)
const templatePreview = ref<{ subject: string; body: string } | null>(null)
const replyToEmail = ref<Email | null>(null)
const uploadFileList = ref<UploadFileInfo[]>([])
const uploadedAttachments = ref<Record<string, EmailAttachment>>({})

const emailForm = reactive<SendEmailParams>({
  to_email: '',
  to_name: '',
  subject: '',
  body: '',
  template_id: undefined,
  template_variables: {},
  attachments: [],
})

const toEmailRule = {
  required: true,
  type: 'email',
  message: '请输入有效的邮箱地址',
  trigger: 'blur',
}

const templateOptions = computed(() => {
  return templates.value.map(t => ({
    label: `${t.name} (${TemplateCategoryMap[t.category as keyof typeof TemplateCategoryMap] || t.category})`,
    value: t.id,
  }))
})

const availableVariables = computed(() => {
  if (!selectedTemplateId.value) return []
  const template = templates.value.find(t => t.id === selectedTemplateId.value)
  if (!template?.variables) return []

  return Object.entries(template.variables).map(([key, value]) => ({
    key,
    description: typeof value === 'string' ? value : key,
  }))
})

const templateVariables = computed(() => {
  return availableVariables.value
})

async function fetchTemplates() {
  try {
    const response = await getEmailTemplates({ language: 'zh' })
    templates.value = response.filter(t => t.is_active)
  } catch (error: any) {
    message.error(error.message || '获取模板失败')
  }
}

async function handleTemplateChange(templateId: string | null) {
  emailForm.template_id = templateId || undefined

  if (templateId) {
    try {
      const preview = await previewEmailTemplate(templateId, emailForm.template_variables)
      emailForm.subject = preview.subject
      emailForm.body = preview.body
    } catch (error: any) {
      message.error('加载模板失败')
    }
  }
}

async function handlePreviewTemplate() {
  if (!selectedTemplateId.value) return

  try {
    templatePreview.value = await previewEmailTemplate(
      selectedTemplateId.value,
      emailForm.template_variables
    )
    showTemplatePreview.value = true
  } catch (error: any) {
    message.error('预览模板失败')
  }
}

function insertVariable(variableKey: string) {
  const variablePlaceholder = `{{${variableKey}}}`
  const textarea = document.querySelector('textarea') as HTMLTextAreaElement
  if (textarea) {
    const start = textarea.selectionStart
    const end = textarea.selectionEnd
    const text = emailForm.body
    emailForm.body = text.substring(0, start) + variablePlaceholder + text.substring(end)
    textarea.focus()
    textarea.setSelectionRange(start + variablePlaceholder.length, start + variablePlaceholder.length)
  }
}

async function handleSend() {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    sending.value = true

    await sendEmail(emailForm)
    message.success('邮件已发送！')
    router.back()
  } catch (error: any) {
    message.error(error.message || '发送邮件失败')
  } finally {
    sending.value = false
  }
}

async function handleSaveDraft() {
  if (!emailForm.to_email) {
    message.warning('请先填写收件人邮箱')
    return
  }

  try {
    await saveEmailDraft(emailForm)
    message.success('草稿已保存')
    router.back()
  } catch (error: any) {
    message.error(error.message || '保存草稿失败')
  }
}

async function handleUpload(options: UploadCustomRequestOptions) {
  const sourceFile = options.file.file as File | undefined
  if (!sourceFile) {
    options.onError()
    return
  }

  try {
    const uploadedFile = await uploadAttachment(sourceFile)
    uploadedAttachments.value[options.file.id] = {
      filename: uploadedFile.filename,
      url: uploadedFile.url,
      size: uploadedFile.size,
      content_type: uploadedFile.content_type,
    }
    emailForm.attachments = Object.values(uploadedAttachments.value)
    options.onFinish()
  } catch (error: any) {
    message.error(error.message || '附件上传失败')
    options.onError()
  }
}

function handleFileListChange(fileList: UploadFileInfo[]) {
  uploadFileList.value = fileList
  const activeFileIds = new Set(fileList.map(file => file.id))
  Object.keys(uploadedAttachments.value).forEach(fileId => {
    if (!activeFileIds.has(fileId)) {
      delete uploadedAttachments.value[fileId]
    }
  })
  emailForm.attachments = Object.values(uploadedAttachments.value)
}

onMounted(async () => {
  await fetchTemplates()

  // 检查是否是回复或转发邮件
  const replyToId = route.query.reply_to as string
  const forwardId = route.query.forward as string
  const customerId = route.query.customer_id as string

  if (replyToId || forwardId) {
    await loadEmailForCompose(replyToId || forwardId, Boolean(replyToId))
  } else if (customerId) {
    await loadCustomerForCompose(customerId)
  }
})

async function loadEmailForCompose(emailId: string, isReply: boolean) {
  try {
    const sourceEmail = await getEmail(emailId)
    if (isReply) {
      replyToEmail.value = sourceEmail
      emailForm.to_email = sourceEmail.from_email
      emailForm.to_name = sourceEmail.from_name || ''
      emailForm.subject = sourceEmail.subject.startsWith('Re:')
        ? sourceEmail.subject
        : `Re: ${sourceEmail.subject}`
      emailForm.body = buildQuotedBody(sourceEmail)
    } else {
      emailForm.subject = sourceEmail.subject.startsWith('Fwd:')
        ? sourceEmail.subject
        : `Fwd: ${sourceEmail.subject}`
      emailForm.body = buildForwardBody(sourceEmail)
    }
    emailForm.customer_id = sourceEmail.customer_id
  } catch (error: any) {
    message.error(error.message || '加载邮件内容失败')
  }
}

async function loadCustomerForCompose(customerId: string) {
  try {
    const customer = await getCustomer(customerId)
    emailForm.customer_id = customer.id
    emailForm.to_email = customer.email || ''
    emailForm.to_name = customer.company_name
    if (!emailForm.subject) {
      emailForm.subject = `关于 ${customer.company_name} 的合作咨询`
    }
    if (!emailForm.body) {
      emailForm.body = buildCustomerEmailBody(customer)
    }
  } catch (error: any) {
    message.error(error.message || '加载客户信息失败')
  }
}

function buildCustomerEmailBody(customer: Customer) {
  return [
    `${customer.company_name} 您好，`,
    '',
    '我们关注到贵司在货运代理领域的业务，希望有机会与您沟通潜在合作。',
    '',
    '期待您的回复。',
  ].join('\n')
}

function buildQuotedBody(email: Email) {
  return [
    '',
    '',
    '-------- 原始邮件 --------',
    `发件人: ${email.from_name || email.from_email} <${email.from_email}>`,
    `主题: ${email.subject}`,
    '',
    email.body,
  ].join('\n')
}

function buildForwardBody(email: Email) {
  return [
    '',
    '',
    '-------- 转发邮件 --------',
    `发件人: ${email.from_name || email.from_email} <${email.from_email}>`,
    `收件人: ${email.to_name || email.to_email} <${email.to_email}>`,
    `主题: ${email.subject}`,
    '',
    email.body,
  ].join('\n')
}
</script>

<style scoped>
.emails-compose-page {
  padding: 16px;
}

.editor-wrapper {
  width: 100%;
}

.variables-hint {
  margin-top: 8px;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 4px;
}

.template-preview {
  max-height: 500px;
  overflow-y: auto;
}

.preview-body {
  padding: 16px;
  background: #f9f9f9;
  border-radius: 4px;
  min-height: 200px;
}
</style>
