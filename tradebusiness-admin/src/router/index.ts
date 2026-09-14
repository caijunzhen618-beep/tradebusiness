import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useUserStore } from '@/store/modules/user'
import NProgress from 'nprogress'
import 'nprogress/nprogress.css'

NProgress.configure({ showSpinner: false })

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
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '仪表盘', icon: 'Odometer' },
      },
      {
        path: 'tasks',
        name: 'Tasks',
        component: () => import('@/views/tasks/list.vue'),
        meta: { title: '任务管理', icon: 'List' },
      },
      {
        path: 'notifications',
        name: 'Notifications',
        component: () => import('@/views/notifications/list.vue'),
        meta: { title: '通知中心', icon: 'Bell' },
      },
      {
        path: 'lead-generation/leads/:id',
        name: 'LeadDetail',
        component: () => import('@/views/lead-generation/detail.vue'),
        meta: { title: '潜客详情', hidden: true },
      },
      {
        path: 'customers',
        name: 'Customers',
        component: () => import('@/views/customers/list.vue'),
        meta: { title: '客户管理', icon: 'User' },
      },
      {
        path: 'customers/:id',
        name: 'CustomerDetail',
        component: () => import('@/views/customers/detail.vue'),
        meta: { title: '客户详情', hidden: true },
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/users/list.vue'),
        meta: { title: '用户管理', icon: 'UserFilled' },
      },
      {
        path: 'sales-agents/templates',
        name: 'AgentTemplates',
        component: () => import('@/views/lead-generation/templates.vue'),
        meta: { title: '话术模板', hidden: true },
      },
      {
        path: 'followups',
        name: 'Followups',
        component: () => import('@/views/lead-generation/followups.vue'),
        meta: { title: '跟进任务', icon: 'Timer' },
      },
      {
        path: 'sales-agents',
        name: 'SalesAgents',
        component: () => import('@/views/lead-generation/agents.vue'),
        meta: { title: '销售智能体', icon: 'Avatar' },
      },
      {
        path: 'lead-generation',
        name: 'LeadGeneration',
        component: () => import('@/views/lead-generation/index.vue'),
        meta: { title: 'AI 获客', icon: 'Aim' },
      },
      {
        path: 'scraping',
        name: 'Scraping',
        component: () => import('@/views/scraping/list.vue'),
        meta: { title: '数据采集', icon: 'Connection' },
      },
      {
        path: 'scraping/leads',
        name: 'ScrapingLeads',
        component: () => import('@/views/scraping/leads/list.vue'),
        meta: { title: '采集线索', icon: 'Document', hidden: true },
      },
      {
        path: 'emails',
        name: 'Emails',
        component: () => import('@/views/emails/list.vue'),
        meta: { title: '邮件管理', icon: 'Message' },
      },
      {
        path: 'cooperation',
        name: 'Cooperation',
        component: () => import('@/views/cooperation/list.vue'),
        meta: { title: '合作管理', icon: 'Link' },
      },
      {
        path: 'statistics',
        name: 'Statistics',
        component: () => import('@/views/statistics/overview.vue'),
        meta: { title: '数据统计', icon: 'DataAnalysis' },
      },
      {
        path: 'plans',
        name: 'Plans',
        component: () => import('@/views/settings/plans.vue'),
        meta: { title: '积分套餐', icon: 'Coin' },
      },
      {
        path: 'credits',
        name: 'Credits',
        component: () => import('@/views/settings/credits.vue'),
        meta: { title: '积分钱包', icon: 'Wallet' },
      },
      {
        path: 'settings',
        name: 'Settings',
        component: () => import('@/views/settings/config.vue'),
        meta: { title: '系统设置', icon: 'Setting' },
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  NProgress.start()

  const userStore = useUserStore()
  const requiresAuth = to.matched.some((record) => record.meta?.requiresAuth !== false)

  if (requiresAuth && !userStore.isLoggedIn) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && userStore.isLoggedIn) {
    next({ name: 'Dashboard' })
  } else {
    next()
  }
})

router.afterEach(() => {
  NProgress.done()
})

export default router








