<template>
  <div class="profile-container">
    <n-card title="个人中心" :bordered="false">
      <n-space vertical :size="20">
        <n-space align="center" :size="16">
          <n-avatar :size="72" :src="userStore.userInfo?.avatar_url">
            {{ userInitial }}
          </n-avatar>
          <div>
            <h2 class="profile-name">{{ displayName }}</h2>
            <n-text depth="3">{{ userStore.userInfo?.email || '-' }}</n-text>
          </div>
        </n-space>

        <n-descriptions bordered :column="1">
          <n-descriptions-item label="用户名">
            {{ userStore.userInfo?.username || '-' }}
          </n-descriptions-item>
          <n-descriptions-item label="姓名">
            {{ userStore.userInfo?.full_name || '-' }}
          </n-descriptions-item>
          <n-descriptions-item label="电话">
            {{ userStore.userInfo?.phone || '-' }}
          </n-descriptions-item>
          <n-descriptions-item label="角色">
            <n-tag :type="userStore.userInfo?.role === 'admin' ? 'error' : 'info'">
              {{ userStore.userInfo?.role === 'admin' ? '管理员' : '业务员' }}
            </n-tag>
          </n-descriptions-item>
          <n-descriptions-item label="账号状态">
            <n-tag :type="userStore.userInfo?.is_active ? 'success' : 'warning'">
              {{ userStore.userInfo?.is_active ? '启用' : '停用' }}
            </n-tag>
          </n-descriptions-item>
        </n-descriptions>

        <n-space>
          <n-button type="primary" @click="router.push('/settings')">
            编辑资料
          </n-button>
        </n-space>
      </n-space>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/modules/user'

const router = useRouter()
const userStore = useUserStore()

const displayName = computed(() => {
  return userStore.userInfo?.full_name || userStore.userInfo?.username || '未登录用户'
})

const userInitial = computed(() => {
  return displayName.value.charAt(0).toUpperCase()
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
}

.profile-name {
  margin: 0 0 6px;
  font-size: 22px;
}
</style>
