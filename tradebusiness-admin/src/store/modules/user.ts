import { defineStore } from 'pinia'
import { login, getUserInfo } from '@/api/user'
import { setToken, getToken, removeToken } from '@/utils/auth'
import { wsManager } from '@/utils/websocket'

interface UserState {
  token: string
  userInfo: any
  permissions: string[]
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    token: getToken() || '',
    userInfo: null,
    permissions: [],
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    username: (state) => state.userInfo?.username || '',
    fullName: (state) => state.userInfo?.full_name || '',
    role: (state) => state.userInfo?.role || '',
    isAdmin: (state) => state.userInfo?.role === 'admin' || state.userInfo?.is_superuser,
    userId: (state) => state.userInfo?.id || '',
  },

  actions: {
    async login(username: string, password: string) {
      try {
        const data = await login(username, password)

        this.token = data.access_token

        setToken(data.access_token)

        this.userInfo = data.user

        // 连接 WebSocket
        if (this.userId) {
          wsManager.connect(this.userId, this.token)
        }

        return data
      } catch (error) {
        console.error('[User Store] 登录失败:', error)
        throw error
      }
    },

    async fetchUserInfo() {
      try {
        const userInfo = await getUserInfo()
        this.userInfo = userInfo

        // 连接 WebSocket
        if (userInfo?.id && wsManager.getStatus() === 'disconnected') {
          wsManager.connect(userInfo.id, this.token)
        }

        return userInfo
      } catch (error) {
        throw error
      }
    },

    logout() {
      // 断开 WebSocket
      wsManager.disconnect()

      this.token = ''
      this.userInfo = null
      this.permissions = []
      removeToken()
    },

    restoreToken() {
      const token = getToken()
      if (token) {
        this.token = token
      }
    },
  },
})
