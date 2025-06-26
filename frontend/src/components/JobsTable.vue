<template>
  <div class="bg-white shadow rounded-lg">
    <div class="px-4 py-5 sm:p-6">
      <div class="sm:flex sm:items-center sm:justify-between mb-4">
        <h3 class="text-lg leading-6 font-medium text-gray-900">
          Job History
        </h3>
        <div class="mt-3 sm:mt-0 sm:ml-4 flex space-x-4">
          <!-- Search -->
          <div class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search jobs..."
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-action focus:border-primary-action sm:text-sm"
            />
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
          
          <!-- Filter by Service -->
          <select
            v-model="filterService"
            class="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-action focus:border-primary-action sm:text-sm rounded-md"
          >
            <option value="">All Services</option>
            <option value="document-intelligence">Document Intelligence</option>
            <option value="translation">Translation</option>
            <option value="transcription">Transcription</option>
          </select>
          
          <!-- Filter by Status -->
          <select
            v-model="filterStatus"
            class="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-action focus:border-primary-action sm:text-sm rounded-md"
          >
            <option value="">All Status</option>
            <option value="completed">Completed</option>
            <option value="processing">Processing</option>
            <option value="failed">Failed</option>
          </select>
        </div>
      </div>
      
      <!-- Table -->
      <div class="overflow-hidden">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th 
                  v-for="column in columns" 
                  :key="column.key"
                  scope="col" 
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  @click="sortBy(column.key)"
                >
                  <div class="flex items-center">
                    {{ column.label }}
                    <svg v-if="sortColumn === column.key" class="ml-1 h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
                      <path v-if="sortDirection === 'asc'" d="M7 10l5-5 5 5H7z" />
                      <path v-else d="M7 10l5 5 5-5H7z" />
                    </svg>
                  </div>
                </th>
                <th scope="col" class="relative px-6 py-3">
                  <span class="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr 
                v-for="job in paginatedJobs" 
                :key="job.id"
                :data-job-id="job.id"
                class="hover:bg-gray-50 transition-colors"
              >
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ formatDate(job.timestamp) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ getUserName(job.userId) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <span 
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="{
                      'bg-blue-100 text-blue-800': job.service === 'document-intelligence',
                      'bg-green-100 text-green-800': job.service === 'translation',
                      'bg-purple-100 text-purple-800': job.service === 'transcription'
                    }"
                  >
                    {{ formatServiceName(job.service) }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <div class="flex items-center">
                    <span class="truncate max-w-xs" :title="job.fileName">{{ job.fileName }}</span>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span 
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                    :class="{
                      'bg-green-100 text-green-800': job.status === 'completed',
                      'bg-blue-100 text-blue-800': job.status === 'processing',
                      'bg-red-100 text-red-800': job.status === 'failed',
                      'bg-gray-100 text-gray-800': job.status === 'cancelled'
                    }"
                  >
                    {{ job.status }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ${{ job.cost?.toFixed(2) || '0.00' }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ formatProcessingTime(job.processingTime) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    v-if="job.status === 'completed'"
                    @click="$emit('download-results', job)"
                    class="text-primary-action hover:text-highlight"
                  >
                    Retrieve Results
                  </button>
                  <span v-else-if="job.status === 'processing'" class="text-gray-400">
                    Processing...
                  </span>
                  <span v-else class="text-gray-400">
                    N/A
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      
      <!-- Pagination -->
      <div class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
        <div class="flex-1 flex justify-between sm:hidden">
          <button
            @click="currentPage--"
            :disabled="currentPage === 1"
            class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Previous
          </button>
          <button
            @click="currentPage++"
            :disabled="currentPage === totalPages"
            class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Next
          </button>
        </div>
        <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
          <div>
            <p class="text-sm text-gray-700">
              Showing
              <span class="font-medium">{{ startIndex + 1 }}</span>
              to
              <span class="font-medium">{{ Math.min(endIndex, filteredJobs.length) }}</span>
              of
              <span class="font-medium">{{ filteredJobs.length }}</span>
              results
            </p>
          </div>
          <div>
            <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
              <button
                @click="currentPage--"
                :disabled="currentPage === 1"
                class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span class="sr-only">Previous</span>
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </button>
              
              <span class="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
                Page {{ currentPage }} of {{ totalPages }}
              </span>
              
              <button
                @click="currentPage++"
                :disabled="currentPage === totalPages"
                class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span class="sr-only">Next</span>
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                </svg>
              </button>
            </nav>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { completedJobs, processingJobs, failedJobs } from '@/mock-data'
import { userAnalytics } from '@/mock-data'

const props = defineProps({
  highlightJobId: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['download-results'])

// Combine all jobs
const allJobs = [...completedJobs, ...processingJobs, ...failedJobs]

// State
const searchQuery = ref('')
const filterService = ref('')
const filterStatus = ref('')
const sortColumn = ref('timestamp')
const sortDirection = ref('desc')
const currentPage = ref(1)
const itemsPerPage = 20

// Table columns
const columns = [
  { key: 'timestamp', label: 'Date' },
  { key: 'userId', label: 'User' },
  { key: 'service', label: 'Service' },
  { key: 'fileName', label: 'File Name' },
  { key: 'status', label: 'Status' },
  { key: 'cost', label: 'Cost' },
  { key: 'processingTime', label: 'Processing Time' }
]

// User lookup helper
const getUserName = (userId) => {
  const user = userAnalytics.topUsersByJobs.find(u => u.userId === userId)
  return user?.name || userId
}

// Format helpers
const formatDate = (timestamp) => {
  return new Date(timestamp).toLocaleString()
}

const formatServiceName = (service) => {
  const names = {
    'document-intelligence': 'Document Intel',
    'translation': 'Translation',
    'transcription': 'Transcription'
  }
  return names[service] || service
}

const formatProcessingTime = (ms) => {
  if (!ms) return '-'
  const seconds = Math.floor(ms / 1000)
  if (seconds < 60) return `${seconds}s`
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}m ${remainingSeconds}s`
}

// Sorting
const sortBy = (column) => {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value = column
    sortDirection.value = 'asc'
  }
  currentPage.value = 1 // Reset to first page when sorting
}

// Filtering and sorting
const filteredJobs = computed(() => {
  let jobs = [...allJobs]
  
  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    jobs = jobs.filter(job => 
      job.fileName.toLowerCase().includes(query) ||
      job.id.toLowerCase().includes(query) ||
      getUserName(job.userId).toLowerCase().includes(query)
    )
  }
  
  // Apply service filter
  if (filterService.value) {
    jobs = jobs.filter(job => job.service === filterService.value)
  }
  
  // Apply status filter
  if (filterStatus.value) {
    jobs = jobs.filter(job => job.status === filterStatus.value)
  }
  
  // Apply sorting
  jobs.sort((a, b) => {
    let aVal = a[sortColumn.value]
    let bVal = b[sortColumn.value]
    
    // Handle special cases
    if (sortColumn.value === 'timestamp') {
      aVal = new Date(aVal).getTime()
      bVal = new Date(bVal).getTime()
    }
    
    if (sortDirection.value === 'asc') {
      return aVal > bVal ? 1 : -1
    } else {
      return aVal < bVal ? 1 : -1
    }
  })
  
  return jobs
})

// Pagination
const totalPages = computed(() => Math.ceil(filteredJobs.value.length / itemsPerPage))
const startIndex = computed(() => (currentPage.value - 1) * itemsPerPage)
const endIndex = computed(() => startIndex.value + itemsPerPage)
const paginatedJobs = computed(() => filteredJobs.value.slice(startIndex.value, endIndex.value))

// Reset pagination when filters change
const resetPagination = () => {
  currentPage.value = 1
}

// Watch for filter changes
onMounted(() => {
  // If there's a highlighted job, find its page
  if (props.highlightJobId) {
    const jobIndex = filteredJobs.value.findIndex(job => job.id === props.highlightJobId)
    if (jobIndex !== -1) {
      currentPage.value = Math.floor(jobIndex / itemsPerPage) + 1
    }
  }
})
</script>

<style scoped>
/* Any additional styles */
</style>