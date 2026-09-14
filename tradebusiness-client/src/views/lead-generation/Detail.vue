<template>
  <div class="lead-detail">
    <n-space vertical :size="20">
      <n-page-header title="潜客详情" subtitle="AI 获客" @back="router.push({ name: 'LeadGenerationOverview' })" />
      <n-spin :show="loading">
        <n-card v-if="lead" :title="lead.company_name" :bordered="false">
          <template #header-extra><n-space><n-tag v-if="lead.do_not_contact" type="warning" v-text="'已退订'" /><n-tag :type="lead.status === 'invalid' ? 'error' : 'info'" v-text="lead.status" /><n-button size="small" :type="lead.do_not_contact ? 'success' : 'warning'" secondary @click="toggleDoNotContact" v-text="lead.do_not_contact ? '恢复联系' : '标记退订'" /></n-space></template>
          <n-descriptions :column="2" bordered>
            <n-descriptions-item label="官网" :content="lead.website || '-'" />
            <n-descriptions-item label="国家" :content="lead.country || '-'" />
            <n-descriptions-item label="行业" :content="lead.industry || '-'" />
            <n-descriptions-item label="来源" :content="lead.source || '-'" />
            <n-descriptions-item label="简介" :span="2" :content="lead.description || '暂无简介'" />
          </n-descriptions>
        </n-card>
        <n-empty v-else description="未找到潜客" />
        <n-card v-if="lead" title="联系人" :bordered="false">
          <template #header-extra><n-button secondary type="primary" @click="contactVisible = true" v-text="'新增联系人'" /></template>
          <n-list v-if="contacts.length" bordered>
            <n-list-item v-for="contact in contacts" :key="contact.id">
              <n-thing :title="contact.name || '未命名联系人'" :description="[contact.title, contact.email, contact.phone].filter(Boolean).join(' · ') || '暂无联系方式'" />
              <template #suffix><n-tag v-if="contact.is_verified" type="success" size="small" v-text="'已验证'" /></template>
            </n-list-item>
          </n-list>
          <n-empty v-else description="暂无联系人" />
        </n-card>
        <n-card v-if="lead" title="企业背调" :bordered="false">
          <template #header-extra><n-button type="primary" secondary :loading="researchLoading" @click="generateResearch" v-text="research ? '重新生成' : '生成背调'" /></template>
          <n-descriptions v-if="research" :column="1" bordered>
            <n-descriptions-item label="摘要" :content="research.summary" />
            <n-descriptions-item label="商业模式" :content="research.business_model || '-'" />
            <n-descriptions-item label="需求信号" :content="research.buying_signals || '-'" />
            <n-descriptions-item label="痛点" :content="research.pain_points || '-'" />
            <n-descriptions-item label="推荐切入点" :content="research.recommended_angle || '-'" />
          </n-descriptions>
          <n-empty v-else description="暂无背调报告" />
        </n-card>
        <n-card v-if="lead" title="开发信" :bordered="false">
          <template #header-extra><n-space><n-select v-model:value="copyChannel" :options="channelOptions" size="small" style="width: 120px" /><n-select v-model:value="copyLanguage" :options="languageOptions" size="small" style="width: 100px" /><n-button v-if="copies.length && copyChannel === 'email'" secondary @click="openEmail(copies[0])" v-text="'发送开发信'" /><n-button type="primary" secondary :loading="copyLoading" @click="generateCopy" v-text="copies.length ? '重新生成' : '生成内容'" /></n-space></template>
          <n-list v-if="copies.length" bordered>
            <n-list-item v-for="copy in copies" :key="copy.id">
              <n-space justify="space-between" align="start" :wrap="false">
                <n-thing :title="copy.subject || '英文开发信'" :description="copy.content" />
                <n-button secondary size="small" @click="copyContent(copy)" v-text="'复制'" />
              </n-space>
            </n-list-item>
          </n-list>
          <n-empty v-else description="暂无开发信" />
        </n-card>
        <n-card v-if="lead" title="安排跟进" :bordered="false">
          <n-form inline label-placement="left">
            <n-form-item label="跟进时间"><n-date-picker v-model:value="followupDate" type="datetime" clearable /></n-form-item>
            <n-form-item><n-input v-model:value="followupContent" placeholder="填写下一次跟进内容" style="width: 360px" /></n-form-item>
            <n-form-item><n-button type="primary" :loading="followupLoading" @click="scheduleFollowup" v-text="'创建跟进任务'" /></n-form-item>
          </n-form>
        </n-card>
        <n-card v-if="lead" title="跟进记录" :bordered="false">
          <n-list v-if="followups.length" bordered>
            <n-list-item v-for="task in followups" :key="task.id">
              <n-thing :title="task.subject || '邮件跟进'" :description="`${formatDate(task.due_at)} · ${task.content}`" />
              <template #suffix><n-space><n-tag :type="followupTagType(task.status)" v-text="task.status" /><n-button v-if="task.status === 'failed'" size="small" secondary @click="retryTask(task.id)" v-text="'重试'" /><n-button v-if="task.status === 'pending'" size="small" secondary type="warning" @click="cancelTask(task.id)" v-text="'取消'" /></n-space></template>
            </n-list-item>
          </n-list>
          <n-empty v-else description="暂无跟进任务" />
        </n-card>
      </n-spin>
    </n-space>
    <n-modal v-model:show="contactVisible" preset="card" title="新增联系人" style="width: 520px">
      <n-form :model="contactForm" label-placement="left" label-width="80">
        <n-form-item label="姓名"><n-input v-model:value="contactForm.name" /></n-form-item>
        <n-form-item label="职位"><n-input v-model:value="contactForm.title" /></n-form-item>
        <n-form-item label="邮箱"><n-input v-model:value="contactForm.email" /></n-form-item>
        <n-form-item label="电话"><n-input v-model:value="contactForm.phone" /></n-form-item>
        <n-form-item label="LinkedIn"><n-input v-model:value="contactForm.linkedin_url" /></n-form-item>
      </n-form>
      <template #footer><n-space justify="end"><n-button @click="contactVisible = false" v-text="'取消'" /><n-button type="primary" :loading="contactSaving" @click="saveContact" v-text="'保存'" /></n-space></template>
    </n-modal>
    <n-modal v-model:show="emailVisible" preset="card" title="发送开发信" style="width: 620px">
      <n-form :model="emailForm" label-placement="left" label-width="90">
        <n-form-item label="收件邮箱" required><n-input v-model:value="emailForm.to_email" placeholder="buyer@example.com" /></n-form-item>
        <n-form-item label="收件人"><n-input v-model:value="emailForm.to_name" /></n-form-item>
        <n-form-item label="主题" required><n-input v-model:value="emailForm.subject" /></n-form-item>
        <n-form-item label="正文" required><n-input v-model:value="emailForm.body" type="textarea" :autosize="{ minRows: 8, maxRows: 16 }" /></n-form-item>
      </n-form>
      <template #footer><n-space justify="end"><n-button @click="emailVisible = false" v-text="'取消'" /><n-button type="primary" :loading="emailSending" @click="sendEmail" v-text="'发送'" /></n-space></template>
    </n-modal>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMessage } from 'naive-ui'
