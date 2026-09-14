import { defineStore } from 'pinia'
import { login, getUserInfo } from '@/api/user'
import { setToken, getToken, removeToken } from '@/utils/auth'

interface UserState {
  token: string
  userInfo: any
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    token: getToken() || '',
    userInfo: null,
  }),

  getters: {
    isLoggedIn: (state) => !!state.token,
    username: (state) => state.userInfo?.username || '',
    fullName: (state) => state.userInfo?.full_name || state.userInfo?.username || '',
    role: (state) => state.userInfo?.role || '',
  },

  actions: {
    async login(username: string, password: string) {
      try {
        const data = await login(username, password)
        this.token = data.access_token
        setToken(data.access_token)
        this.userInfo = data.user
        return data
      } catch (error) {
        throw error
      }
    },

    async fetchUserInfo() {
      try {
        const userInfo = await getUserInfo()
        this.userInfo = userInfo
        return userInfo
      } catch (error) {
        throw error
      }
    },

    logout() {
      this.token = ''
      this.userInfo = null
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
