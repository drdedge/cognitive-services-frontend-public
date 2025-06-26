<template>
  <Transition
    enter-active-class="transition ease-out duration-300"
    enter-from-class="transform opacity-0 scale-95"
    enter-to-class="transform opacity-100 scale-100"
    leave-active-class="transition ease-in duration-200"
    leave-from-class="transform opacity-100 scale-100"
    leave-to-class="transform opacity-0 scale-95"
  >
    <div v-if="visible" :class="alertClasses">
      <div class="flex">
        <!-- Icon -->
        <div class="flex-shrink-0">
          <svg :class="iconClasses" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path 
              v-if="type === 'error'" 
              stroke-linecap="round" 
              stroke-linejoin="round" 
              stroke-width="2" 
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" 
            />
            <path 
              v-else-if="type === 'warning'" 
              stroke-linecap="round" 
              stroke-linejoin="round" 
              stroke-width="2" 
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" 
            />
            <path 
              v-else-if="type === 'info'" 
              stroke-linecap="round" 
              stroke-linejoin="round" 
              stroke-width="2" 
              d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" 
            />
          </svg>
        </div>

        <!-- Content -->
        <div class="ml-3 flex-1">
          <!-- Title -->
          <h3 v-if="title" :class="titleClasses">
            {{ title }}
          </h3>

          <!-- Message -->
          <div :class="messageClasses">
            <p v-if="typeof error === 'string'">{{ error }}</p>
            <p v-else-if="error?.message">{{ error.message }}</p>
            <p v-else>{{ defaultMessage }}</p>
          </div>

          <!-- Details (if error object has additional info) -->
          <div v-if="showDetails && errorDetails" class="mt-2">
            <details class="text-sm">
              <summary class="cursor-pointer font-medium hover:underline">
                Show details
              </summary>
              <pre class="mt-2 text-xs bg-black bg-opacity-5 p-2 rounded overflow-x-auto">{{ errorDetails }}</pre>
            </details>
          </div>

          <!-- Actions -->
          <div v-if="showRetry || dismissible" class="mt-4 flex items-center space-x-3">
            <button
              v-if="showRetry"
              @click="$emit('retry')"
              :class="retryButtonClasses"
            >
              Try Again
            </button>
            <button
              v-if="dismissible"
              @click="handleDismiss"
              :class="dismissButtonClasses"
            >
              Dismiss
            </button>
          </div>
        </div>

        <!-- Close button (alternative to dismiss button) -->
        <div v-if="dismissible && !showRetry" class="ml-auto pl-3">
          <button
            @click="handleDismiss"
            :class="closeButtonClasses"
          >
            <span class="sr-only">Dismiss</span>
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  error: {
    type: [String, Object, Error],
    default: null
  },
  type: {
    type: String,
    default: 'error',
    validator: (value) => ['error', 'warning', 'info'].includes(value)
  },
  title: {
    type: String,
    default: null
  },
  dismissible: {
    type: Boolean,
    default: true
  },
  showRetry: {
    type: Boolean,
    default: false
  },
  showDetails: {
    type: Boolean,
    default: true
  },
  autoDismiss: {
    type: Number,
    default: null // milliseconds
  }
})

const emit = defineEmits(['dismiss', 'retry'])

// State
const visible = ref(true)
let dismissTimer = null

// Computed
const defaultMessage = computed(() => {
  const messages = {
    error: 'An error occurred. Please try again.',
    warning: 'Please review the warning message.',
    info: 'Information message.'
  }
  return messages[props.type]
})

const errorDetails = computed(() => {
  if (!props.error || typeof props.error === 'string') return null
  
  // Extract useful details from error object
  const details = {}
  
  if (props.error.code) details.code = props.error.code
  if (props.error.status) details.status = props.error.status
  if (props.error.statusText) details.statusText = props.error.statusText
  if (props.error.response) details.response = props.error.response
  if (props.error.stack && process.env.NODE_ENV === 'development') {
    details.stack = props.error.stack
  }
  
  return Object.keys(details).length > 0 ? JSON.stringify(details, null, 2) : null
})

// Alert styling based on type
const alertClasses = computed(() => {
  const baseClasses = 'rounded-lg p-4 shadow-sm border'
  const typeClasses = {
    error: 'bg-red-50 border-red-200',
    warning: 'bg-[#ffc107] bg-opacity-10 border-[#ffc107]',
    info: 'bg-blue-50 border-blue-200'
  }
  return `${baseClasses} ${typeClasses[props.type]}`
})

const iconClasses = computed(() => {
  const baseClasses = 'h-5 w-5'
  const colorClasses = {
    error: 'text-red-400',
    warning: 'text-[#ffc107]',
    info: 'text-blue-400'
  }
  return `${baseClasses} ${colorClasses[props.type]}`
})

const titleClasses = computed(() => {
  const baseClasses = 'text-sm font-medium'
  const colorClasses = {
    error: 'text-red-800',
    warning: 'text-yellow-800',
    info: 'text-blue-800'
  }
  return `${baseClasses} ${colorClasses[props.type]}`
})

const messageClasses = computed(() => {
  const baseClasses = 'text-sm'
  const colorClasses = {
    error: 'text-red-700',
    warning: 'text-yellow-700',
    info: 'text-blue-700'
  }
  const marginClass = props.title ? 'mt-1' : ''
  return `${baseClasses} ${colorClasses[props.type]} ${marginClass}`
})

const retryButtonClasses = computed(() => {
  const baseClasses = 'text-sm font-medium px-3 py-1.5 rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2'
  const typeClasses = {
    error: 'bg-red-100 text-red-800 hover:bg-red-200 focus:ring-red-500',
    warning: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200 focus:ring-yellow-500',
    info: 'bg-blue-100 text-blue-800 hover:bg-blue-200 focus:ring-blue-500'
  }
  return `${baseClasses} ${typeClasses[props.type]}`
})

const dismissButtonClasses = computed(() => {
  const baseClasses = 'text-sm font-medium px-3 py-1.5 rounded-md transition-colors focus:outline-none'
  const typeClasses = {
    error: 'text-red-600 hover:text-red-500',
    warning: 'text-yellow-600 hover:text-yellow-500',
    info: 'text-blue-600 hover:text-blue-500'
  }
  return `${baseClasses} ${typeClasses[props.type]}`
})

const closeButtonClasses = computed(() => {
  const baseClasses = '-m-1.5 p-1.5 inline-flex rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors'
  const typeClasses = {
    error: 'text-red-400 hover:bg-red-100 focus:ring-red-500',
    warning: 'text-yellow-400 hover:bg-yellow-100 focus:ring-yellow-500',
    info: 'text-blue-400 hover:bg-blue-100 focus:ring-blue-500'
  }
  return `${baseClasses} ${typeClasses[props.type]}`
})

// Methods
const handleDismiss = () => {
  visible.value = false
  emit('dismiss')
}

// Auto dismiss
const setupAutoDismiss = () => {
  if (props.autoDismiss && props.autoDismiss > 0) {
    dismissTimer = setTimeout(() => {
      handleDismiss()
    }, props.autoDismiss)
  }
}

// Watch for error changes
watch(() => props.error, (newError) => {
  if (newError) {
    visible.value = true
    setupAutoDismiss()
  }
}, { immediate: true })

// Cleanup
const cleanup = () => {
  if (dismissTimer) {
    clearTimeout(dismissTimer)
  }
}

// Lifecycle
import { onUnmounted } from 'vue'
onUnmounted(() => {
  cleanup()
})
</script>

<style scoped>
/* Additional styles if needed */
</style>