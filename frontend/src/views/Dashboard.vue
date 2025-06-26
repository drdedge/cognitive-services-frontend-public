<template>
  <div class="py-10">
    <header>
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 class="text-3xl font-bold leading-tight text-[#3B5781]">
          Azure Cognitive Services Dashboard
        </h1>
        <p class="mt-2 text-lg text-gray-600">
          Harness the power of Azure AI to process documents, translate text, and transcribe audio with enterprise-grade accuracy
        </p>
      </div>
    </header>

    <main>
      <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
        <!-- Welcome Section -->
        <div class="mt-8 bg-gradient-to-r from-[#4F78AB] to-[#3B5781] rounded-lg shadow-lg p-8 mx-4 sm:mx-0">
          <div class="flex items-center justify-between">
            <div class="text-white">
              <h2 class="text-2xl font-bold mb-2">Welcome to Cognitive Services</h2>
              <p class="text-blue-100">
                Select a service below to get started. Each service provides real-time processing with detailed cost estimates.
              </p>
            </div>
            <svg class="hidden sm:block w-24 h-24 text-white opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
        </div>

        <!-- Services Grid -->
        <div class="mt-10 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3 px-4 sm:px-0">
          <ServiceCard
            :service="documentService"
            @select="navigateToService"
          >
            <template #icon>
              <svg class="w-12 h-12 text-[#4F78AB]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </template>
          </ServiceCard>

          <ServiceCard
            :service="translationService"
            @select="navigateToService"
          >
            <template #icon>
              <svg class="w-12 h-12 text-[#4F78AB]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
              </svg>
            </template>
          </ServiceCard>

          <ServiceCard
            :service="transcriptionService"
            @select="navigateToService"
          >
            <template #icon>
              <svg class="w-12 h-12 text-[#4F78AB]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            </template>
          </ServiceCard>
        </div>

        <!-- Recent Jobs Section -->
        <div class="mt-12 bg-white overflow-hidden shadow rounded-lg mx-4 sm:mx-0">
          <div class="px-6 py-4 border-b border-gray-200">
            <div class="flex items-center justify-between">
              <h2 class="text-lg font-medium text-[#3B5781]">Recent Jobs</h2>
              <button 
                v-if="recentJobs.length > 0"
                @click="clearRecentJobs"
                class="text-sm text-gray-500 hover:text-gray-700"
              >
                Clear All
              </button>
            </div>
          </div>
          <div class="p-6">
            <div v-if="recentJobs.length === 0" class="text-center py-8">
              <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              <p class="mt-2 text-sm text-gray-500">No recent jobs</p>
              <p class="text-xs text-gray-400 mt-1">Your processing history will appear here</p>
            </div>
            <div v-else class="space-y-4">
              <div 
                v-for="job in recentJobs" 
                :key="job.id"
                @click="navigateToJob(job)"
                class="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors cursor-pointer"
              >
                <div class="flex items-center justify-between">
                  <div class="flex items-center space-x-3">
                    <div 
                      class="p-2 rounded-full"
                      :class="{
                        'bg-blue-100': job.service === 'document-intelligence',
                        'bg-green-100': job.service === 'translation',
                        'bg-purple-100': job.service === 'transcription'
                      }"
                    >
                      <svg 
                        v-if="job.service === 'document-intelligence'"
                        class="w-5 h-5 text-blue-600" 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                      <svg 
                        v-else-if="job.service === 'translation'"
                        class="w-5 h-5 text-green-600" 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5h12M9 3v2m1.048 9.5A18.022 18.022 0 016.412 9m6.088 9h7M11 21l5-10 5 10M12.751 5C11.783 10.77 8.07 15.61 3 18.129" />
                      </svg>
                      <svg 
                        v-else-if="job.service === 'transcription'"
                        class="w-5 h-5 text-purple-600" 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                      >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                      </svg>
                    </div>
                    <div>
                      <p class="text-sm font-medium text-[#3B5781]">{{ job.fileName }}</p>
                      <p class="text-xs text-gray-500">{{ formatJobTime(job.timestamp) }}</p>
                    </div>
                  </div>
                  <div class="flex items-center space-x-2">
                    <span 
                      class="px-2 py-1 text-xs font-medium rounded-full"
                      :class="{
                        'bg-green-100 text-green-800': job.status === 'completed',
                        'bg-blue-100 text-blue-800': job.status === 'processing',
                        'bg-red-100 text-red-800': job.status === 'error',
                        'bg-gray-100 text-gray-800': job.status === 'cancelled'
                      }"
                    >
                      {{ job.status }}
                    </span>
                    <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Stats -->
        <div class="mt-8 bg-white overflow-hidden shadow rounded-lg mx-4 sm:mx-0">
          <div class="px-4 py-5 sm:p-6">
            <h2 class="text-lg font-medium text-[#3B5781] mb-4">Service Capabilities</h2>
            <dl class="grid grid-cols-1 gap-5 sm:grid-cols-3">
              <div class="bg-gradient-to-br from-blue-50 to-blue-100 px-4 py-5 rounded-lg">
                <dt class="text-sm font-medium text-blue-700">
                  Document Formats
                </dt>
                <dd class="mt-1 text-3xl font-semibold text-[#3B5781]">
                  10+
                </dd>
                <p class="mt-2 text-xs text-blue-600">PDF, DOCX, Images, and more</p>
              </div>
              <div class="bg-gradient-to-br from-green-50 to-green-100 px-4 py-5 rounded-lg">
                <dt class="text-sm font-medium text-green-700">
                  Languages
                </dt>
                <dd class="mt-1 text-3xl font-semibold text-[#3B5781]">
                  100+
                </dd>
                <p class="mt-2 text-xs text-green-600">Translation & Transcription</p>
              </div>
              <div class="bg-gradient-to-br from-purple-50 to-purple-100 px-4 py-5 rounded-lg">
                <dt class="text-sm font-medium text-purple-700">
                  Processing Speed
                </dt>
                <dd class="mt-1 text-3xl font-semibold text-[#3B5781]">
                  Real-time
                </dd>
                <p class="mt-2 text-xs text-purple-600">Live progress updates</p>
              </div>
            </dl>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ServiceCard from '@/components/ServiceCard.vue'

