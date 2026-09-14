<template>
  <div class="revor-shell">
    <header class="topbar"><div class="brand"><span class="brand-mark">T</span><span><b>Tradebase</b><small>我的增长工作台</small></span></div><nav class="topnav"><n-menu mode="horizontal" responsive :value="activeKey" :options="menuOptions" @update:value="handleMenuSelect" /></nav><div class="top-actions"><n-button quaternary circle><template #icon><n-icon :component="PersonCircleOutline" /></template></n-button><n-dropdown :options="userOptions" @select="handleUserAction"><span class="avatar">{{ (userStore.fullName || 'A').slice(0, 1).toUpperCase() }}</span></n-dropdown></div></header>
    <main class="canvas"><div class="canvas-head"><div><span class="eyebrow">AI SALES WORKSPACE</span><h1>{{ currentPageTitle }}</h1></div><div class="head-meta">准备好推进下一条商机</div></div><div class="page-content"><router-view /></div></main>
  </div>
</template>

<script setup lang="ts">
import { h, computed, Component } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NIcon, useDialog, useMessage } from 'naive-ui'
import {
  HomeOutline,
  PeopleOutline,
  GlobeOutline,
  MailOutline,
  ChatbubbleOutline,
  CheckboxOutline,
  FlashOutline,
  AnalyticsOutline,
  PersonOutline,
  LogOutOutline,
  PersonCircleOutline,
  SettingsOutline,
  RocketOutline,
} from '@vicons/ionicons5'
import { useUserStore } from '@/store/modules/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const dialog = useDialog()
const message = useMessage()

const renderIcon = (icon: Component) => {
  return () => h(NIcon, null, { default: () => h(icon) })
}

const menuOptions = computed(() => {
  const layoutRoute = router.getRoutes().find((r) => r.name === 'Layout')
  return (
    layoutRoute?.children
      ?.filter((r) => !r.meta?.hidden)
      .map((r) => ({
        label: r.meta?.title as string,
        key: r.name as string,  // 使用路由名称而不是路径
        icon: renderIcon(getIcon(r.meta?.icon as string)),
      })) || []
  )
})

const activeKey = computed(() => {
  return route.name as string || ''
})

const currentPageTitle = computed(() => {
  return route.meta?.title || '首页'
})

const userOptions = [
  {
    label: '个人中心',
    key: 'profile',
    icon: renderIcon(PersonOutline),
  },
  {
    type: 'divider',
    key: 'd1',
  },
  {
    label: '退出登录',
    key: 'logout',
    icon: renderIcon(LogOutOutline),
  },
]

function getIcon(iconName: string): Component {
  const icons: Record<string, Component> = {
    'home-outline': HomeOutline,
    'people-outline': PeopleOutline,
    'globe-outline': GlobeOutline,
    'mail-outline': MailOutline,
    'chatbubble-outline': ChatbubbleOutline,
    'checkbox-outline': CheckboxOutline,
    'flash-outline': FlashOutline,
    'analytics-outline': AnalyticsOutline,
    'person-outline': PersonOutline,
    'settings-outline': SettingsOutline,
    'rocket-outline': RocketOutline,
  }
  return icons[iconName] || HomeOutline
}

async function handleMenuSelect(key: string) {
  // key 是路由名称，需要使用对象形式导航
  try {
    await router.push({ name: key })
  } catch (error: unknown) {
    console.error('路由导航错误:', error)
    const errorMessage = error instanceof Error ? error.message : '未知错误'
    message.error(`导航失败: ${errorMessage}`)
  }
}

function handleUserAction(key: string) {
  if (key === 'profile') {
    router.push({ name: 'Profile' })
  } else if (key === 'logout') {
    dialog.warning({
      title: '退出登录',
      content: '确定要退出登录吗？',
      positiveText: '确定',
      negativeText: '取消',
      onPositiveClick: () => {
        userStore.logout()
        message.success('已退出登录')
        router.push({ name: 'Login' })
      },
    })
  }
}
</script>

<style scoped>
.revor-shell{min-height:100vh;background:#fbfbfa;color:#111}.topbar{height:76px;min-width:0;background:#fff;border-bottom:1px solid #e9e8e4;display:flex;align-items:center;padding:0 28px;gap:24px;position:sticky;top:0;z-index:10}.brand{display:flex;align-items:center;gap:10px;min-width:190px;flex:0 0 auto}.brand b{display:block;font-size:16px;letter-spacing:-.3px}.brand small{display:block;color:#92949a;font-size:10px;margin-top:3px}.brand-mark{width:31px;height:31px;border-radius:10px;display:grid;place-items:center;color:#fff;font-weight:800;background:linear-gradient(135deg,#111 0%,#685cf4 60%,#ff916d)}.topnav{flex:1;min-width:0;overflow:hidden}.topnav :deep(.n-menu){background:transparent;min-width:0;max-width:100%}.topnav :deep(.n-menu-item-content){height:76px;padding:0 11px;color:#777b83;font-size:13px;white-space:nowrap}.topnav :deep(.n-menu-item-content--selected){color:#111!important;font-weight:700;background:transparent!important}.topnav :deep(.n-menu-item-content--selected:after){background:#111!important}.top-actions{display:flex;align-items:center;gap:4px;flex:0 0 auto}.avatar{display:grid;place-items:center;width:30px;height:30px;border-radius:50%;background:#111;color:#fff;font-size:12px;cursor:pointer}.canvas{max-width:1440px;margin:0 auto;padding:52px 54px 80px;background:radial-gradient(circle at 92% 4%,rgba(255,218,194,.32),transparent 24%)}.canvas-head{display:flex;align-items:flex-end;justify-content:space-between;margin-bottom:34px}.eyebrow{font-size:10px;letter-spacing:1.8px;color:#8a7cf4;font-weight:800}.canvas h1{font-size:38px;letter-spacing:-1.8px;margin:10px 0 0;font-weight:700}.head-meta{font-size:12px;color:#97999f}.page-content :deep(.n-card){border:1px solid #e9e8e4;box-shadow:0 12px 36px rgba(25,25,25,.045)}
@media (max-width:1100px){.topbar{padding:0 18px;gap:16px}.brand{min-width:178px}.topnav :deep(.n-menu-item-content){padding:0 8px;font-size:12px}}
@media (max-width:760px){.topbar{height:64px;padding:0 14px;gap:10px}.brand{min-width:auto}.brand small{display:none}.brand b{font-size:14px}.topnav :deep(.n-menu-item-content){height:64px;padding:0 7px}.top-actions .n-button{display:none}.canvas{padding:30px 18px 50px}.canvas-head{align-items:flex-start;gap:12px;flex-direction:column}.canvas h1{font-size:30px}}
</style>
