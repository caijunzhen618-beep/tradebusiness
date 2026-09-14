<template>
  <div class="users-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h2>用户管理</h2>
          <el-button :icon="Refresh" @click="fetchUsers">刷新</el-button>
        </div>
      </template>

      <el-form :inline="true" :model="filters" class="filter-form">
        <el-form-item label="角色">
          <el-select v-model="filters.role" placeholder="全部角色" clearable>
            <el-option label="管理员" value="admin" />
            <el-option label="业务员" value="sales" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">查询</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>

      <el-table v-loading="loading" :data="users" style="width: 100%">
        <el-table-column prop="username" label="用户名" width="140" />
        <el-table-column prop="full_name" label="姓名" width="140">
          <template #default="{ row }">
            {{ row.full_name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="email" label="邮箱" min-width="220" />
        <el-table-column prop="phone" label="电话" width="150">
          <template #default="{ row }">
            {{ row.phone || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="110">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'info'">
              {{ row.role === 'admin' ? '管理员' : '业务员' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="is_active" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'warning'">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="130">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-space>
              <el-button link type="primary" size="small" @click="handleToggleStatus(row)">
                {{ row.is_active ? '停用' : '启用' }}
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
import { deleteUser, getUserList, toggleUserStatus } from '@/api/user'
import type { User } from '@/types/user'

const loading = ref(false)
const users = ref<User[]>([])

const filters = reactive({
  role: '',
})

const pagination = reactive({
  page: 1,
  pageSize: 20,
  total: 0,
})

async function fetchUsers() {
  loading.value = true
  try {
    const response = await getUserList({
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      role: filters.role || undefined,
    })
    users.value = response.items || []
    pagination.total = response.total || 0
  } catch (error: any) {
    ElMessage.error(error.message || '加载用户失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  fetchUsers()
}

function handleReset() {
  filters.role = ''
  pagination.page = 1
  fetchUsers()
}

function handleSizeChange(size: number) {
  pagination.pageSize = size
  pagination.page = 1
  fetchUsers()
}

function handlePageChange(page: number) {
  pagination.page = page
  fetchUsers()
}

async function handleToggleStatus(user: User) {
  try {
    await toggleUserStatus(user.id)
    ElMessage.success(user.is_active ? '用户已停用' : '用户已启用')
    fetchUsers()
  } catch (error: any) {
    ElMessage.error(error.message || '更新用户状态失败')
  }
}

function handleDelete(user: User) {
  ElMessageBox.confirm(
    `确定要删除用户 "${user.username}" 吗？`,
    '删除用户',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await deleteUser(user.id)
      ElMessage.success('用户已删除')
      fetchUsers()
    } catch (error: any) {
      ElMessage.error(error.message || '删除用户失败')
    }
  })
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleDateString('zh-CN')
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.users-container {
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
