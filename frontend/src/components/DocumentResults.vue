<template>
  <div class="mt-8 bg-white shadow rounded-lg">
    <div class="px-6 py-4 border-b border-gray-200">
      <h3 class="text-lg font-medium text-gray-900">Analysis Results</h3>
    </div>
    
    <div class="p-6">
      <!-- Document Info -->
      <div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <div class="bg-gray-50 px-4 py-3 rounded-lg">
          <dt class="text-sm font-medium text-gray-500">Document</dt>
          <dd class="mt-1 text-sm font-medium text-gray-900">{{ results.document_name }}</dd>
        </div>
        <div class="bg-gray-50 px-4 py-3 rounded-lg">
          <dt class="text-sm font-medium text-gray-500">Pages</dt>
          <dd class="mt-1 text-sm font-medium text-gray-900">{{ results.total_pages }}</dd>
        </div>
        <div class="bg-gray-50 px-4 py-3 rounded-lg">
          <dt class="text-sm font-medium text-gray-500">Processing Time</dt>
          <dd class="mt-1 text-sm font-medium text-gray-900">{{ formatTime(results.processing_time_seconds) }}</dd>
        </div>
      </div>

      <!-- Tables Section -->
      <div v-if="results.tables && results.tables.count > 0" class="mb-6">
        <h4 class="text-sm font-medium text-gray-700 mb-3">Extracted Tables</h4>
        <div class="bg-gray-50 rounded-lg p-4">
          <p class="text-sm text-gray-600 mb-3">
            Found {{ results.tables.count }} table(s) in the document
          </p>
          <div class="flex flex-wrap gap-2">
            <button
              @click="$emit('download', 'csv')"
              class="btn-secondary text-sm"
            >
              <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download CSV Files
            </button>
            <button
              v-if="results.tables.excel_file"
              @click="$emit('download', 'excel')"
              class="btn-primary text-sm"
            >
              <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download Excel Workbook
            </button>
          </div>
        </div>
      </div>

      <!-- Text Content Section -->
      <div v-if="results.markdown_content" class="mb-6">
        <h4 class="text-sm font-medium text-gray-700 mb-3">Extracted Text</h4>
        <div class="bg-gray-50 rounded-lg p-4">
          <div class="prose prose-sm max-w-none max-h-96 overflow-y-auto">
            <div v-html="renderMarkdown(results.markdown_content)"></div>
          </div>
          <div class="mt-3 flex gap-2">
            <button
              @click="$emit('download', 'markdown')"
              class="btn-secondary text-sm"
            >
              <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download Markdown
            </button>
          </div>
        </div>
      </div>

      <!-- Confidence Statistics -->
      <div v-if="results.confidence_stats && results.confidence_stats.document_level">
        <h4 class="text-sm font-medium text-gray-700 mb-3">Extraction Confidence</h4>
        <div class="grid grid-cols-1 sm:grid-cols-4 gap-4">
          <div class="bg-blue-50 px-4 py-3 rounded-lg">
            <dt class="text-sm font-medium text-blue-600">Mean</dt>
            <dd class="mt-1 text-lg font-medium text-blue-900">
              {{ formatPercent(results.confidence_stats.document_level.mean) }}
            </dd>
          </div>
          <div class="bg-green-50 px-4 py-3 rounded-lg">
            <dt class="text-sm font-medium text-green-600">Median</dt>
            <dd class="mt-1 text-lg font-medium text-green-900">
              {{ formatPercent(results.confidence_stats.document_level.median) }}
            </dd>
          </div>
          <div class="bg-yellow-50 px-4 py-3 rounded-lg">
            <dt class="text-sm font-medium text-yellow-600">Min</dt>
            <dd class="mt-1 text-lg font-medium text-yellow-900">
              {{ formatPercent(results.confidence_stats.document_level.min) }}
            </dd>
          </div>
          <div class="bg-purple-50 px-4 py-3 rounded-lg">
            <dt class="text-sm font-medium text-purple-600">Max</dt>
            <dd class="mt-1 text-lg font-medium text-purple-900">
              {{ formatPercent(results.confidence_stats.document_level.max) }}
            </dd>
          </div>
        </div>

        <!-- Low Confidence Pages -->
        <div v-if="results.confidence_stats.low_confidence_pages && results.confidence_stats.low_confidence_pages.length > 0" class="mt-4">
          <p class="text-sm text-warning mb-2">
            <svg class="inline h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            Pages with low confidence (< 85%): 
            {{ results.confidence_stats.low_confidence_pages.map(p => p.page).join(', ') }}
          </p>
        </div>

        <!-- Confidence Dashboard -->
        <div v-if="results.confidence_dashboard" class="mt-4">
          <button
            @click="showDashboard = !showDashboard"
            class="btn-secondary text-sm"
          >
            <svg class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            {{ showDashboard ? 'Hide' : 'View' }} Confidence Dashboard
          </button>
          
          <div v-if="showDashboard" class="mt-4">
            <img 
              :src="`/api/storage/download/${results.confidence_dashboard}`" 
              alt="Confidence Dashboard"
              class="rounded-lg shadow-lg"
            />
          </div>
        </div>
      </div>

      <!-- Download All Results -->
      <div class="mt-6 pt-6 border-t border-gray-200">
        <button
          @click="$emit('download', 'all')"
          class="btn-primary"
        >
          <svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
          </svg>
          Download All Results
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

defineProps({
  results: {
    type: Object,
    required: true
  },
  taskId: {
    type: String,
    required: true
  }
})

defineEmits(['download'])

const showDashboard = ref(false)

// Helper methods
const formatTime = (seconds) => {
  if (seconds < 1) return `${Math.round(seconds * 1000)}ms`
  return `${seconds.toFixed(1)}s`
}

const formatPercent = (value) => {
  if (value === null || value === undefined) return 'N/A'
  return `${(value * 100).toFixed(1)}%`
}

const renderMarkdown = (markdown) => {
  // Simple markdown to HTML conversion
  // In production, use a proper markdown parser
  return markdown
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/\*\*(.*)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*)\*/g, '<em>$1</em>')
    .replace(/\n/g, '<br>')
}
</script>