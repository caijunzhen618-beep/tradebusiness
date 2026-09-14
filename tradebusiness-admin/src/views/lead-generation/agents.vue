<template>
  <div class="agents">
    <div class="page-head">
      <div>
        <h2>销售智能体</h2>
        <p>让 AI 按照你的公司、产品和客户画像来生成开发内容。</p>
      </div>
      <el-button type="primary" @click="openCreate">新建智能体</el-button>
    </div>
    <el-row :gutter="18"
      ><el-col v-for="agent in agents" :key="agent.id" :span="8"
        ><el-card class="agent-card"
          ><div class="agent-title">
            <strong>{{ agent.name }}</strong
            ><el-tag v-if="agent.is_default" type="success">默认</el-tag>
          </div>
          <p>{{ agent.target_customer || "尚未填写目标客户" }}</p>
          <div class="agent-meta">
            {{ agent.tone }} · {{ agent.default_language }}
          </div>
          <div class="agent-actions">
            <el-button
              link
              type="primary"
              @click="
                router.push({
                  name: 'AgentTemplates',
                  query: { agent_id: agent.id },
                })
              "
              >话术模板</el-button
            ><el-button link type="primary" @click="openEdit(agent)"
              >编辑配置</el-button
            ><el-upload
              :show-file-list="false"
              accept=".txt,.md,.csv"
              :http-request="
                (options: any) => uploadDocument(agent, options.file)
              "
              ><el-button link type="primary">上传资料</el-button></el-upload
            >
          </div>
          <div class="docs">
            {{ documents[agent.id]?.length || 0 }} 份产品资料
            <el-button
              v-if="documents[agent.id]?.length"
              link
              size="small"
              @click="previewDocuments(agent)"
              >查看资料</el-button
            >
          </div></el-card
        ></el-col
      ></el-row
    ><el-dialog
      v-model="visible"
      :title="editing ? '编辑智能体' : '新建智能体'"
      width="650px"
      ><el-form :model="form" label-width="110px"
        ><el-form-item label="名称"
          ><el-input v-model="form.name" /></el-form-item
        ><el-form-item label="公司介绍"
          ><el-input
            v-model="form.company_intro"
            type="textarea"
            :rows="2" /></el-form-item
        ><el-form-item label="产品介绍"
          ><el-input
            v-model="form.product_intro"
            type="textarea"
            :rows="2" /></el-form-item
        ><el-form-item label="价值主张"
          ><el-input
            v-model="form.value_proposition"
            type="textarea"
            :rows="2" /></el-form-item
        ><el-form-item label="目标客户"
          ><el-input
            v-model="form.target_customer"
            type="textarea"
            :rows="2" /></el-form-item
        ><el-form-item label="语气"
          ><el-select v-model="form.tone"
            ><el-option label="正式" value="professional" /><el-option
              label="友好"
              value="friendly" /><el-option
              label="简洁"
              value="concise" /></el-select></el-form-item
        ><el-form-item label="默认语言"
          ><el-select v-model="form.default_language"
            ><el-option label="英文" value="en" /><el-option
              label="中文"
              value="zh" /></el-select></el-form-item
        ><el-form-item label="设为默认"
          ><el-switch v-model="form.is_default" /></el-form-item></el-form
      ><template #footer
        ><el-button @click="visible = false">取消</el-button
        ><el-button type="primary" @click="save">保存</el-button></template
      ></el-dialog
    ><el-dialog v-model="docsVisible" title="产品资料预览" width="720px"
      ><el-collapse
        ><el-collapse-item
          v-for="doc in selectedDocs"
          :key="doc.id"
          :title="`${doc.file_name} · ${doc.embedding_status === 'ready' ? '已载入' : '处理中'}`"
          ><div class="doc-row">
            <span class="doc-status">{{
              doc.embedding_status === "ready" ? "已载入" : "处理中"
            }}</span
            ><el-button
              link
              type="danger"
              size="small"
              @click="removeDocument(doc)"
              >删除</el-button
            >
          </div>
          <pre class="doc-preview">{{ doc.content_text }}</pre>
        </el-collapse-item></el-collapse
      ></el-dialog
    >
  </div>
</template>
<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import {
  createSalesAgent,
  getSalesAgents,
  updateSalesAgent,
  getAgentDocuments,
  uploadAgentDocument,
  deleteAgentDocument,
  type SalesAgent,
  type KnowledgeDocument,
} from "@/api/salesAgents";
const router = useRouter();
const agents = ref<SalesAgent[]>([]);
const docsVisible = ref(false);
const selectedDocs = ref<KnowledgeDocument[]>([]);
const documents = ref<Record<string, KnowledgeDocument[]>>({});
const visible = ref(false);
const editing = ref<SalesAgent>();
const form = reactive<Partial<SalesAgent>>({
  name: "",
  company_intro: "",
  product_intro: "",
  value_proposition: "",
  target_customer: "",
  tone: "professional",
  default_language: "en",
  is_default: false,
});
async function load() {
  agents.value = await getSalesAgents();
  for (const agent of agents.value) {
    documents.value[agent.id] = await getAgentDocuments(agent.id);
  }
}
function previewDocuments(agent: SalesAgent) {
  selectedDocs.value = documents.value[agent.id] || [];
  docsVisible.value = true;
}
async function removeDocument(doc: KnowledgeDocument) {
  await deleteAgentDocument(doc.agent_id, doc.id);
  documents.value[doc.agent_id] = await getAgentDocuments(doc.agent_id);
  selectedDocs.value = documents.value[doc.agent_id];
  ElMessage.success('资料已删除');
}
function openCreate() {
  editing.value = undefined;
  Object.assign(form, {
    name: "",
    company_intro: "",
    product_intro: "",
    value_proposition: "",
    target_customer: "",
    tone: "professional",
    default_language: "en",
    is_default: false,
  });
  visible.value = true;
}
function openEdit(agent: SalesAgent) {
  editing.value = agent;
  Object.assign(form, agent);
  visible.value = true;
}
async function uploadDocument(agent: SalesAgent, file: File) {
  await uploadAgentDocument(agent.id, file);
  documents.value[agent.id] = await getAgentDocuments(agent.id);
  ElMessage.success("资料已上传");
}
async function save() {
  if (!form.name) {
    ElMessage.warning("请输入智能体名称");
    return;
  }
  if (editing.value) await updateSalesAgent(editing.value.id, form);
  else await createSalesAgent(form);
  visible.value = false;
  await load();
  ElMessage.success("智能体已保存");
}
onMounted(load);
</script>
<style scoped>
.agents {
  max-width: 1200px;
  margin: auto;
}
.page-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}
.page-head h2 {
  margin: 0;
}
.page-head p {
  color: #667085;
}
.agent-card {
  margin-bottom: 18px;
  border-radius: 16px;
}
.agent-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.agent-card p {
  min-height: 42px;
  color: #667085;
  line-height: 1.6;
}
.agent-meta {
  font-size: 12px;
  color: #98a2b3;
  margin-bottom: 14px;
}
.agent-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
.docs {
  margin-top: 8px;
  font-size: 12px;
  color: #98a2b3;
}
.doc-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}
.doc-status {
  font-size: 12px;
  color: #667085;
}
.doc-preview {
  white-space: pre-wrap;
  max-height: 360px;
  overflow: auto;
  background: #f8f8f6;
  padding: 14px;
  border-radius: 8px;
  line-height: 1.6;
}
</style>
