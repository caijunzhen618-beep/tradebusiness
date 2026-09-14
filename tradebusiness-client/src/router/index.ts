import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/store/modules/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录', requiresAuth: false },
  },
  {
    path: '/',
    name: 'Layout',
    component: () => import('@/views/layout/index.vue'),
    redirect: '/home',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'home',
        name: 'Home',
        component: () => import('@/views/home/index.vue'),
        meta: { title: '首页', icon: 'home-outline' },
      },
      {
        path: 'customers/my',
        name: 'MyCustomers',
        component: () => import('@/views/customers/MyCustomers.vue'),
        meta: { title: '我的客户', icon: 'people-outline' },
      },
      {
        path: 'customers/unassigned',
        name: 'UnassignedCustomers',
        component: () => import('@/views/customers/UnassignedCustomers.vue'),
        meta: { title: '未分配客户', icon: 'people-outline' },
      },
      {
        path: 'customers/discover',
        name: 'DiscoverCustomers',
        component: () => import('@/views/customers/DiscoverCustomers.vue'),
        meta: { title: '发现客户', icon: 'globe-outline' },
      },
      {
        path: 'emails',
        name: 'Emails',
        component: () => import('@/views/emails/Inbox.vue'),
        meta: { title: '邮件', icon: 'mail-outline' },
      },
      {
        path: 'emails/compose',
        name: 'ComposeEmail',
        component: () => import('@/views/emails/Compose.vue'),
        meta: { title: '写邮件', hidden: true },
      },
      {
        path: 'messages',
        name: 'Messages',
        component: () => import('@/views/messages/Messages.vue'),
        meta: { title: '消息中心', icon: 'chatbubble-outline' },
      },
      {
        path: 'tasks',
        name: 'Tasks',
        component: () => import('@/views/tasks/Tasks.vue'),
        meta: { title: '任务管理', icon: 'checkbox-outline' },
      },
      {
        path: 'analytics',
        name: 'Analytics',
        component: () => import('@/views/analytics/Analytics.vue'),
        meta: { title: '数据分析', icon: 'analytics-outline' },
      },
      {
        path: 'lead-generation',
        name: 'LeadGenerationOverview',
        component: () => import('@/views/lead-generation/Overview.vue'),
        meta: { title: 'AI 获客', icon: 'rocket-outline' },
      },
      {
        path: 'lead-generation/:id',
        name: 'LeadGenerationDetail',
        component: () => import('@/views/lead-generation/Detail.vue'),
        meta: { title: '潜客详情', hidden: true },
      },
      {
        path: 'automation',
        name: 'Automation',
        component: () => import('@/views/automation/Automation.vue'),
        meta: { title: '自动化', icon: 'flash-outline' },
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/profile/Profile.vue'),
        meta: { title: '个人中心', icon: 'person-outline' },
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/settings/Settings.vue'),
        meta: { title: '系统设置', icon: 'settings-outline' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const userStore = useUserStore()
  const requiresAuth = to.matched.some((record) => record.meta?.requiresAuth !== false)

  if (requiresAuth && !userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && userStore.isLoggedIn) {
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
