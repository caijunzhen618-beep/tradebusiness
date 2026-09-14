<template>
  <div class="revor-shell">
    <header class="topbar">
      <div class="brand"><span class="brand-mark">T</span><span><b>Tradebase</b><small>货运增长工作台</small></span></div>
      <nav class="topnav"><el-menu mode="horizontal" :default-active="activeMenu" router :ellipsis="true"><el-menu-item v-for="item in menuRoutes" :key="item.path" :index="item.path">{{ item.meta?.title }}</el-menu-item></el-menu></nav>
      <div class="top-actions"><el-badge :value="unreadCount" :hidden="unreadCount === 0"><el-button text circle @click="handleNotificationClick"><el-icon><Bell /></el-icon></el-button></el-badge><el-dropdown><span class="avatar">{{ (userStore.username || 'A').slice(0, 1).toUpperCase() }}</span><template #dropdown><el-dropdown-menu><el-dropdown-item @click="handleProfile">个人中心</el-dropdown-item><el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item></el-dropdown-menu></template></el-dropdown></div>
    </header>
    <main class="canvas"><div class="canvas-head"><div><span class="eyebrow">REVOR-STYLE WORKSPACE</span><h1>{{ currentPageTitle }}</h1></div><div class="head-meta">实时同步 · {{ userStore.username }}</div></div><div class="page-content"><router-view /></div></main>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Bell } from '@element-plus/icons-vue'
import { useUserStore } from '@/store/modules/user'
import { getUnreadCount } from '@/api/notification'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const unreadCount = ref(0)
let refreshTimer: NodeJS.Timeout | null = null

const menuRoutes = computed(() => {
  const layoutRoute = router.getRoutes().find((r) => r.name === 'Layout')
  return layoutRoute?.children?.filter((r) => !r.meta?.hidden) || []
})

const activeMenu = computed(() => {
  return route.path
})

const currentPageTitle = computed(() => {
  return route.meta?.title || '首页'
})

// 加载未读数量
const loadUnreadCount = async () => {
  try {
    const res = await getUnreadCount()
    unreadCount.value = res.count
  } catch (error) {
    console.error('加载未读数量失败', error)
  }
}

// 点击通知图标
const handleNotificationClick = () => {
  router.push({ name: 'Notifications' })
}

// 个人中心
const handleProfile = () => {
  router.push({ name: 'Settings' })
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    })

    userStore.logout()
    ElMessage.success('已退出登录')
    router.push({ name: 'Login' })
  } catch {
    // 用户取消
  }
}

onMounted(() => {
  loadUnreadCount()
  // 每30秒刷新一次未读数量
  refreshTimer = setInterval(() => {
    loadUnreadCount()
  }, 30000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.revor-shell{min-height:100vh;background:#fbfbfa;color:#111}.topbar{height:76px;min-width:0;background:#fff;border-bottom:1px solid #e9e8e4;display:flex;align-items:center;padding:0 28px;gap:24px;position:sticky;top:0;z-index:10}.brand{display:flex;align-items:center;gap:10px;min-width:190px;flex:0 0 auto}.brand b{display:block;font-size:16px;letter-spacing:-.3px}.brand small{display:block;color:#92949a;font-size:10px;margin-top:3px}.brand-mark{width:31px;height:31px;border-radius:10px;display:grid;place-items:center;color:#fff;font-weight:800;background:linear-gradient(135deg,#111 0%,#685cf4 60%,#ff916d)}.topnav{flex:1;min-width:0;overflow:hidden}.topnav :deep(.el-menu){border:0;background:transparent;height:76px;min-width:0}.topnav :deep(.el-menu-item){height:76px;border:0!important;color:#777b83;font-size:13px;padding:0 11px;white-space:nowrap}.topnav :deep(.el-menu-item.is-active){color:#111!important;font-weight:700}.topnav :deep(.el-menu-item.is-active:after){height:2px;background:#111}.top-actions{display:flex;align-items:center;gap:8px;flex:0 0 auto}.avatar{display:grid;place-items:center;width:30px;height:30px;border-radius:50%;background:#111;color:#fff;font-size:12px;cursor:pointer}.canvas{max-width:1440px;margin:0 auto;padding:52px 54px 80px;background:radial-gradient(circle at 92% 4%,rgba(255,218,194,.32),transparent 24%)}.canvas-head{display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:34px}.eyebrow{font-size:10px;letter-spacing:1.8px;color:#8a7cf4;font-weight:800}.canvas h1{font-size:38px;letter-spacing:-1.8px;margin:10px 0 0;font-weight:700}.head-meta{font-size:12px;color:#97999f}.page-content :deep(.el-card){border:1px solid #e9e8e4;border-radius:18px;box-shadow:0 12px 36px rgba(25,25,25,.045)}
@media (max-width:1100px){.topbar{padding:0 18px;gap:16px}.brand{min-width:178px}.topnav :deep(.el-menu-item){padding:0 8px;font-size:12px}}
@media (max-width:760px){.topbar{height:64px;padding:0 14px;gap:10px}.brand{min-width:auto}.brand small{display:none}.brand b{font-size:14px}.topnav :deep(.el-menu),.topnav :deep(.el-menu-item){height:64px}.topnav :deep(.el-menu-item){padding:0 7px}.top-actions .el-badge{display:none}.canvas{padding:30px 18px 50px}.canvas-head{align-items:flex-start;gap:12px;flex-direction:column}.canvas h1{font-size:30px}}
</style>
