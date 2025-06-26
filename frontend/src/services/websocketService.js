import { getWebSocketUrl } from './config';
import appConfig from './config';

/**
 * WebSocket Service
 * Handles real-time communication for job status updates
 */
class WebSocketService {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = appConfig.wsReconnectAttempts;
    this.reconnectDelay = appConfig.wsReconnectDelay;
    this.listeners = new Map();
    this.jobRooms = new Set();
    this.isConnecting = false;
    this.connectionPromise = null;
  }

  /**
   * Get WebSocket URL from configuration
   */
  getWebSocketUrl(clientId = null) {
    const baseUrl = getWebSocketUrl();
    return clientId ? `${baseUrl}/${clientId}` : baseUrl;
  }

  /**
   * Connect to WebSocket server
   * @param {string} clientId - Optional client ID for direct connection
   * @returns {Promise<void>}
   */
  async connect(clientId = null) {
    // If already connected or connecting, return existing promise
    if (this.ws?.readyState === WebSocket.OPEN) {
      return Promise.resolve();
    }

    if (this.isConnecting && this.connectionPromise) {
      return this.connectionPromise;
    }

    this.isConnecting = true;

    this.connectionPromise = new Promise((resolve, reject) => {
      try {
        const wsUrl = this.getWebSocketUrl(clientId);
        console.log('[WebSocket] Connecting to', wsUrl);
        
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log('[WebSocket] Connected');
          this.reconnectAttempts = 0;
          this.isConnecting = false;
          
          // If no client ID in URL, send identification
          if (!clientId) {
            this.sendMessage('identify', { client_id: 'frontend-client' });
          }
          
          // Rejoin all job rooms
          this.jobRooms.forEach(jobId => {
            this.sendMessage('subscribe', { task_id: jobId });
          });

          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error('[WebSocket] Error parsing message:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('[WebSocket] Error:', error);
          this.isConnecting = false;
          reject(error);
        };

        this.ws.onclose = (event) => {
          console.log('[WebSocket] Disconnected', event);
          this.isConnecting = false;
          
          // Attempt to reconnect
          if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
            console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
            
            setTimeout(() => {
              this.connect().catch(console.error);
            }, delay);
          } else {
            console.error('[WebSocket] Max reconnection attempts reached');
          }
        };
      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });

    return this.connectionPromise;
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.listeners.clear();
    this.jobRooms.clear();
    this.reconnectAttempts = 0;
  }

  /**
   * Send message to server
   * @param {string} type - Message type
   * @param {Object} data - Message data
   */
  sendMessage(type, data) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, data }));
    } else {
      console.warn('[WebSocket] Not connected, unable to send message');
      // Try to reconnect
      this.connect().then(() => {
        if (this.ws?.readyState === WebSocket.OPEN) {
          this.ws.send(JSON.stringify({ type, data }));
        }
      }).catch(console.error);
    }
  }

  /**
   * Handle incoming messages
   * @param {Object} message - Message from server
   */
  handleMessage(message) {
    const { type, job_id, task_id, progress, data, status, error } = message;
    
    // Use job_id if available, fallback to task_id for backward compatibility
    const jobId = job_id || task_id;

    switch (type) {
      case 'connection_established':
      case 'connected':
        console.log('[WebSocket] Connection confirmed:', message);
        break;
        
      case 'job_update':
        // Handle job status updates from backend
        if (jobId) {
          const updateData = {
            type: 'job_update',
            job_id: jobId,
            status: status,
            progress: progress || {},
            error: error
          };
          
          // Forward the entire message to listeners
          this.notifyListeners(jobId, '*', updateData);
          
          // Also notify specific status listeners
          if (status === 'processing' && progress) {
            this.notifyListeners(jobId, 'progress', {
              task_id: jobId,
              progress: progress.progress_percentage || 0,
              message: progress.message || progress.current_step,
              data: updateData
            });
          } else if (status === 'failed' && error) {
            this.notifyListeners(jobId, 'error', {
              task_id: jobId,
              error: error,
              data: updateData
            });
            this.leaveRoom(jobId);
          }
        }
        break;
        
      case 'job_completed':
        // Handle job completion from backend
        if (jobId) {
          const completionData = {
            type: 'job_completed',
            job_id: jobId,
            results_url: message.results_url,
            final_cost: message.final_cost,
            processing_time_seconds: message.processing_time_seconds,
            data: message.data
          };
          
          // Notify all listeners
          this.notifyListeners(jobId, '*', completionData);
          this.notifyListeners(jobId, 'completed', completionData);
          
          // Clean up
          this.leaveRoom(jobId);
        }
        break;
        
      case 'progress':
        // Legacy progress message format
        this.notifyListeners(jobId, 'progress', {
          task_id: jobId,
          progress,
          message: message.message,
          data
        });
        
        // Check if completed
        if (progress === 100) {
          this.notifyListeners(jobId, 'completed', message);
          this.leaveRoom(jobId);
        }
        break;
      
      case 'error':
        console.error('[WebSocket] Server error:', message);
        this.notifyListeners(jobId, 'error', message);
        this.leaveRoom(jobId);
        break;
      
      case 'ping':
      case 'pong':
        // Handle ping/pong
        console.log('[WebSocket] Ping/Pong received');
        break;
      
      default:
        console.log('[WebSocket] Message received:', type, message);
        // Forward unknown messages to listeners in case they want to handle them
        if (jobId) {
          this.notifyListeners(jobId, '*', message);
        }
    }
  }

  /**
   * Notify listeners for a specific job
   * @param {string} jobId - Job ID
   * @param {string} event - Event type
   * @param {Object} data - Event data
   */
  notifyListeners(jobId, event, data) {
    const jobListeners = this.listeners.get(jobId);
    if (jobListeners) {
      jobListeners.forEach(listener => {
        if (listener.event === event || listener.event === '*') {
          try {
            listener.callback(data);
          } catch (error) {
            console.error('[WebSocket] Listener error:', error);
          }
        }
      });
    }
  }

  /**
   * Join a job room for updates
   * @param {string} jobId - Job ID to monitor
   * @returns {Promise<void>}
   */
  async joinRoom(jobId) {
    // Connect with job ID in the URL path as expected by backend
    await this.connect(jobId);
    this.jobRooms.add(jobId);
    // Backend doesn't require explicit subscribe message when connected with job_id in URL
    // But send it anyway for compatibility
    this.sendMessage('subscribe', { job_id: jobId, task_id: jobId });
  }

  /**
   * Leave a job room
   * @param {string} jobId - Job ID to stop monitoring
   */
  leaveRoom(jobId) {
    this.jobRooms.delete(jobId);
    this.listeners.delete(jobId);
    // Note: Backend doesn't have unsubscribe, connection will close when job completes
  }

  /**
   * Subscribe to job updates
   * @param {string} jobId - Job ID to monitor
   * @param {string} event - Event type ('status', 'progress', 'completed', 'failed', 'error', '*')
   * @param {Function} callback - Callback function
   * @returns {Function} Unsubscribe function
   */
  subscribe(jobId, event, callback) {
    // Ensure we're in the room
    this.joinRoom(jobId);

    // Add listener
    if (!this.listeners.has(jobId)) {
      this.listeners.set(jobId, []);
    }
    
    const listener = { event, callback };
    this.listeners.get(jobId).push(listener);

    // Return unsubscribe function
    return () => {
      const jobListeners = this.listeners.get(jobId);
      if (jobListeners) {
        const index = jobListeners.indexOf(listener);
        if (index > -1) {
          jobListeners.splice(index, 1);
        }
        
        // If no more listeners for this job, leave the room
        if (jobListeners.length === 0) {
          this.leaveRoom(jobId);
        }
      }
    };
  }

  /**
   * Subscribe to all events for a job
   * @param {string} jobId - Job ID to monitor
   * @param {Function} callback - Callback function
   * @returns {Function} Unsubscribe function
   */
  subscribeToAll(jobId, callback) {
    return this.subscribe(jobId, '*', callback);
  }

  /**
   * Get connection state
   * @returns {string} Connection state
   */
  getState() {
    if (!this.ws) return 'DISCONNECTED';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'CONNECTING';
      case WebSocket.OPEN:
        return 'CONNECTED';
      case WebSocket.CLOSING:
        return 'CLOSING';
      case WebSocket.CLOSED:
        return 'DISCONNECTED';
      default:
        return 'UNKNOWN';
    }
  }

  /**
   * Check if connected
   * @returns {boolean} True if connected
   */
  isConnected() {
    return this.ws?.readyState === WebSocket.OPEN;
  }
}

// Export singleton instance
export default new WebSocketService();

// Export class for testing purposes
export { WebSocketService };