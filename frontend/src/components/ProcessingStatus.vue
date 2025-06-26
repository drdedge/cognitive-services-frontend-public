<template>
  <div class="processing-status bg-white rounded-lg shadow-sm border border-gray-200">
    <!-- Header -->
    <div class="px-6 py-4 border-b border-gray-200">
      <div class="flex items-center justify-between">
        <h3 class="text-lg font-semibold text-[#3B5781]">Processing Status</h3>
        <div v-if="jobId" class="text-sm text-gray-500">
          Job ID: <code class="font-mono bg-gray-100 px-2 py-0.5 rounded">{{ jobId }}</code>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="p-6 space-y-6">
      <!-- Progress Bar -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-medium text-gray-700">Progress</span>
          <span class="text-sm text-gray-500">{{ progress }}%</span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div 
            class="h-full rounded-full transition-all duration-500 ease-out relative overflow-hidden"
            :class="{
              'bg-[#4F78AB]': status === 'processing',
              'bg-[#28a745]': status === 'completed',
              'bg-red-500': status === 'error',
              'bg-gray-400': status === 'cancelled'
            }"
            :style="{ width: `${progress}%` }"
          >
            <!-- Animated stripes for processing state -->
            <div v-if="status === 'processing'" class="stripe-animation absolute inset-0"></div>
          </div>
        </div>
      </div>

      <!-- Current Stage -->
      <div class="flex items-center space-x-3">
        <!-- Status Icon -->
        <div class="flex-shrink-0">
          <!-- Processing -->
          <svg v-if="status === 'processing'" class="animate-spin h-6 w-6 text-[#4F78AB]" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" 
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          
          <!-- Completed -->
          <svg v-else-if="status === 'completed'" class="h-6 w-6 text-[#28a745]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          
          <!-- Error -->
          <svg v-else-if="status === 'error'" class="h-6 w-6 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          
          <!-- Cancelled -->
          <svg v-else-if="status === 'cancelled'" class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>

        <!-- Stage Information -->
        <div class="flex-1">
          <p class="text-sm font-medium text-[#3B5781]">{{ currentStage }}</p>
          <p v-if="stageDetails" class="text-xs text-gray-500 mt-0.5">{{ stageDetails }}</p>
        </div>
      </div>

      <!-- Time Information -->
      <div class="grid grid-cols-2 gap-4 pt-4 border-t border-gray-100">
        <!-- Elapsed Time -->
        <div>
          <p class="text-xs text-gray-500 uppercase tracking-wide">Elapsed Time</p>
          <p class="text-sm font-medium text-[#3B5781] mt-1">{{ formattedElapsedTime }}</p>
        </div>
        
        <!-- Estimated Time Remaining -->
        <div v-if="status === 'processing' && estimatedTimeRemaining">
          <p class="text-xs text-gray-500 uppercase tracking-wide">Est. Time Remaining</p>
          <p class="text-sm font-medium text-[#3B5781] mt-1">{{ formattedEstimatedTime }}</p>
        </div>
      </div>

      <!-- Actions -->
      <div class="flex items-center justify-between pt-4 border-t border-gray-100">
        <!-- Cancel Button -->
        <button
          v-if="status === 'processing' && !disableCancel"
          @click="handleCancel"
          class="px-4 py-2 text-sm font-medium text-red-600 bg-red-50 rounded-md hover:bg-red-100 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
        >
          Cancel Processing
        </button>
        
        <!-- Retry Button -->
        <button
          v-else-if="status === 'error'"
          @click="handleRetry"
          class="px-4 py-2 text-sm font-medium text-white bg-[#4F78AB] rounded-md hover:bg-blue-700 transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#4F78AB]"
        >
          Retry Processing
        </button>

        <!-- Service Info -->
        <div v-if="service" class="text-sm text-gray-500 ml-auto">
          Service: <span class="font-medium">{{ service.name }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  jobId: {
    type: String,
    required: true
  },
  service: {
    type: Object,
    default: null
  },
  status: {
    type: String,
    default: 'processing',
    validator: (value) => ['processing', 'completed', 'error', 'cancelled'].includes(value)
  },
  progress: {
    type: Number,
    default: 0,
    validator: (value) => value >= 0 && value <= 100
  },
  currentStage: {
    type: String,
    default: 'Initializing...'
  },
  stageDetails: {
    type: String,
    default: null
  },
  startTime: {
    type: Date,
    default: () => new Date()
  },
  estimatedDuration: {
    type: Number, // in seconds
    default: null
  },
  disableCancel: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['cancel', 'retry'])

// State
const currentTime = ref(new Date())
let timer = null

// Computed
const elapsedTime = computed(() => {
  return Math.floor((currentTime.value - props.startTime) / 1000) // in seconds
})

const formattedElapsedTime = computed(() => {
  return formatTime(elapsedTime.value)
})

const estimatedTimeRemaining = computed(() => {
  if (!props.estimatedDuration || props.progress === 0) return null
  
  const estimatedTotal = (elapsedTime.value / props.progress) * 100
  const remaining = estimatedTotal - elapsedTime.value
  
  return Math.max(0, Math.floor(remaining))
})

const formattedEstimatedTime = computed(() => {
  if (!estimatedTimeRemaining.value) return 'Calculating...'
  return formatTime(estimatedTimeRemaining.value)
})

// Methods
const formatTime = (seconds) => {
  if (seconds < 60) {
    return `${seconds}s`
  } else if (seconds < 3600) {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}m ${secs}s`
  } else {
    const hours = Math.floor(seconds / 3600)
    const mins = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${mins}m`
  }
}

const handleCancel = () => {
  if (confirm('Are you sure you want to cancel this processing job?')) {
    emit('cancel', props.jobId)
  }
}

const handleRetry = () => {
  emit('retry', props.jobId)
}

// Update current time every second
const updateTime = () => {
  currentTime.value = new Date()
}

// Lifecycle
onMounted(() => {
  timer = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})
</script>

<style scoped>
/* Animated stripes for progress bar */
@keyframes stripe-animation {
  0% {
    background-position: 0 0;
  }
  100% {
    background-position: 40px 0;
  }
}

.stripe-animation {
  background-image: linear-gradient(
    45deg,
    rgba(255, 255, 255, 0.15) 25%,
    transparent 25%,
    transparent 50%,
    rgba(255, 255, 255, 0.15) 50%,
    rgba(255, 255, 255, 0.15) 75%,
    transparent 75%,
    transparent
  );
  background-size: 40px 40px;
  animation: stripe-animation 1s linear infinite;
}
</style>