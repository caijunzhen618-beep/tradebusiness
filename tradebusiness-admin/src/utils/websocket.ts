/**
 * WebSocket 管理器
 * 处理 WebSocket 连接和消息接收
 */

import { ElNotification } from 'element-plus'

type MessageHandler = (data: any) => void
type ConnectionStatus = 'connecting' | 'connected' | 'disconnected' | 'error'

function getWebSocketBaseUrl(): string {
  const configuredUrl = import.meta.env.VITE_APP_WS_URL
  if (configuredUrl && configuredUrl !== 'wss://api.example.com') {
    return configuredUrl.replace(/\/$/, '')
  }

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  return `${protocol}//${window.location.host}`
}

class WebSocketManager {
  private ws: WebSocket | null = null
  private userId: string = ''
  private token: string = ''
  private reconnectTimer: NodeJS.Timeout | null = null
  private reconnectAttempts: number = 0
  private maxReconnectAttempts: number = 5
  private reconnectDelay: number = 3000
  private messageHandlers: Map<string, MessageHandler[]> = new Map()
  private status: ConnectionStatus = 'disconnected'
  private statusHandlers: ((status: ConnectionStatus) => void)[] = []

  /**
   * 连接 WebSocket
   */
  connect(userId: string, token: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      return
    }

    const wsUrl = `${getWebSocketBaseUrl()}/api/v1/notifications/ws/${userId}`
    this.userId = userId
    this.token = token
    this.setStatus('connecting')

    try {
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        this.setStatus('connected')
        this.reconnectAttempts = 0

        // 发送 ping 消息保持连接
        this.startHeartbeat()
      }

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)

          // 处理不同类型的消息
          this.handleMessage(message)
        } catch (error) {
          console.error('[WebSocket] Failed to parse message:', error)
        }
      }

      this.ws.onerror = (error) => {
        console.error('[WebSocket] Error:', error)
        this.setStatus('error')
      }

      this.ws.onclose = () => {
        this.setStatus('disconnected')
        this.stopHeartbeat()

        // 尝试重连
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
          this.reconnect()
        }
      }
    } catch (error) {
      console.error('[WebSocket] Failed to connect:', error)
      this.setStatus('error')
    }
  }

  /**
   * 断开连接
   */
  disconnect() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }

    this.stopHeartbeat()

    if (this.ws) {
      this.ws.close()
      this.ws = null
    }

    this.setStatus('disconnected')
  }

  /**
   * 重新连接
   */
  private reconnect() {
    if (this.reconnectTimer) {
      return
    }

    this.reconnectAttempts++

    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null
      if (this.userId && this.token) {
        this.connect(this.userId, this.token)
      }
    }, this.reconnectDelay)
  }

  /**
   * 发送消息
   */
  send(message: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message))
    } else {
      console.warn('[WebSocket] Cannot send message: not connected')
    }
  }

  /**
   * 注册消息处理器
   */
  on(type: string, handler: MessageHandler) {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, [])
    }
    this.messageHandlers.get(type)!.push(handler)
  }

  /**
   * 移除消息处理器
   */
  off(type: string, handler: MessageHandler) {
    const handlers = this.messageHandlers.get(type)
    if (handlers) {
      const index = handlers.indexOf(handler)
      if (index > -1) {
        handlers.splice(index, 1)
      }
    }
  }

  /**
   * 处理收到的消息
   */
  private handleMessage(message: any) {
    const { type, data } = message

    // 调用注册的处理器
    const handlers = this.messageHandlers.get(type)
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data)
        } catch (error) {
          console.error(`[WebSocket] Handler error for type "${type}":`, error)
        }
      })
    }

    // 默认处理通知消息
    if (type === 'notification') {
      this.showNotification(data)
    }
  }

  /**
   * 显示通知
   */
  private showNotification(data: any) {
    const { title, message } = data

    ElNotification.info({
      title: title,
      message: message,
      duration: 5000,
      position: 'top-right',
    })
  }

  /**
   * 开始心跳
   */
  private heartbeatTimer: NodeJS.Timeout | null = null

  private startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      this.send({ type: 'ping' })
    }, 30000) // 每30秒发送一次心跳
  }

  private stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  /**
   * 设置连接状态
   */
  private setStatus(status: ConnectionStatus) {
    this.status = status
    this.statusHandlers.forEach(handler => handler(status))
  }

  /**
   * 监听连接状态变化
   */
  onStatusChange(handler: (status: ConnectionStatus) => void) {
    this.statusHandlers.push(handler)
  }

  /**
   * 获取当前状态
   */
  getStatus(): ConnectionStatus {
    return this.status
  }

  /**
   * 是否已连接
   */
  isConnected(): boolean {
    return this.status === 'connected'
  }
}

// 导出单例
export const wsManager = new WebSocketManager()


