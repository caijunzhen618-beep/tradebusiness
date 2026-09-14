<template>
  <div class="lead-detail" v-loading="loading">
    <el-page-header
      content="潜客详情"
      @back="router.push({ name: 'LeadGeneration' })"
    /><el-button class="send-button" type="primary" @click="emailVisible = true"
      >发送开发信</el-button
    >
    <el-row :gutter="20" class="detail-grid">
      <el-col :span="10"
        ><el-card
          ><template #header
            ><div class="card-title">
              <span>{{ lead?.company_name }}</span
              ><span><el-tag v-if="lead?.do_not_contact" type="warning">已退订</el-tag><el-tag>{{ lead?.status }}</el-tag><el-button size="small" :type="lead?.do_not_contact ? 'success' : 'warning'" plain @click="toggleDoNotContact">{{ lead?.do_not_contact ? '恢复联系' : '标记退订' }}</el-button></span>
            </div></template
          ><el-descriptions :column="1"
            ><el-descriptions-item label="官网">{{
              lead?.website || "-"
            }}</el-descriptions-item
            ><el-descriptions-item label="国家">{{
              lead?.country || "-"
            }}</el-descriptions-item
            ><el-descriptions-item label="行业">{{
              lead?.industry || "-"
            }}</el-descriptions-item
            ><el-descriptions-item label="简介">{{
              lead?.description || "-"
            }}</el-descriptions-item></el-descriptions
          ></el-card
        ><el-card class="contacts-card"
          ><template #header
            ><div class="card-title">
              <span>联系人</span
              ><el-button
                size="small"
                type="primary"
                @click="contactVisible = true"
                >新增联系人</el-button
              >
            </div></template
          ><el-empty
            v-if="!contacts.length"
            description="暂无联系人" /><el-table v-else :data="contacts"
            ><el-table-column prop="name" label="姓名" /><el-table-column
              prop="title"
              label="职位" /><el-table-column
              prop="email"
              label="邮箱" /></el-table></el-card
      ></el-col>
      <el-col :span="14"
        ><el-card
          ><template #header
            ><div class="card-title">
              <span>企业背调</span
              ><el-button type="primary" @click="generateResearch"
                >重新生成</el-button
              >
            </div></template
          ><el-empty
            v-if="!research"
            description="暂无背调报告"
          /><el-descriptions v-else :column="1"
            ><el-descriptions-item label="摘要">{{
              research.summary
            }}</el-descriptions-item
            ><el-descriptions-item label="商业模式">{{
              research.business_model
            }}</el-descriptions-item
            ><el-descriptions-item label="需求信号">{{
              research.buying_signals
            }}</el-descriptions-item
            ><el-descriptions-item label="痛点">{{
              research.pain_points
            }}</el-descriptions-item
            ><el-descriptions-item label="推荐切入点">{{
              research.recommended_angle
            }}</el-descriptions-item
            ><el-descriptions-item label="数据来源"
              ><div class="source-list">
                <span>官网：{{ research.raw_sources?.website || "-" }}</span
                ><span>来源：{{ research.raw_sources?.source || "-" }}</span
                ><span
                  >官网文本：{{
                    research.raw_sources?.website_text_available
                      ? "已抓取"
                      : "未抓取或抓取失败"
                  }}</span
                >
              </div></el-descriptions-item
            ></el-descriptions
          ></el-card
        ></el-col
      >
    </el-row>
    <el-dialog v-model="contactVisible" title="新增联系人" width="520px"
      ><el-form :model="contactForm" label-width="80px"
        ><el-form-item label="姓名"
          ><el-input v-model="contactForm.name" /></el-form-item
        ><el-form-item label="职位"
          ><el-input v-model="contactForm.title" /></el-form-item
        ><el-form-item label="邮箱"
          ><el-input v-model="contactForm.email" /></el-form-item
        ><el-form-item label="电话"
          ><el-input v-model="contactForm.phone" /></el-form-item
        ><el-form-item label="LinkedIn"
          ><el-input
            v-model="contactForm.linkedin_url" /></el-form-item></el-form
      ><template #footer
        ><el-button @click="contactVisible = false">取消</el-button
        ><el-button type="primary" @click="saveContact"
          >保存</el-button
      ></template
      ></el-dialog
    >
    <el-dialog v-model="emailVisible" title="发送开发信" width="620px">
      <el-form :model="emailForm" label-width="90px">
        <el-form-item label="收件邮箱" required><el-input v-model="emailForm.to_email" placeholder="recipient@example.com" /></el-form-item>
        <el-form-item label="收件人"><el-input v-model="emailForm.to_name" /></el-form-item>
        <el-form-item label="邮件主题" required><el-input v-model="emailForm.subject" /></el-form-item>
        <el-form-item label="邮件正文" required><el-input v-model="emailForm.body" type="textarea" :rows="8" /></el-form-item>
      </el-form>
      <template #footer><el-button @click="emailVisible = false">取消</el-button><el-button type="primary" :loading="emailSending" @click="sendEmail">发送</el-button></template>
    </el-dialog>
  </div>
