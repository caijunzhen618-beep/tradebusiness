<template>
  <div class="followups">
    <div class="head">
      <div><h2>跟进任务</h2><p>管理潜客下一步人工跟进。</p></div>
      <div class="head-actions">
        <el-select v-model="channel" clearable placeholder="全部渠道" @change="load">
          <el-option label="Email" value="email" /><el-option label="WhatsApp" value="whatsapp" /><el-option label="LinkedIn" value="linkedin" />
        </el-select>
        <el-button type="primary" @click="visible = true">新增跟进</el-button>
      </div>
    </div>
    <el-table :data="tasks" v-loading="loading">
      <el-table-column prop="subject" label="主题" min-width="220" />
      <el-table-column label="话术" min-width="100"><template #default="{ row }"><el-button link type="primary" @click="copyContent(row)">复制</el-button></template></el-table-column>
      <el-table-column prop="channel" label="渠道" width="120" /><el-table-column prop="due_at" label="计划时间" width="180" />
      <el-table-column prop="status" label="状态" width="120"><template #default="{ row }"><el-tag :type="row.status === 'failed' ? 'danger' : row.status === 'completed' ? 'success' : 'info'">{{ row.status }}</el-tag></template></el-table-column>
      <el-table-column label="操作" width="160"><template #default="{ row }"><el-button v-if="row.status === 'failed'" link type="warning" @click="retry(row)">重试</el-button><el-button v-else link type="primary" :disabled="row.status === 'completed'" @click="complete(row)">完成</el-button></template></el-table-column>
    </el-table>
    <el-dialog v-model="visible" title="新增跟进" width="600px">
      <el-form :model="form" label-width="90px"><el-form-item label="潜客 ID"><el-input v-model="form.lead_id" /></el-form-item><el-form-item label="渠道"><el-select v-model="form.channel"><el-option label="Email" value="email" /><el-option label="WhatsApp" value="whatsapp" /><el-option label="LinkedIn" value="linkedin" /></el-select></el-form-item><el-form-item label="主题"><el-input v-model="form.subject" /></el-form-item><el-form-item label="内容"><el-input v-model="form.content" type="textarea" :rows="5" /></el-form-item><el-form-item label="计划时间"><el-date-picker v-model="form.due_at" type="datetime" value-format="YYYY-MM-DDTHH:mm:ss" /></el-form-item></el-form>
      <template #footer><el-button @click="visible = false">取消</el-button><el-button type="primary" @click="save">保存</el-button></template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { createFollowup, getFollowups, retryFollowup, updateFollowup, type FollowupTask } from '@/api/leadGeneration'

const tasks = ref<FollowupTask[]>([])
const channel = ref('')
const loading = ref(false)
const visible = ref(false)
const form = reactive<Partial<FollowupTask>>({ lead_id: '', channel: 'email', subject: '', content: '', due_at: '' })
async function load() { loading.value = true; try { tasks.value = await getFollowups(channel.value || undefined) } finally { loading.value = false } }
async function save() { if (!form.lead_id || !form.content || !form.due_at) { ElMessage.warning('请填写潜客 ID、内容和计划时间'); return } await createFollowup(form); visible.value = false; await load(); ElMessage.success('跟进任务已创建') }
async function copyContent(row: FollowupTask) { await navigator.clipboard.writeText(row.content); ElMessage.success('话术已复制') }
async function complete(row: FollowupTask) { await updateFollowup(row.id, 'completed'); await load(); ElMessage.success('已完成') }
async function retry(row: FollowupTask) { await retryFollowup(row.id); await load(); ElMessage.success('已重新加入发送队列') }
onMounted(load)
</script>

<style scoped>
.followups { max-width: 1200px; margin: auto; }
.head-actions { display: flex; gap: 10px; align-items: center; }
.head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 24px; }
.head h2 { margin: 0; }.head p { color: #667085; }
</style>