const router = useRouter()

// Services data
const documentService = {
  id: 'document-intelligence',
  name: 'Document Intelligence',
  description: 'Extract text, tables, and structure from PDFs, images, and documents with AI-powered analysis',
  features: [
    'Extract tables to CSV/Excel',
    'Support for 10+ file formats',
    'Structured data extraction',
    'Multi-language support'
  ],
  price: 'From $0.50 per page'
}

const translationService = {
  id: 'translation',
  name: 'Translation',
  description: 'Translate text and documents across 100+ languages with neural machine translation',
  features: [
    'Real-time text translation',
    'Document translation',
    'Auto-detect source language',
    'Batch translation support'
  ],
  price: 'From $1.00 per 1K characters'
}

const transcriptionService = {
  id: 'transcription',
  name: 'Transcription',
  description: 'Convert speech to text with high accuracy, supporting multiple languages and audio formats',
  features: [
    'Speaker diarization',
    'Automatic punctuation',
    'Multiple output formats',
    'Timestamp generation'
  ],
  price: 'From $0.75 per minute'
}

// Recent jobs (mock data)
const recentJobs = ref([])

// Methods
const navigateToService = (service) => {
  router.push(`/${service.id}`)
}

const navigateToJob = (job) => {
  router.push(`/usage?jobId=${job.id}`)
}

const clearRecentJobs = () => {
  recentJobs.value = []
  localStorage.removeItem('recentJobs')
}

const formatJobTime = (timestamp) => {
  const date = new Date(timestamp)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) {
    return 'Just now'
  } else if (diff < 3600000) {
    const mins = Math.floor(diff / 60000)
    return `${mins} minute${mins > 1 ? 's' : ''} ago`
  } else if (diff < 86400000) {
    const hours = Math.floor(diff / 3600000)
    return `${hours} hour${hours > 1 ? 's' : ''} ago`
  } else {
    return date.toLocaleDateString()
  }
}

// Load recent jobs from localStorage
onMounted(() => {
  const savedJobs = localStorage.getItem('recentJobs')
  if (savedJobs) {
    recentJobs.value = JSON.parse(savedJobs)
  } else {
    // Mock data for demonstration
    recentJobs.value = [
      {
        id: 'job-1',
        service: 'document-intelligence',
        fileName: 'annual-report-2024.pdf',
        timestamp: new Date(Date.now() - 1800000).toISOString(),
        status: 'completed'
      },
      {
        id: 'job-2',
        service: 'translation',
        fileName: 'product-manual.docx',
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        status: 'completed'
      },
      {
        id: 'job-3',
        service: 'transcription',
        fileName: 'interview-recording.mp3',
        timestamp: new Date(Date.now() - 3600000).toISOString(),
        status: 'processing'
      }
    ]
  }
})
</script>

<style scoped>
/* Add any additional styling if needed */
</style>