import { createFollowup, createLeadContact, generateCompanyResearch, generateSalesCopy, getCompanyResearch, getFollowups, getLeadContacts, getLeadDetail, getSalesCopies, retryFollowup, sendLeadEmail, updateFollowup, updateLead, type CompanyResearchReport, type FollowupTask, type Lead, type LeadContact, type SalesCopy } from '@/api/leadGeneration'

const route = useRoute()
const router = useRouter()
const message = useMessage()
const loading = ref(false)
const lead = ref<Lead>()
const research = ref<CompanyResearchReport | null>(null)
const researchLoading = ref(false)
const contacts = ref<LeadContact[]>([])
const contactVisible = ref(false)
const contactSaving = ref(false)
const contactForm = ref({ name: '', title: '', email: '', phone: '', linkedin_url: '', whatsapp: '', source: '', is_verified: false })
const copies = ref<SalesCopy[]>([])
const copyLoading = ref(false)
const copyChannel = ref<'email' | 'whatsapp' | 'linkedin'>('email')
const copyLanguage = ref<'en' | 'zh'>('en')
const channelOptions = [{ label: 'Email', value: 'email' }, { label: 'WhatsApp', value: 'whatsapp' }, { label: 'LinkedIn', value: 'linkedin' }]
const languageOptions = [{ label: '英文', value: 'en' }, { label: '中文', value: 'zh' }]
const emailVisible = ref(false)
const emailSending = ref(false)
const emailForm = ref({ to_email: '', to_name: '', subject: '', body: '' })
const followupDate = ref(Date.now() + 24 * 60 * 60 * 1000)
const followupContent = ref('')
const followupLoading = ref(false)
const followups = ref<FollowupTask[]>([])

