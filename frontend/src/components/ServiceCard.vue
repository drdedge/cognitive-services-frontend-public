<template>
  <div
    @click="handleClick"
    :class="[
      'service-card relative p-6 rounded-lg border-2 transition-all duration-200 cursor-pointer',
      isSelected 
        ? 'border-[#4F78AB] bg-blue-50 shadow-lg scale-[1.02]' 
        : 'border-gray-200 bg-white hover:border-gray-300 hover:shadow-md hover:scale-[1.01]',
      disabled ? 'opacity-50 cursor-not-allowed' : ''
    ]"
    :disabled="disabled"
  >
    <!-- Selection Indicator -->
    <div v-if="isSelected" class="absolute top-3 right-3">
      <div class="h-6 w-6 bg-[#4F78AB] rounded-full flex items-center justify-center">
        <svg class="h-4 w-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
        </svg>
      </div>
    </div>

    <!-- Service Icon -->
    <div class="mb-4">
      <!-- Custom icon slot -->
      <div v-if="$slots.icon" class="service-icon">
        <slot name="icon"></slot>
      </div>
      <!-- Icon from prop -->
      <div v-else-if="service.icon" class="service-icon">
        <!-- SVG icon -->
        <div v-if="service.icon.includes('<svg')" v-html="service.icon" class="h-12 w-12 text-[#4F78AB]"></div>
        <!-- Image URL -->
        <img v-else-if="service.icon.startsWith('http') || service.icon.startsWith('/')" 
             :src="service.icon" 
             :alt="`${service.name} icon`"
             class="h-12 w-12 object-contain">
        <!-- Icon class (for icon fonts) -->
        <i v-else :class="service.icon" class="text-4xl text-[#4F78AB]"></i>
      </div>
      <!-- Default icon -->
      <div v-else>
        <svg class="h-12 w-12 text-[#4F78AB]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" 
                d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
        </svg>
      </div>
    </div>

    <!-- Service Info -->
    <div class="space-y-2">
      <h3 class="text-lg font-semibold text-[#3B5781]">
        {{ service.name }}
      </h3>
      <p class="text-sm text-gray-600 leading-relaxed">
        {{ service.description }}
      </p>
    </div>

    <!-- Additional Info (if provided) -->
    <div v-if="service.features || service.price" class="mt-4 pt-4 border-t border-gray-100">
      <!-- Features List -->
      <ul v-if="service.features" class="space-y-1">
        <li v-for="(feature, index) in service.features" :key="index" 
            class="flex items-start text-sm text-gray-500">
          <svg class="h-4 w-4 text-[#28a745] mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <span>{{ feature }}</span>
        </li>
      </ul>
      
      <!-- Price Info -->
      <div v-if="service.price" class="mt-3 text-sm text-gray-500">
        <span class="font-medium">Starting at:</span> {{ service.price }}
      </div>
    </div>

    <!-- Hover Overlay Effect -->
    <div 
      class="absolute inset-0 bg-gradient-to-br from-[#4F78AB] to-blue-600 opacity-0 rounded-lg transition-opacity duration-200"
      :class="{ 'hover:opacity-5': !disabled && !isSelected }"
    ></div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  service: {
    type: Object,
    required: true,
    validator: (service) => {
      return service.id && service.name && service.description
    }
  },
  selected: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['select'])

// Computed
const isSelected = computed(() => props.selected)

// Methods
const handleClick = () => {
  if (!props.disabled) {
    emit('select', props.service)
  }
}
</script>

<style scoped>
.service-card {
  transform-origin: center;
}

.service-icon :deep(svg) {
  width: 3rem;
  height: 3rem;
}

/* Ensure consistent icon colors */
.service-icon :deep(svg path),
.service-icon :deep(svg circle),
.service-icon :deep(svg rect),
.service-icon :deep(svg polygon) {
  stroke: #4F78AB;
}

.service-icon :deep(svg[fill]) path {
  fill: #4F78AB;
}
</style>