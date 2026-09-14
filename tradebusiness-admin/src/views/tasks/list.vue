<template>
  <div class="tasks-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>任务管理</h2>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            新建任务
          </el-button>
        </div>
      </template>

      <!-- 搜索筛选 -->
      <el-form :inline="true" :model="queryParams" class="search-form">
        <el-form-item label="状态">
          <el-select v-model="queryParams.status" placeholder="全部" clearable @change="handleQuery">
            <el-option label="待处理" value="pending" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="queryParams.priority" placeholder="全部" clearable @change="handleQuery">
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
            <el-option label="紧急" value="urgent" />
          </el-select>
        </el-form-item>
        <el-form-item label="搜索">
          <el-input
            v-model="queryParams.search"
            placeholder="搜索任务标题"
            clearable
            @keyup.enter="handleQuery"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleQuery">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <!-- 快捷筛选 -->
      <div class="quick-filters">
        <el-button
          :type="activeTab === 'all' ? 'primary' : 'default'"
          @click="handleTabChange('all')"
        >
          全部 ({{ stats.total || 0 }})
        </el-button>
        <el-button
          :type="activeTab === 'my' ? 'primary' : 'default'"
          @click="handleTabChange('my')"
        >
          我的任务
        </el-button>
        <el-button
          :type="activeTab === 'overdue' ? 'primary' : 'default'"
          @click="handleTabChange('overdue')"
        >
          逾期 ({{ stats.overdue || 0 }})
        </el-button>
        <el-button
          :type="activeTab === 'upcoming' ? 'primary' : 'default'"
          @click="handleTabChange('upcoming')"
        >
          即将到期
        </el-button>
      </div>

      <!-- 任务列表 -->
      <el-table
        v-loading="loading"
        :data="taskList"
        style="width: 100%; margin-top: 20px"
      >
        <el-table-column prop="title" label="任务标题" min-width="200" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)">
              {{ getPriorityText(row.priority) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="负责人" width="120">
          <template #default="{ row }">
            {{ row.assigned_user?.full_name || row.assigned_user?.username || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="due_date" label="截止日期" width="120">
          <template #default="{ row }">
            {{ row.due_date ? formatDate(row.due_date) : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="120">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="handleView(row)">
              查看
            </el-button>
            <el-button link type="primary" size="small" @click="handleEdit(row)">
              编辑
            </el-button>
            <el-button
              v-if="row.status !== 'completed'"
              link
              type="success"
              size="small"
              @click="handleComplete(row)"
            >
              完成
            </el-button>
            <el-popconfirm
              title="确定删除此任务吗？"
              @confirm="handleDelete(row)"
            >
              <template #reference>
                <el-button link type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <el-pagination
        v-model:current-page="queryParams.page"
        v-model:page-size="queryParams.pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end"
        @size-change="handleQuery"
        @current-change="handleQuery"
      />
    </el-card>

    <!-- 任务对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="600px"
      @close="handleDialogClose"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="100px"
      >
        <el-form-item label="任务标题" prop="title">
          <el-input v-model="formData.title" placeholder="请输入任务标题" />
        </el-form-item>
        <el-form-item label="任务描述" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="4"
            placeholder="请输入任务描述"
          />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-select v-model="formData.priority" placeholder="请选择优先级">
            <el-option label="低" value="low" />
            <el-option label="中" value="medium" />
            <el-option label="高" value="high" />
            <el-option label="紧急" value="urgent" />
          </el-select>
        </el-form-item>
        <el-form-item label="负责人" prop="assigned_to">
          <el-select v-model="formData.assigned_to" placeholder="请选择负责人" filterable>
            <el-option
              v-for="user in userList"
              :key="user.id"
              :label="user.full_name || user.username"
              :value="user.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="截止日期" prop="due_date">
          <el-date-picker
            v-model="formData.due_date"
            type="datetime"
            placeholder="请选择截止日期"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DD HH:mm:ss"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getTasks,
  getMyTasks,
  getOverdueTasks,
  getUpcomingTasks,
  createTask,
  updateTask,
  deleteTask,
  completeTask,
  getTaskStats,
  type Task,
  type TaskCreate,
  type TaskUpdate,
} from '@/api/task'
import { getUserList } from '@/api/user'

const loading = ref(false)
const taskList = ref<Task[]>([])
const total = ref(0)
const userList = ref<any[]>([])
const dialogVisible = ref(false)
const dialogTitle = ref('')
const formRef = ref()
const activeTab = ref('all')

const queryParams = reactive({
  page: 1,
  pageSize: 20,
  status: '',
  priority: '',
  search: '',
})

const formData = reactive<Partial<TaskCreate>>({
  title: '',
  description: '',
  priority: 'medium',
  assigned_to: '',
  due_date: '',
})
const editingTaskId = ref<string | null>(null)

const formRules = {
  title: [{ required: true, message: '请输入任务标题', trigger: 'blur' }],
  description: [{ required: true, message: '请输入任务描述', trigger: 'blur' }],
  priority: [{ required: true, message: '请选择优先级', trigger: 'change' }],
  assigned_to: [{ required: true, message: '请选择负责人', trigger: 'change' }],
}

const stats = ref({
  total: 0,
  pending: 0,
  in_progress: 0,
  completed: 0,
  overdue: 0,
  upcoming: 0,
})

// 加载任务列表
const loadTasks = async () => {
  try {
    loading.value = true
    let res
    const params = {
      skip: (queryParams.page - 1) * queryParams.pageSize,
      limit: queryParams.pageSize,
      status: queryParams.status || undefined,
      priority: queryParams.priority || undefined,
      search: queryParams.search || undefined,
    }

    switch (activeTab.value) {
      case 'my':
        res = await getMyTasks(params)
        break
      case 'overdue':
        res = await getOverdueTasks(params)
        break
      case 'upcoming':
        res = await getUpcomingTasks(params)
        break
      default:
        res = await getTasks(params)
    }

    taskList.value = res.items
    total.value = res.total
  } catch (error) {
    ElMessage.error('加载任务列表失败')
  } finally {
    loading.value = false
  }
}

// 加载统计数据
const loadStats = async () => {
  try {
    const res = await getTaskStats()
    stats.value = res
  } catch (error) {
    console.error('加载统计数据失败', error)
  }
}

// 加载用户列表
const loadUsers = async () => {
  try {
    const res = await getUserList({ skip: 0, limit: 100 })
    userList.value = res.items || res
  } catch (error) {
    console.error('加载用户列表失败', error)
  }
}

// 查询
const handleQuery = () => {
  queryParams.page = 1
  loadTasks()
}

// 重置
const handleReset = () => {
  queryParams.status = ''
  queryParams.priority = ''
  queryParams.search = ''
  handleQuery()
}

// Tab切换
const handleTabChange = (tab: string) => {
  activeTab.value = tab
  queryParams.page = 1
  loadTasks()
}

// 新建
const handleCreate = () => {
  dialogTitle.value = '新建任务'
  Object.assign(formData, {
    title: '',
    description: '',
    priority: 'medium',
    assigned_to: '',
    due_date: '',
  })
  editingTaskId.value = null
  dialogVisible.value = true
}

// 查看
const handleView = (row: Task) => {
  ElMessageBox.alert(
    `
    <div style="line-height: 2;">
      <p><strong>标题：</strong>${row.title}</p>
      <p><strong>描述：</strong>${row.description}</p>
      <p><strong>状态：</strong>${getStatusText(row.status)}</p>
      <p><strong>优先级：</strong>${getPriorityText(row.priority)}</p>
      <p><strong>负责人：</strong>${row.assigned_user?.full_name || '-'}</p>
      <p><strong>截止日期：</strong>${row.due_date ? formatDate(row.due_date) : '-'}</p>
      <p><strong>创建时间：</strong>${formatDate(row.created_at)}</p>
    </div>
    `,
    '任务详情',
    {
      dangerouslyUseHTMLString: true,
      confirmButtonText: '关闭',
    }
  )
}

// 编辑
const handleEdit = (row: Task) => {
  dialogTitle.value = '编辑任务'
  Object.assign(formData, {
    title: row.title,
    description: row.description,
    priority: row.priority,
    assigned_to: row.assigned_to,
    due_date: row.due_date || '',
  })
  editingTaskId.value = row.id
  dialogVisible.value = true
}

// 完成
const handleComplete = async (row: Task) => {
  try {
    await completeTask(row.id)
    ElMessage.success('任务已完成')
    loadTasks()
    loadStats()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

// 删除
const handleDelete = async (row: Task) => {
  try {
    await deleteTask(row.id)
    ElMessage.success('删除成功')
    loadTasks()
    loadStats()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value.validate()
    const data = { ...formData }

    if (editingTaskId.value) {
      await updateTask(editingTaskId.value, data as TaskUpdate)
      ElMessage.success('更新成功')
    } else {
      await createTask(data as TaskCreate)
      ElMessage.success('创建成功')
    }

    dialogVisible.value = false
    loadTasks()
    loadStats()
  } catch (error: any) {
    if (error.errors) {
      ElMessage.error('请检查表单')
    } else {
      ElMessage.error('操作失败')
    }
  }
}

// 对话框关闭
const handleDialogClose = () => {
  formRef.value?.resetFields()
  editingTaskId.value = null
}

// 状态类型
const getStatusType = (status: string) => {
  const map: Record<string, any> = {
    pending: 'info',
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'danger',
  }
  return map[status] || 'info'
}

// 状态文本
const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    pending: '待处理',
    in_progress: '进行中',
    completed: '已完成',
    cancelled: '已取消',
  }
  return map[status] || status
}

// 优先级类型
const getPriorityType = (priority: string) => {
  const map: Record<string, any> = {
    low: 'info',
    medium: '',
    high: 'warning',
    urgent: 'danger',
  }
  return map[priority] || ''
}

// 优先级文本
const getPriorityText = (priority: string) => {
  const map: Record<string, string> = {
    low: '低',
    medium: '中',
    high: '高',
    urgent: '紧急',
  }
  return map[priority] || priority
}

// 格式化日期
const formatDate = (date: string) => {
  return new Date(date).toLocaleString('zh-CN')
}

onMounted(() => {
  loadTasks()
  loadStats()
  loadUsers()
})
</script>

<style scoped>
.tasks-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-form {
  margin-bottom: 20px;
}

.quick-filters {
  margin: 20px 0;
  display: flex;
  gap: 10px;
}
</style>