onMounted(async () => {
  loading.value = true
  try {
    const id = String(route.params.id)
    const result = await Promise.all([getLeadDetail(id), getCompanyResearch(id), getSalesCopies(id), getLeadContacts(id), getFollowups(id)])
    lead.value = result[0]
    research.value = result[1]
    copies.value = result[2]
    contacts.value = result[3]
    followups.value = result[4]
  } finally {
    loading.value = false
  }
})

async function generateResearch() {
  researchLoading.value = true
  try { research.value = await generateCompanyResearch(String(route.params.id)) } finally { researchLoading.value = false }
}

async function generateCopy() {
  copyLoading.value = true
  try { copies.value = [await generateSalesCopy(String(route.params.id), { channel: copyChannel.value, language: copyLanguage.value }), ...copies.value] } finally { copyLoading.value = false }
}

async function copyContent(copy: SalesCopy) {
  await navigator.clipboard.writeText([copy.subject, copy.content].filter(Boolean).join('\n\n'))
  message.success('开发信已复制')
}

function openEmail(copy: SalesCopy) {
  emailForm.value.subject = copy.subject || ''
  emailForm.value.body = copy.content
  emailVisible.value = true
}

async function sendEmail() {
  if (!emailForm.value.to_email || !emailForm.value.subject || !emailForm.value.body) {
    message.warning('请填写收件邮箱、主题和正文')
    return
  }
  emailSending.value = true
  try {
    await sendLeadEmail(String(route.params.id), emailForm.value)
    emailVisible.value = false
    message.success('邮件已发送')
  } finally { emailSending.value = false }
}

async function toggleDoNotContact() {
  if (!lead.value) return
  const nextValue = !lead.value.do_not_contact
  const reason = nextValue ? window.prompt('请输入退订原因（可选）') || undefined : undefined
  lead.value = await updateLead(String(route.params.id), { do_not_contact: nextValue, do_not_contact_reason: reason })
  message.success(nextValue ? '已标记为禁止联系' : '已恢复联系')
}

async function scheduleFollowup() {
  if (!followupDate.value || !followupContent.value.trim()) {
    message.warning('请填写跟进时间和内容')
    return
  }
  followupLoading.value = true
  try {
    await createFollowup(String(route.params.id), {
      channel: 'email',
      subject: copies.value[0]?.subject || undefined,
      content: followupContent.value.trim(),
      due_at: new Date(followupDate.value).toISOString(),
    })
    followups.value = await getFollowups().then((items) => items.filter((task) => task.lead_id === String(route.params.id)))
    followupContent.value = ''
    message.success('跟进任务已创建')
  } finally {
    followupLoading.value = false
  }
}

function formatDate(value: string) {
  return new Date(value).toLocaleString()
}

function followupTagType(status: string) {
  if (status === 'completed') return 'success'
  if (status === 'failed') return 'error'
  if (status === 'cancelled') return 'warning'
  return 'info'
}

async function refreshFollowups() {
  followups.value = await getFollowups(String(route.params.id))
}

async function retryTask(id: string) {
  await retryFollowup(id)
  await refreshFollowups()
  message.success('跟进任务已重新排队')
}

async function cancelTask(id: string) {
  await updateFollowup(id, 'cancelled')
  await refreshFollowups()
  message.success('跟进任务已取消')
}

async function saveContact() {
  if (!contactForm.value.email && !contactForm.value.phone && !contactForm.value.linkedin_url) {
    message.warning('请至少填写邮箱、电话或 LinkedIn')
    return
  }
  contactSaving.value = true
  try {
    const contact = await createLeadContact(String(route.params.id), contactForm.value)
    contacts.value = [...contacts.value, contact]
    contactVisible.value = false
    contactForm.value = { name: '', title: '', email: '', phone: '', linkedin_url: '', whatsapp: '', source: '', is_verified: false }
    message.success('联系人已保存')
  } finally { contactSaving.value = false }
}
</script>

<style scoped>
.lead-detail{max-width:1080px;margin:0 auto}
</style>
