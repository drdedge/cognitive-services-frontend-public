<template>
  <div class="loading-spinner-container flex flex-col items-center justify-center">
    <!-- Spinner -->
    <div :class="spinnerClasses" :style="spinnerStyles">
      <svg class="animate-spin" fill="none" viewBox="0 0 24 24">
        <circle 
          class="opacity-25" 
          cx="12" 
          cy="12" 
          r="10" 
          stroke="currentColor" 
          stroke-width="4"
        ></circle>
        <path 
          class="opacity-75" 
          fill="currentColor" 
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>
    </div>

    <!-- Loading Text -->
    <p v-if="message" :class="messageClasses">
      {{ message }}
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: {
    type: String,
    default: 'medium',
    validator: (value) => ['small', 'medium', 'large'].includes(value)
  },
  color: {
    type: String,
    default: 'primary' // primary, secondary, white, custom
  },
  message: {
    type: String,
    default: ''
  },
  customColor: {
    type: String,
    default: null
  }
})

// Size configurations
const sizeConfig = {
  small: {
    spinner: 'h-6 w-6',
    text: 'text-xs mt-2'
  },
  medium: {
    spinner: 'h-10 w-10',
    text: 'text-sm mt-3'
  },
  large: {
    spinner: 'h-16 w-16',
    text: 'text-base mt-4'
  }
}

// Color configurations
const colorConfig = {
  primary: 'text-[#4F78AB]',
  secondary: 'text-gray-600',
  white: 'text-white',
  custom: ''
}

// Computed properties
const spinnerClasses = computed(() => {
  const size = sizeConfig[props.size].spinner
  const color = props.color === 'custom' ? '' : colorConfig[props.color]
  return `${size} ${color}`
})

const spinnerStyles = computed(() => {
  if (props.color === 'custom' && props.customColor) {
    return { color: props.customColor }
  }
  return {}
})

const messageClasses = computed(() => {
  const size = sizeConfig[props.size].text
  const color = props.color === 'white' ? 'text-white' : 'text-gray-600'
  return `${size} ${color}`
})
</script>

<style scoped>
/* Ensure smooth animation */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>