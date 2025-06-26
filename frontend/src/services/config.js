/**
 * Service Configuration
 * Centralized configuration for all API services
 */

// Default configuration values
const DEFAULT_CONFIG = {
  apiBaseUrl: 'http://localhost:8000',
  timeout: 30000, // 30 seconds
  maxRetries: 3,
  retryDelay: 1000, // 1 second
  wsReconnectAttempts: 5,
  wsReconnectDelay: 1000,
};

// Environment-based configuration
const config = {
  // API Base URL - can be overridden by environment variable
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || DEFAULT_CONFIG.apiBaseUrl,
  
  // Request timeout
  timeout: parseInt(import.meta.env.VITE_API_TIMEOUT) || DEFAULT_CONFIG.timeout,
  
  // Retry configuration
  maxRetries: parseInt(import.meta.env.VITE_API_MAX_RETRIES) || DEFAULT_CONFIG.maxRetries,
  retryDelay: parseInt(import.meta.env.VITE_API_RETRY_DELAY) || DEFAULT_CONFIG.retryDelay,
  
  // WebSocket configuration
  wsUrl: import.meta.env.VITE_WS_URL || null, // Auto-generated from apiBaseUrl if not provided
  wsReconnectAttempts: parseInt(import.meta.env.VITE_WS_RECONNECT_ATTEMPTS) || DEFAULT_CONFIG.wsReconnectAttempts,
  wsReconnectDelay: parseInt(import.meta.env.VITE_WS_RECONNECT_DELAY) || DEFAULT_CONFIG.wsReconnectDelay,
  
  // Feature flags
  enableWebSocket: import.meta.env.VITE_ENABLE_WEBSOCKET !== 'false', // Default enabled
  enableRetries: import.meta.env.VITE_ENABLE_RETRIES !== 'false', // Default enabled
  enableLogging: import.meta.env.DEV || import.meta.env.VITE_ENABLE_LOGGING === 'true',
  
  // Service-specific settings
  documentIntelligence: {
    maxFileSize: parseInt(import.meta.env.VITE_DOC_MAX_FILE_SIZE) || 50 * 1024 * 1024, // 50MB
    supportedFormats: ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.heif', '.docx', '.xlsx', '.pptx', '.html'],
    pollInterval: parseInt(import.meta.env.VITE_DOC_POLL_INTERVAL) || 2000, // 2 seconds
  },
  
  translation: {
    maxFileSize: parseInt(import.meta.env.VITE_TRANS_MAX_FILE_SIZE) || 40 * 1024 * 1024, // 40MB
    supportedFormats: ['.txt', '.pdf', '.docx', '.xlsx', '.pptx', '.html', '.xml', '.xlf', '.tmx'],
    pollInterval: parseInt(import.meta.env.VITE_TRANS_POLL_INTERVAL) || 2000, // 2 seconds
    maxTextLength: parseInt(import.meta.env.VITE_TRANS_MAX_TEXT_LENGTH) || 50000, // 50k characters
  },
  
  transcription: {
    maxFileSize: parseInt(import.meta.env.VITE_AUDIO_MAX_FILE_SIZE) || 200 * 1024 * 1024, // 200MB
    supportedFormats: ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.wma', '.aac', '.opus', '.webm'],
    pollInterval: parseInt(import.meta.env.VITE_AUDIO_POLL_INTERVAL) || 3000, // 3 seconds
    maxDuration: parseInt(import.meta.env.VITE_AUDIO_MAX_DURATION) || 120 * 60, // 120 minutes
  },
};

// Validation functions
const validateConfig = () => {
  const errors = [];
  
  if (!config.apiBaseUrl) {
    errors.push('API base URL is required');
  }
  
  if (config.timeout < 1000) {
    errors.push('Timeout should be at least 1000ms');
  }
  
  if (config.maxRetries < 0 || config.maxRetries > 10) {
    errors.push('Max retries should be between 0 and 10');
  }
  
  // Validate service-specific settings
  Object.keys(config).forEach(service => {
    if (typeof config[service] === 'object' && config[service] !== null && config[service].maxFileSize) {
      if (config[service].maxFileSize < 1024) {
        errors.push(`${service} max file size should be at least 1KB`);
      }
    }
  });
  
  if (errors.length > 0) {
    console.error('Configuration validation errors:', errors);
    throw new Error(`Invalid configuration: ${errors.join(', ')}`);
  }
};

// Helper functions
const getWebSocketUrl = () => {
  if (config.wsUrl) {
    return config.wsUrl;
  }
  
  // Auto-generate WebSocket URL from API base URL
  return config.apiBaseUrl.replace(/^http/, 'ws') + '/ws';
};

const isDevelopment = () => {
  return import.meta.env.DEV;
};

const isProduction = () => {
  return import.meta.env.PROD;
};

// Environment-specific overrides
if (isDevelopment()) {
  // Development-specific settings
  config.enableLogging = true;
  
  // Shorter timeouts for faster development feedback
  config.documentIntelligence.pollInterval = 1000; // 1 second
  config.translation.pollInterval = 1000; // 1 second
  config.transcription.pollInterval = 2000; // 2 seconds
}

// Validate configuration on import
validateConfig();

// Export configuration
export default config;

// Export helper functions
export {
  getWebSocketUrl,
  isDevelopment,
  isProduction,
  validateConfig,
  DEFAULT_CONFIG,
};

// Export service-specific configs for convenience
export const { 
  documentIntelligence, 
  translation, 
  transcription 
} = config;