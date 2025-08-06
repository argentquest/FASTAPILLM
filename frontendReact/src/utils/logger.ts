/**
 * Frontend Logger Utility
 * Provides structured logging for the React application
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
  timestamp: string;
  level: LogLevel;
  message: string;
  data?: any;
  component?: string;
  userId?: string;
  sessionId?: string;
}

class Logger {
  private sessionId: string;
  private isDevelopment: boolean;
  private logs: LogEntry[] = [];

  constructor() {
    this.sessionId = this.generateSessionId();
    this.isDevelopment = process.env.NODE_ENV === 'development';
    
    // Log session start
    this.info('Frontend session started', { sessionId: this.sessionId });
  }

  private generateSessionId(): string {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }

  private log(level: LogLevel, message: string, data?: any, component?: string): void {
    const entry: LogEntry = {
      timestamp: new Date().toISOString(),
      level,
      message,
      data,
      component,
      sessionId: this.sessionId,
    };

    // Store in memory (limited to last 1000 entries)
    this.logs.push(entry);
    if (this.logs.length > 1000) {
      this.logs.shift();
    }

    // Console output with styling
    const emoji = {
      debug: '🔍',
      info: 'ℹ️',
      warn: '⚠️',
      error: '❌'
    }[level];

    if (this.isDevelopment || level !== 'debug') {
      const style = {
        debug: 'color: #6b7280',
        info: 'color: #3b82f6', 
        warn: 'color: #f59e0b',
        error: 'color: #ef4444; font-weight: bold'
      }[level];

      console.groupCollapsed(`%c${emoji} [${level.toUpperCase()}] ${component || 'App'}: ${message}`, style);
      console.log(`%c${entry.timestamp}`, 'color: #9ca3af; font-size: 0.8em');
      if (data) {
        console.log('Data:', data);
      }
      console.log(`%cSession: ${this.sessionId}`, 'color: #9ca3af; font-size: 0.8em');
      console.groupEnd();
    }

    // Send to backend in production (optional)
    if (!this.isDevelopment && level === 'error') {
      this.sendToBackend(entry);
    }
  }

  private async sendToBackend(entry: LogEntry): Promise<void> {
    try {
      await fetch('/api/frontend-logs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(entry),
      });
    } catch (error) {
      console.error('Failed to send log to backend:', error);
    }
  }

  // Public methods
  debug(message: string, data?: any, component?: string): void {
    this.log('debug', message, data, component);
  }

  info(message: string, data?: any, component?: string): void {
    this.log('info', message, data, component);
  }

  warn(message: string, data?: any, component?: string): void {
    this.log('warn', message, data, component);
  }

  error(message: string, data?: any, component?: string): void {
    this.log('error', message, data, component);
  }

  // Component-specific loggers
  component(name: string) {
    return {
      debug: (message: string, data?: any) => this.debug(message, data, name),
      info: (message: string, data?: any) => this.info(message, data, name),
      warn: (message: string, data?: any) => this.warn(message, data, name),
      error: (message: string, data?: any) => this.error(message, data, name),
    };
  }

  // User action tracking
  userAction(action: string, data?: any, component?: string): void {
    this.info(`User Action: ${action}`, data, component);
  }

  // Performance tracking
  performance(name: string, duration: number, component?: string): void {
    this.info(`Performance: ${name}`, { duration: `${duration}ms` }, component);
  }

  // Get logs for debugging
  getLogs(level?: LogLevel): LogEntry[] {
    if (level) {
      return this.logs.filter(log => log.level === level);
    }
    return [...this.logs];
  }

  // Export logs
  exportLogs(): string {
    return JSON.stringify(this.logs, null, 2);
  }

  // Clear logs
  clearLogs(): void {
    this.logs = [];
    this.info('Logs cleared');
  }
}

// Create singleton instance
const logger = new Logger();

export default logger;

// Hook version for React components
export const useLogger = (componentName: string) => {
  return logger.component(componentName);
};