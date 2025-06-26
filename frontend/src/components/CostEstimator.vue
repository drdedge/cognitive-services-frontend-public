<template>
  <div class="cost-estimator bg-white rounded-lg shadow-sm border border-gray-200 p-6">
    <h3 class="text-lg font-semibold text-[#3B5781] mb-4">Cost Estimate</h3>
    
    <!-- Cost Breakdown -->
    <div class="space-y-3">
      <!-- Service Base Cost -->
      <div class="flex justify-between items-center py-2 border-b border-gray-100">
        <div>
          <p class="text-sm font-medium text-gray-700">{{ service?.name || 'Service' }}</p>
          <p class="text-xs text-gray-500">Base rate</p>
        </div>
        <span class="text-sm font-medium text-[#3B5781]">{{ formatCurrency(baseCost) }}</span>
      </div>

      <!-- File-based costs -->
      <div v-if="fileInfo" class="space-y-2">
        <!-- Per file cost -->
        <div v-if="fileInfo.count > 0" class="flex justify-between items-center py-2 border-b border-gray-100">
          <div>
            <p class="text-sm text-gray-700">Files ({{ fileInfo.count }})</p>
            <p class="text-xs text-gray-500">{{ formatCurrency(perFileCost) }} per file</p>
          </div>
          <span class="text-sm font-medium text-[#3B5781]">{{ formatCurrency(filesCost) }}</span>
        </div>

        <!-- Size-based cost -->
        <div v-if="fileInfo.totalSize > 0" class="flex justify-between items-center py-2 border-b border-gray-100">
          <div>
            <p class="text-sm text-gray-700">Data processing</p>
            <p class="text-xs text-gray-500">{{ formatFileSize(fileInfo.totalSize) }}</p>
          </div>
          <span class="text-sm font-medium text-[#3B5781]">{{ formatCurrency(sizeCost) }}</span>
        </div>
      </div>

      <!-- Options-based costs -->
      <div v-if="options && optionsCosts.length > 0" class="space-y-2">
        <div v-for="optionCost in optionsCosts" :key="optionCost.name" 
             class="flex justify-between items-center py-2 border-b border-gray-100">
          <div>
            <p class="text-sm text-gray-700">{{ optionCost.label }}</p>
            <p v-if="optionCost.description" class="text-xs text-gray-500">{{ optionCost.description }}</p>
          </div>
          <span class="text-sm font-medium text-[#3B5781]">{{ formatCurrency(optionCost.cost) }}</span>
        </div>
      </div>

      <!-- Total Cost -->
      <div class="flex justify-between items-center pt-3 border-t-2 border-gray-200">
        <span class="text-base font-semibold text-[#3B5781]">Total Estimated Cost</span>
        <span class="text-lg font-bold" :class="totalCost > 10 ? 'text-[#ffc107]' : 'text-[#3B5781]'">
          {{ formatCurrency(totalCost) }}
        </span>
      </div>
    </div>

    <!-- High Cost Warning -->
    <div v-if="totalCost > 10" class="mt-4 p-4 bg-[#ffc107] bg-opacity-10 border border-[#ffc107] rounded-lg">
      <div class="flex items-start">
        <svg class="h-5 w-5 text-[#ffc107] mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
        <div class="flex-1">
          <p class="text-sm font-medium text-[#ffc107]">High cost warning</p>
          <p class="text-sm text-gray-600 mt-1">
            The estimated cost exceeds $10. Please review your selections before proceeding.
          </p>
        </div>
      </div>
    </div>

    <!-- Cost Notes -->
    <div class="mt-4 text-xs text-gray-500 space-y-1">
      <p>* This is an estimate based on current pricing.</p>
      <p>* Actual costs may vary depending on processing complexity.</p>
      <p>* All prices are in {{ currency }}.</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  service: {
    type: Object,
    default: null
  },
  fileInfo: {
    type: Object,
    default: null,
    validator: (value) => {
      if (!value) return true
      return typeof value.count === 'number' && typeof value.totalSize === 'number'
    }
  },
  options: {
    type: Object,
    default: null
  },
  currency: {
    type: String,
    default: 'USD'
  }
})

