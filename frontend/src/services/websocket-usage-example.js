/**
 * Example usage of WebSocket functionality in Vue components
 * This file demonstrates how to integrate the websocketService and useWebSocket composable
 */

// Example 1: Using the composable in a Vue component
/*
<template>
  <div>
    <div v-if="connecting">Connecting to real-time updates...</div>
    <div v-else-if="connected">
      <span class="text-green-500">Connected</span>
      <div>Status: {{ jobStatus.status }}</div>
      <div>Progress: {{ jobStatus.progress }}%</div>
      <div>{{ jobStatus.message }}</div>
    </div>
    <div v-else-if="hasError" class="text-red-500">
      Connection error: {{ error }}
    </div>
    
    <button v-if="!connected && !connecting" @click="connectToJob">
      Connect to Job Updates
    </button>
  </div>
</template>

<script setup>
import { useWebSocket } from '@/composables/useWebSocket'

// Option 1: Auto-connect with job ID
const jobId = 'job-123-456'
const { 
  connected, 
  connecting, 
  jobStatus, 
  hasError, 
  error,
  isProcessing,
  isCompleted,
  isFailed 
} = useWebSocket(jobId)

// Option 2: Manual connection
const ws = useWebSocket()

async function connectToJob() {
  try {
    await ws.connect('job-789-012')
  } catch (error) {
    console.error('Failed to connect:', error)
  }
}

// Watch for completion
watch(isCompleted, (completed) => {
  if (completed) {
    console.log('Job completed!', ws.jobStatus.details)
    // Handle completion, e.g., download results
  }
})
</script>
*/

// Example 2: Using WebSocket in Document Intelligence view
/*
import { useWebSocket } from '@/composables/useWebSocket'
import { useDocumentIntelligence } from '@/composables/useDocumentIntelligence'

export default {
  setup() {
    const { processDocument } = useDocumentIntelligence()
    const ws = useWebSocket()
    
    async function handleFileUpload(file) {
      try {
        // Start document processing
        const { jobId } = await processDocument(file)
        
        // Connect WebSocket to monitor progress
        await ws.connect(jobId)
        
        // The websocket will automatically update jobStatus
        // which can be used in the template for real-time updates
      } catch (error) {
        console.error('Processing failed:', error)
      }
    }
    
    return {
      handleFileUpload,
      jobStatus: ws.jobStatus,
      isProcessing: ws.isProcessing,
      progress: computed(() => ws.jobStatus.progress)
    }
  }
}
*/

// Example 3: Direct service usage (for advanced scenarios)
/*
import { websocketService } from '@/services/websocketService'

// Connect to a job
await websocketService.connect('job-123')

// Register custom message handlers
const unsubscribe = websocketService.onMessage('custom-event', (data) => {
  console.log('Custom event received:', data)
})

// Send custom messages
websocketService.send({
  type: 'custom-request',
  data: { action: 'get-details' }
})

// Check connection state
const state = websocketService.getState()
console.log('Connected:', state.connected)
console.log('Job ID:', state.jobId)

// Clean up when done
unsubscribe()
websocketService.disconnect()
*/

// Example 4: Integration with ProcessingStatus component
/*
<template>
  <ProcessingStatus
    :status="jobStatus.status"
    :progress="jobStatus.progress"
    :message="jobStatus.message"
    :connected="connected"
    @retry="reconnect"
  />
</template>

<script setup>
import { useWebSocket } from '@/composables/useWebSocket'
import ProcessingStatus from '@/components/ProcessingStatus.vue'

const props = defineProps({
  jobId: String
})

const { 
  connected, 
  jobStatus, 
  reconnect 
} = useWebSocket(props.jobId)
</script>
*/

// Example 5: Message history and debugging
/*
const { messages, latestMessage, messageCount } = useWebSocket(jobId)

// Display message history
watch(latestMessage, (message) => {
  if (message) {
    console.log(`[${message.type}] ${message.message}`)
  }
})

// Access all messages
console.log(`Total messages received: ${messageCount.value}`)
messages.value.forEach(msg => {
  console.log(msg.timestamp, msg.type, msg)
})
*/