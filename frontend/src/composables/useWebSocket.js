import { ref, computed, onUnmounted, reactive } from 'vue'
import { websocketService } from '../services/websocketService.js'

/**
 * Vue composable for WebSocket functionality
 * Provides reactive state and methods for real-time job status updates
 * 
 * @param {string} jobId - Optional job ID to connect to immediately
 * @returns {Object} WebSocket state and methods
 */
export function useWebSocket(jobId = null) {
  // Reactive state
  const connected = ref(false)
  const connecting = ref(false)
  const messages = ref([])
  const latestMessage = ref(null)
  const error = ref(null)
  const jobStatus = reactive({
    status: null,
    progress: 0,
    message: '',
    details: null
  })

  // Store cleanup functions
  const cleanupFunctions = []

  /**
   * Connect to WebSocket for a specific job
   * @param {string} id - Job ID to monitor
   * @returns {Promise<void>}
   */
  const connect = async (id) => {
    const targetJobId = id || jobId
    if (!targetJobId) {
      throw new Error('Job ID is required to connect to WebSocket')
    }

    connecting.value = true
    error.value = null

    try {
      await websocketService.connect(targetJobId)
      connected.value = true
      
      // Register message handlers
      registerHandlers()
    } catch (err) {
      error.value = err.message
      throw err
    } finally {
      connecting.value = false
    }
  }

  /**
   * Register all message and connection handlers
   */
  const registerHandlers = () => {
    // Clear any existing handlers
    clearHandlers()

    // Message handlers
    cleanupFunctions.push(
      websocketService.onMessage('status', (data) => {
        jobStatus.status = data.status
        jobStatus.message = data.message || ''
        jobStatus.details = data.details || null
        addMessage({ type: 'status', ...data })
      })
    )

    cleanupFunctions.push(
      websocketService.onMessage('progress', (data) => {
        jobStatus.progress = data.progress || 0
        jobStatus.message = data.message || ''
        addMessage({ type: 'progress', ...data })
      })
    )

    cleanupFunctions.push(
      websocketService.onMessage('complete', (data) => {
        jobStatus.status = 'completed'
        jobStatus.progress = 100
        jobStatus.message = data.message || 'Processing completed'
        jobStatus.details = data.result || null
        addMessage({ type: 'complete', ...data })
      })
    )

    cleanupFunctions.push(
      websocketService.onMessage('error', (data) => {
        jobStatus.status = 'error'
        jobStatus.message = data.message || 'An error occurred'
        error.value = data.error || data.message
        addMessage({ type: 'error', ...data })
      })
    )

    // Generic message handler
    cleanupFunctions.push(
      websocketService.onMessage('message', (data) => {
        addMessage(data)
      })
    )

    // Connection event handlers
    cleanupFunctions.push(
      websocketService.onConnectionEvent('onOpen', () => {
        connected.value = true
        error.value = null
      })
    )

    cleanupFunctions.push(
      websocketService.onConnectionEvent('onClose', () => {
        connected.value = false
      })
    )

    cleanupFunctions.push(
      websocketService.onConnectionEvent('onError', (err) => {
        error.value = 'WebSocket connection error'
        connected.value = false
      })
    )
  }

  /**
   * Add a message to the messages array
   * @param {Object} message
   */
  const addMessage = (message) => {
    const timestampedMessage = {
      ...message,
      timestamp: message.timestamp || Date.now(),
      id: `${Date.now()}-${Math.random()}`
    }
    messages.value.push(timestampedMessage)
    latestMessage.value = timestampedMessage
  }

  /**
   * Send a message through WebSocket
   * @param {Object} data
   * @returns {boolean} Success status
   */
  const send = (data) => {
    return websocketService.send(data)
  }

  /**
   * Disconnect from WebSocket
   */
  const disconnect = () => {
    clearHandlers()
    websocketService.disconnect()
    connected.value = false
    connecting.value = false
  }

  /**
   * Clear all message handlers
   */
  const clearHandlers = () => {
    cleanupFunctions.forEach(cleanup => cleanup())
    cleanupFunctions.length = 0
  }

  /**
   * Clear all messages
   */
  const clearMessages = () => {
    messages.value = []
    latestMessage.value = null
  }

  /**
   * Reconnect to the current job
   */
  const reconnect = async () => {
    const currentState = websocketService.getState()
    if (currentState.jobId) {
      await connect(currentState.jobId)
    }
  }

  // Computed properties
  const isConnected = computed(() => connected.value)
  const isConnecting = computed(() => connecting.value)
  const hasError = computed(() => !!error.value)
  const messageCount = computed(() => messages.value.length)
  
  // Job status computed properties
  const isProcessing = computed(() => 
    jobStatus.status === 'processing' || jobStatus.status === 'running'
  )
  const isCompleted = computed(() => jobStatus.status === 'completed')
  const isFailed = computed(() => jobStatus.status === 'error' || jobStatus.status === 'failed')

  // Auto-connect if jobId provided
  if (jobId) {
    connect(jobId).catch(err => {
      console.error('Failed to auto-connect to WebSocket:', err)
    })
  }

  // Cleanup on unmount
  onUnmounted(() => {
    disconnect()
  })

  return {
    // State
    connected: isConnected,
    connecting: isConnecting,
    messages,
    latestMessage,
    error,
    jobStatus,
    
    // Computed
    hasError,
    messageCount,
    isProcessing,
    isCompleted,
    isFailed,
    
    // Methods
    connect,
    disconnect,
    send,
    reconnect,
    clearMessages,
    
    // Direct service access (for advanced usage)
    service: websocketService
  }
}