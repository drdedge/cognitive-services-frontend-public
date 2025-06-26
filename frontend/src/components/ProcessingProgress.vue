<template>
  <div v-if="status !== 'idle'" class="mt-8 bg-white shadow rounded-lg">
    <div class="px-6 py-4 border-b border-gray-200">
      <h3 class="text-lg font-medium text-gray-900">Processing Status</h3>
    </div>
    
    <div class="p-6">
      <!-- Progress Bar -->
      <div class="mb-4">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-gray-700">Progress</span>
          <span class="text-sm text-gray-500">{{ progress }}%</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-2.5">
          <div 
            class="h-2.5 rounded-full transition-all duration-300"
            :class="{
              'bg-primary': status === 'processing',
              'bg-success': status === 'completed',
              'bg-error': status === 'error'
            }"
            :style="{ width: `${progress}%` }"
          ></div>
        </div>
      </div>

      <!-- Status Message -->
      <div class="flex items-center">
        <div v-if="status === 'processing'" class="flex items-center">
          <svg class="animate-spin h-5 w-5 text-primary mr-3" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span class="text-sm text-gray-700">{{ message || 'Processing...' }}</span>
        </div>
        
        <div v-else-if="status === 'completed'" class="flex items-center">
          <svg class="h-5 w-5 text-success mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="text-sm text-success">{{ message || 'Processing complete!' }}</span>
        </div>
        
        <div v-else-if="status === 'error'" class="flex items-center">
          <svg class="h-5 w-5 text-error mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="text-sm text-error">{{ message || 'An error occurred' }}</span>
        </div>
      </div>

      <!-- Additional Details -->
      <div v-if="details" class="mt-4 text-sm text-gray-600">
        <p>{{ details }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  progress: {
    type: Number,
    default: 0
  },
  message: {
    type: String,
    default: ''
  },
  status: {
    type: String,
    default: 'idle',
    validator: (value) => ['idle', 'processing', 'completed', 'error'].includes(value)
  },
  details: {
    type: String,
    default: null
  }
})
</script>