// Real Azure Cognitive Services Pricing (as of 2025)
const azurePricing = {
  services: {
    'document-intelligence': { 
      pricePerThousandPages: 10.00,
      unit: 'pages',
      description: 'Document Intelligence - $10 per 1,000 pages'
    },
    'translation': { 
      pricePerMillionCharacters: 10.00,
      unit: 'characters',
      description: 'Translation - $10 per million characters'
    },
    'transcription': { 
      fastTranscription: 0.36, // per hour
      batchTranscription: 0.18, // per hour
      unit: 'hours',
      description: 'Transcription - Fast: $0.36/hour, Batch: $0.18/hour'
    }
  },
  options: {
    'batchProcessing': { cost: 0.50, label: 'Batch Processing (50% discount)', multiplier: 0.5 },
    'highAccuracy': { cost: 0.00, label: 'High Accuracy Mode (included)', multiplier: 1.0 },
    'speakerDiarization': { cost: 0.00, label: 'Speaker Diarization (included)', multiplier: 1.0 },
    'timestamps': { cost: 0.00, label: 'Timestamps (included)', multiplier: 1.0 }
  }
}

// Helper function to calculate cost based on Azure pricing
const calculateAzureCost = (serviceId, fileInfo, options) => {
  const serviceConfig = azurePricing.services[serviceId]
  if (!serviceConfig) return 0

  let baseCost = 0
  
  switch (serviceId) {
    case 'document-intelligence':
      if (fileInfo?.pageCount) {
        baseCost = (fileInfo.pageCount / 1000) * serviceConfig.pricePerThousandPages
      }
      break
      
    case 'translation':
      if (fileInfo?.characterCount) {
        baseCost = (fileInfo.characterCount / 1000000) * serviceConfig.pricePerMillionCharacters
      }
      break
      
    case 'transcription':
      if (fileInfo?.audioDuration) {
        const hours = fileInfo.audioDuration / 3600
        const isBatch = options?.batchProcessing
        const rate = isBatch ? serviceConfig.batchTranscription : serviceConfig.fastTranscription
        baseCost = hours * rate
      }
      break
  }
  
  return baseCost
}

// Computed costs using Azure pricing
const servicePricing = computed(() => {
  if (!props.service?.id) return azurePricing.services['document-intelligence']
  return azurePricing.services[props.service.id] || azurePricing.services['document-intelligence']
})

const baseCost = computed(() => {
  return calculateAzureCost(props.service?.id, props.fileInfo, props.options)
})

const perFileCost = computed(() => {
  // Azure pricing is now unit-based, not per-file
  return 0
})

const filesCost = computed(() => {
  // Included in base cost calculation
  return 0
})

const sizeCost = computed(() => {
  // Included in base cost calculation  
  return 0
})

const optionsCosts = computed(() => {
  if (!props.options) return []
  
  return Object.entries(props.options)
    .filter(([key, value]) => value === true)
    .map(([key]) => {
      const optionPricing = azurePricing.options[key]
      if (!optionPricing) return null
      
      // Calculate additional cost based on multiplier
      const additionalCost = optionPricing.multiplier !== 1.0 
        ? baseCost.value * (optionPricing.multiplier - 1.0)
        : optionPricing.cost || 0
      
      return {
        name: key,
        label: optionPricing.label,
        cost: additionalCost,
        description: optionPricing.description
      }
    })
    .filter(Boolean)
})

const totalCost = computed(() => {
  const base = baseCost.value
  const options = optionsCosts.value.reduce((sum, option) => sum + option.cost, 0)
  
  return Math.max(0, base + options) // Ensure non-negative
})

// Utility functions
const formatCurrency = (amount) => {
  const formatter = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: props.currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
  return formatter.format(amount)
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>

<style scoped>
/* Add any component-specific styles here */
</style>