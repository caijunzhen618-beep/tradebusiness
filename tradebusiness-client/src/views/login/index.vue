<template>
  <div class="login-container">
    <n-card class="login-card" title="货运代理业务管理系统">
      <template #header-extra>
        <span class="subtitle">客户端登录</span>
      </template>

      <n-form ref="formRef" :model="loginForm" :rules="rules" size="large">
        <n-form-item path="username" label="用户名">
          <n-input
            v-model:value="loginForm.username"
            placeholder="请输入用户名"
            :input-props="{ autocomplete: 'username' }"
          >
            <template #prefix>
              <n-icon :component="PersonOutline" />
            </template>
          </n-input>
        </n-form-item>

        <n-form-item path="password" label="密码">
          <n-input
            v-model:value="loginForm.password"
            type="password"
            placeholder="请输入密码"
            show-password-on="click"
            :input-props="{ autocomplete: 'current-password' }"
          >
            <template #prefix>
              <n-icon :component="LockClosedOutline" />
            </template>
          </n-input>
        </n-form-item>

        <n-form-item>
          <n-button
            type="primary"
            :loading="loading"
            block
            size="large"
            @click="handleLogin"
          >
            {{ loading ? '登录中...' : '登录' }}
          </n-button>
        </n-form-item>
      </n-form>
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { NIcon, useMessage } from 'naive-ui'
import { PersonOutline, LockClosedOutline } from '@vicons/ionicons5'
import { useUserStore } from '@/store/modules/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const message = useMessage()

const formRef = ref()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: '',
})

const rules = {
  username: {
    required: true,
    message: '请输入用户名',
    trigger: ['blur', 'input'],
  },
  password: {
    required: true,
    message: '请输入密码',
    trigger: ['blur', 'input'],
  },
}

const handleLogin = async () => {
  try {
    await formRef.value?.validate()

    loading.value = true
    await userStore.login(loginForm.username, loginForm.password)

    message.success('登录成功')

    // 跳转到重定向页面或首页
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (error: any) {
    message.error(error.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 400px;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

.subtitle {
  color: #909399;
  font-size: 14px;
}
</style>