</template>
<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import {
  createLeadContact,
  generateCompanyResearch,
  getCompanyResearch,
  getLeadContacts,
  getLeadDetail,
  sendLeadEmail,
  updateLead,
  type CompanyResearchReport,
  type Lead,
  type LeadContact,
} from "@/api/leadGeneration";
const route = useRoute();
const router = useRouter();
const loading = ref(false);
const emailVisible = ref(false);
const emailSending = ref(false);
const emailForm = reactive({ to_email: "", to_name: "", subject: "", body: "" });
const lead = ref<Lead>();
const research = ref<CompanyResearchReport | null>(null);
const contacts = ref<LeadContact[]>([]);
const contactVisible = ref(false);
const contactForm = reactive({
  name: "",
  title: "",
  email: "",
  phone: "",
  linkedin_url: "",
});
async function load() {
  loading.value = true;
  try {
    const id = String(route.params.id);
    [lead.value, research.value, contacts.value] = await Promise.all([
      getLeadDetail(id),
      getCompanyResearch(id),
      getLeadContacts(id),
    ]);
  } finally {
    loading.value = false;
  }
}
async function generateResearch() {
  const id = String(route.params.id);
  research.value = await generateCompanyResearch(id);
  ElMessage.success("背调已更新");
}
async function sendEmail() {
  if (!emailForm.to_email || !emailForm.subject || !emailForm.body) {
    ElMessage.warning("请填写收件邮箱、主题和正文");
    return;
  }
  emailSending.value = true;
  try {
    await sendLeadEmail(String(route.params.id), emailForm);
    emailVisible.value = false;
    ElMessage.success("邮件已发送");
  } finally {
    emailSending.value = false;
  }
}
async function toggleDoNotContact() {
  if (!lead.value) return;
  const nextValue = !lead.value.do_not_contact;
  const reason = nextValue ? window.prompt("请输入退订原因（可选）") || undefined : undefined;
  lead.value = await updateLead(String(route.params.id), { do_not_contact: nextValue, do_not_contact_reason: reason });
  ElMessage.success(nextValue ? "已标记为禁止联系" : "已恢复联系");
}
async function saveContact() {
  await createLeadContact(String(route.params.id), contactForm);
  contactVisible.value = false;
  Object.assign(contactForm, {
    name: "",
    title: "",
    email: "",
    phone: "",
    linkedin_url: "",
  });
  contacts.value = await getLeadContacts(String(route.params.id));
  ElMessage.success("联系人已保存");
}
onMounted(load);
</script>
<style scoped>
.lead-detail {
  position: relative;
}
.send-button {
  position: absolute;
  right: 0;
  top: 0;
}
.lead-detail {
  max-width: 1200px;
  margin: auto;
}
.detail-grid {
  margin-top: 20px;
}
.card-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 700;
}
.contacts-card {
  margin-top: 20px;
}
.source-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  color: #667085;
  font-size: 13px;
}
</style>
