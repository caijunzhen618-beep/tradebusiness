import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/es/locale/lang/zh-cn'

import App from './App.vue'
import router from './router'
import logger from './utils/logger'

const app = createApp(App)

// 注册所有 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus, {
  locale: zhCn,
})

// Global error handler
app.config.errorHandler = (err, instance, info) => {
  logger.error('Vue Error Handler', {
    error: err,
    info,
    component: instance?.$?.type?.name || 'Unknown',
  })
}

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
  logger.error('Unhandled Promise Rejection', event.reason)
})

// Handle global errors
window.addEventListener('error', (event) => {
  logger.error('Global Error', {
    message: event.message,
    filename: event.filename,
    lineno: event.lineno,
    colno: event.colno,
    error: event.error,
  })
})

logger.info('Application starting', {
  environment: import.meta.env.MODE,
  version: import.meta.env.VITE_APP_VERSION || '0.1.0',
})

app.mount('#app')

logger.info('Application mounted successfully')

