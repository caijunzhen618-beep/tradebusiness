/**
 * Logger Utility for Client Frontend
 * Provides logging functionality with console output and localStorage persistence
 */

enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
}

interface LogEntry {
  timestamp: string
  level: string
  message: string
  data?: any
  stack?: string
}

class Logger {
  private logLevel: LogLevel
  private enableConsole: boolean
  private enableStorage: boolean
  private storageKey: string
  private maxStorageLogs: number
  private appName: string

  constructor() {
    // Set log level based on environment
    const isDev = import.meta.env.DEV
    this.logLevel = isDev ? LogLevel.DEBUG : LogLevel.INFO
    this.enableConsole = true
    this.enableStorage = isDev // Only enable storage in dev to avoid filling localStorage
    this.storageKey = 'client_logs'
    this.maxStorageLogs = 500 // Maximum number of logs to keep in storage
    this.appName = 'TradeBusiness-Client'
  }

  /**
   * Format timestamp
   */
  private getTimestamp(): string {
    return new Date().toISOString()
  }

  /**
   * Get log level name
   */
  private getLevelName(level: LogLevel): string {
    switch (level) {
      case LogLevel.DEBUG:
        return 'DEBUG'
      case LogLevel.INFO:
        return 'INFO'
      case LogLevel.WARN:
        return 'WARN'
      case LogLevel.ERROR:
        return 'ERROR'
      default:
        return 'UNKNOWN'
    }
  }

  /**
   * Format log message
   */
  private formatMessage(level: string, message: string): string {
    return `[${this.getTimestamp()}] [${this.appName}] [${level}] ${message}`
  }

  /**
   * Save log to localStorage
   */
  private saveToStorage(entry: LogEntry): void {
    if (!this.enableStorage) return

    try {
      const logs = this.getStoredLogs()
      logs.push(entry)

      // Rotate logs if we exceed the maximum
      if (logs.length > this.maxStorageLogs) {
        logs.splice(0, logs.length - this.maxStorageLogs)
      }

      localStorage.setItem(this.storageKey, JSON.stringify(logs))
    } catch (error) {
      // If localStorage is full, clear old logs and try again
      try {
        localStorage.removeItem(this.storageKey)
        const logs = [entry]
        localStorage.setItem(this.storageKey, JSON.stringify(logs))
      } catch {
        // Ignore if we still can't write
      }
    }
  }

  /**
   * Get logs from localStorage
   */
  private getStoredLogs(): LogEntry[] {
    try {
      const stored = localStorage.getItem(this.storageKey)
      return stored ? JSON.parse(stored) : []
    } catch {
      return []
    }
  }

  /**
   * Core logging method
   */
  private log(level: LogLevel, message: string, data?: any): void {
    // Check if we should log this level
    if (level < this.logLevel) return

    const levelName = this.getLevelName(level)
    const entry: LogEntry = {
      timestamp: this.getTimestamp(),
      level: levelName,
      message,
      data,
    }

    // Console output
    if (this.enableConsole) {
      const formattedMessage = this.formatMessage(levelName, message)

      switch (level) {
        case LogLevel.DEBUG:
          console.debug(formattedMessage, data || '')
          break
        case LogLevel.INFO:
          console.info(formattedMessage, data || '')
          break
        case LogLevel.WARN:
          console.warn(formattedMessage, data || '')
          break
        case LogLevel.ERROR:
          console.error(formattedMessage, data || '')
          break
      }
    }

    // Storage
    this.saveToStorage(entry)
  }

  /**
   * Debug level log
   */
  debug(message: string, data?: any): void {
    this.log(LogLevel.DEBUG, message, data)
  }

  /**
   * Info level log
   */
  info(message: string, data?: any): void {
    this.log(LogLevel.INFO, message, data)
  }

  /**
   * Warning level log
   */
  warn(message: string, data?: any): void {
    this.log(LogLevel.WARN, message, data)
  }

  /**
   * Error level log
   */
  error(message: string, error?: Error | any): void {
    let data: any = error

    // If it's an Error object, extract stack trace
    if (error instanceof Error) {
      data = {
        message: error.message,
        stack: error.stack,
        name: error.name,
      }
    }

    this.log(LogLevel.ERROR, message, data)
  }

  /**
   * Get all stored logs
   */
  getLogs(): LogEntry[] {
    return this.getStoredLogs()
  }

  /**
   * Clear all stored logs
   */
  clearLogs(): void {
    localStorage.removeItem(this.storageKey)
  }

  /**
   * Export logs as JSON string
   */
  exportLogs(): string {
    const logs = this.getStoredLogs()
    return JSON.stringify(logs, null, 2)
  }

  /**
   * Download logs as a file
   */
  downloadLogs(): void {
    const logs = this.exportLogs()
    const blob = new Blob([logs], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `client-logs-${new Date().toISOString()}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  /**
   * Set log level
   */
  setLogLevel(level: LogLevel): void {
    this.logLevel = level
  }

  /**
   * Enable/disable console logging
   */
  setConsoleEnabled(enabled: boolean): void {
    this.enableConsole = enabled
  }

  /**
   * Enable/disable storage logging
   */
  setStorageEnabled(enabled: boolean): void {
    this.enableStorage = enabled
  }
}

// Create singleton instance
const logger = new Logger()

// Export logger instance and LogLevel enum
export default logger
export { LogLevel }
export type { LogEntry }
