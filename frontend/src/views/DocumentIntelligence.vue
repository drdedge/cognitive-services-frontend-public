<template>
  <div class="py-10">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-[#3B5781]">Document Intelligence</h1>
        <p class="mt-2 text-lg text-gray-600">
          Extract structured data from documents using AI-powered analysis
        </p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Main Content Area -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Upload Section -->
          <div class="bg-white shadow rounded-lg">
            <div class="px-6 py-4 border-b border-gray-200">
              <h2 class="text-lg font-medium text-[#3B5781]">Upload Document</h2>
            </div>
            
            <div class="p-6">
              <!-- File Upload Component -->
              <FileUpload
                @files-selected="handleFilesSelected"
                @upload-error="handleUploadError"
                :accept="acceptedFormats"
                :multiple="false"
                :max-size="10485760"
              />

              <!-- Processing Options -->
              <div v-if="selectedFile" class="mt-6 space-y-4">
                <h3 class="text-sm font-medium text-[#3B5781] mb-3">Processing Options</h3>
                
                <div class="space-y-3">
                  <label class="flex items-start">
                    <input
                      type="checkbox"
                      v-model="options.extractTables"
                      class="h-4 w-4 text-[#4F78AB] focus:ring-[#4F78AB] border-gray-300 rounded mt-0.5"
                    />
                    <div class="ml-3">
                      <span class="text-sm font-medium text-gray-700">Extract tables</span>
                      <p class="text-xs text-gray-500">Export tables to CSV or Excel format</p>
                    </div>
                  </label>

                  <label class="flex items-start">
                    <input
                      type="checkbox"
                      v-model="options.includeConfidence"
                      class="h-4 w-4 text-[#4F78AB] focus:ring-[#4F78AB] border-gray-300 rounded mt-0.5"
                    />
                    <div class="ml-3">
                      <span class="text-sm font-medium text-gray-700">Include confidence scores</span>
                      <p class="text-xs text-gray-500">Show AI confidence levels for extracted data</p>
                    </div>
                  </label>

                  <label class="flex items-start">
                    <input
                      type="checkbox"
                      v-model="options.detectLayout"
                      class="h-4 w-4 text-[#4F78AB] focus:ring-[#4F78AB] border-gray-300 rounded mt-0.5"
                    />
                    <div class="ml-3">
                      <span class="text-sm font-medium text-gray-700">Detect layout structure</span>
                      <p class="text-xs text-gray-500">Identify headers, paragraphs, and sections</p>
                    </div>
                  </label>
                </div>

                <div class="pt-4">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Output Format</label>
                  <select 
                    v-model="options.outputFormat" 
                    class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-[#4F78AB] focus:border-[#4F78AB] sm:text-sm"
                  >
                    <option value="markdown">Markdown</option>
                    <option value="json">JSON</option>
                    <option value="text">Plain Text</option>
                    <option value="html">HTML</option>
                  </select>
                </div>

                <!-- Process Button -->
                <div class="pt-4">
                  <button
                    @click="processDocument"
                    :disabled="processing"
                    class="w-full sm:w-auto px-6 py-3 bg-[#4F78AB] text-white font-medium rounded-md hover:bg-[#3B5781] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#4F78AB] disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                  >
                    <span v-if="processing" class="flex items-center justify-center">
                      <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Processing...
                    </span>
                    <span v-else>Process Document</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Processing Status -->
          <ProcessingStatus
            v-if="jobId && !results"
            :job-id="jobId"
            :service="{ id: 'text-extraction', name: 'Document Intelligence' }"
            :status="processingStatus"
            :progress="progress"
            :current-stage="currentStage"
            :stage-details="stageDetails"
            :start-time="startTime"
            @cancel="cancelProcessing"
            @retry="retryProcessing"
          />

          <!-- Download Section - Shows immediately when processing completes -->
          <div v-if="processingStatus === 'completed' && jobId" class="bg-green-50 border border-green-200 rounded-lg p-6">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div class="flex items-center">
                <svg class="h-8 w-8 text-green-500 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <div>
                  <h3 class="text-lg font-medium text-green-900">Processing Complete!</h3>
                  <p class="text-sm text-green-700">
                    <span v-if="characterCount > 0">{{ characterCount.toLocaleString() }} characters extracted</span>
                    <span v-else>No text detected in document</span>
                  </p>
                </div>
              </div>
              <div v-if="characterCount > 0" class="flex flex-col sm:flex-row items-center gap-4">
                <!-- Success message -->
                <transition
                  enter-active-class="transition ease-out duration-300"
                  enter-from-class="transform opacity-0 scale-95"
                  enter-to-class="transform opacity-100 scale-100"
                  leave-active-class="transition ease-in duration-200"
                  leave-from-class="transform opacity-100 scale-100"
                  leave-to-class="transform opacity-0 scale-95"
                >
                  <div v-if="downloadSuccess" class="flex items-center text-green-600">
                    <svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                    <span class="text-sm font-medium">Downloaded successfully!</span>
                  </div>
                </transition>
                
                <!-- Download button -->
                <button
                  @click="downloadProcessedResults"
                  :disabled="downloading"
                  class="px-6 py-3 bg-green-600 text-white font-medium rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors flex items-center disabled:bg-gray-400 disabled:cursor-not-allowed"
                >
                  <svg v-if="!downloading" class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <svg v-else class="animate-spin h-5 w-5 mr-2 text-white" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {{ downloading ? 'Downloading...' : 'Download Results' }}
                </button>
              </div>
            </div>
          </div>

          <!-- Results Section (Hidden - kept for future use) -->
          <div v-if="false && results" class="bg-white shadow rounded-lg">
            <div class="px-6 py-4 border-b border-gray-200">
              <div class="flex items-center justify-between">
                <h3 class="text-lg font-medium text-[#3B5781]">Extraction Results</h3>
                <div class="flex space-x-2">
                  <button 
                    @click="downloadResults('original')"
                    :disabled="downloading"
                    class="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed flex items-center"
                  >
                    <svg v-if="!downloading" class="h-4 w-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    <svg v-else class="animate-spin h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    {{ downloading ? 'Downloading...' : 'Download' }}
                  </button>
                  <button 
                    @click="copyResults"
                    class="px-3 py-1 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
                  >
                    <svg class="h-4 w-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    Copy
                  </button>
                </div>
              </div>
            </div>
            
            <div class="p-6">
              <!-- Summary Stats -->
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
                <div class="bg-gray-50 px-4 py-3 rounded-lg">
                  <dt class="text-xs font-medium text-gray-500 uppercase tracking-wider">Pages</dt>
                  <dd class="mt-1 text-lg font-semibold text-[#3B5781]">{{ results.pageCount || 1 }}</dd>
                </div>
                <div class="bg-gray-50 px-4 py-3 rounded-lg">
                  <dt class="text-xs font-medium text-gray-500 uppercase tracking-wider">Words</dt>
                  <dd class="mt-1 text-lg font-semibold text-[#3B5781]">{{ results.wordCount || 0 }}</dd>
                </div>
                <div class="bg-gray-50 px-4 py-3 rounded-lg">
                  <dt class="text-xs font-medium text-gray-500 uppercase tracking-wider">Tables</dt>
                  <dd class="mt-1 text-lg font-semibold text-[#3B5781]">{{ results.tableCount || 0 }}</dd>
                </div>
                <div class="bg-gray-50 px-4 py-3 rounded-lg">
                  <dt class="text-xs font-medium text-gray-500 uppercase tracking-wider">Confidence</dt>
                  <dd class="mt-1 text-lg font-semibold text-[#3B5781]">{{ Math.round((results.confidence || 0.95) * 100) }}%</dd>
                </div>
              </div>

              <!-- Extracted Content Preview -->
              <div class="border border-gray-200 rounded-lg p-4 bg-gray-50 max-h-96 overflow-y-auto">
                <pre class="whitespace-pre-wrap text-sm text-gray-700 font-mono">{{ results.extractedText }}</pre>
              </div>

              <!-- Tables (if any) -->
              <div v-if="results.tables && results.tables.length > 0" class="mt-6">
                <h4 class="text-sm font-medium text-gray-700 mb-3">Extracted Tables</h4>
                <div class="space-y-4">
                  <div v-for="(table, index) in results.tables" :key="index" class="border border-gray-200 rounded-lg overflow-hidden">
                    <div class="bg-gray-100 px-4 py-2 flex items-center justify-between">
                      <span class="text-sm font-medium text-gray-700">Table {{ index + 1 }}</span>
                      <button 
                        @click="downloadTable(index)"
                        class="text-sm text-[#4F78AB] hover:text-[#3B5781]"
                      >
                        Download CSV
                      </button>
                    </div>
                    <div class="overflow-x-auto">
                      <table class="min-w-full divide-y divide-gray-200">
                        <thead class="bg-gray-50">
                          <tr>
                            <th 
                              v-for="(header, colIndex) in table.headers" 
                              :key="colIndex"
                              class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                            >
                              {{ header }}
                            </th>
                          </tr>
                        </thead>
                        <tbody class="bg-white divide-y divide-gray-200">
                          <tr v-for="(row, rowIndex) in table.rows" :key="rowIndex">
                            <td 
                              v-for="(cell, cellIndex) in row" 
                              :key="cellIndex"
                              class="px-4 py-2 text-sm text-gray-900"
                            >
                              {{ cell }}
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="lg:col-span-1 space-y-6">
          <!-- Tips -->
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 class="text-sm font-medium text-blue-900 mb-2">Tips for Best Results</h3>
            <ul class="text-sm text-blue-700 space-y-1">
              <li class="flex items-start">
                <svg class="h-4 w-4 mr-1 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                Use high-quality scans (300+ DPI)
              </li>
              <li class="flex items-start">
                <svg class="h-4 w-4 mr-1 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                Ensure text is clear and readable
              </li>
              <li class="flex items-start">
                <svg class="h-4 w-4 mr-1 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                Avoid skewed or rotated pages
              </li>
              <li class="flex items-start">
                <svg class="h-4 w-4 mr-1 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                Files under 10MB process faster
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onUnmounted } from 'vue'
import FileUpload from '@/components/FileUpload.vue'
import ProcessingStatus from '@/components/ProcessingStatus.vue'
import documentIntelligenceService from '@/services/documentIntelligenceService'
import websocketService from '@/services/websocketService'

// State
const selectedFile = ref(null)
const processing = ref(false)
const jobId = ref(null)
const progress = ref(0)
const processingStatus = ref('idle')
const currentStage = ref('Initializing...')
const stageDetails = ref('')
const startTime = ref(null)
const results = ref(null)
const uploadError = ref(null)
const downloading = ref(false)
const downloadSuccess = ref(false)
const characterCount = ref(0)

// Options
const options = ref({
  extractTables: true,
  includeConfidence: false,
  detectLayout: true,
  outputFormat: 'markdown'
})

// Accepted formats
const acceptedFormats = '.pdf,.docx,.doc,.jpg,.jpeg,.png,.tiff,.bmp'

// Computed properties
const fileInfo = computed(() => {
  if (!selectedFile.value) return null
  return {
    count: 1,
    totalSize: selectedFile.value.size
  }
})


// Watch for file selection
watch(selectedFile, (newFile) => {
  if (newFile) {
    // Reset character count when new file is selected
    characterCount.value = 0
  }
})

// Methods
const handleFilesSelected = (files) => {
  if (files.length > 0) {
    selectedFile.value = files[0].file
    results.value = null
    jobId.value = null
    uploadError.value = null
    downloadSuccess.value = false
    processingStatus.value = 'idle'
  }
}

const handleUploadError = (errors) => {
  uploadError.value = errors[0]?.error || 'Upload failed'
}

const processDocument = async () => {
  if (!selectedFile.value) return

  try {
    processing.value = true
    processingStatus.value = 'processing'
    startTime.value = new Date()
    progress.value = 0
    currentStage.value = 'Initializing...'
    stageDetails.value = 'Preparing document for processing'
    
    // Process document with backend
    const processingOptions = {
      analysisType: 'layout',
      extractTables: options.value.extractTables,
      extractText: true,
      outputFormat: options.value.outputFormat
    }
    
    const result = await documentIntelligenceService.processDocument(
      selectedFile.value,
      processingOptions,
      (progressData) => {
        // Handle upload progress
        if (progressData.lengthComputable) {
          const uploadProgress = Math.round((progressData.loaded / progressData.total) * 30)
          progress.value = uploadProgress
          currentStage.value = 'Uploading document'
          stageDetails.value = `${uploadProgress}% uploaded`
        }
      }
    )
    
    jobId.value = result.job_id
    
    // Subscribe to WebSocket updates for this job
    const unsubscribe = websocketService.subscribe(jobId.value, '*', handleWebSocketUpdate)
    
    // Store unsubscribe function for cleanup
    websocketUnsubscribe.value = unsubscribe
    
  } catch (error) {
    console.error('Error processing document:', error)
    processingStatus.value = 'failed'
    currentStage.value = 'Processing failed'
    stageDetails.value = error.message || 'An error occurred while processing the document'
    processing.value = false
  }
}

// WebSocket update handler
const websocketUnsubscribe = ref(null)

const handleWebSocketUpdate = (data) => {
  console.log('WebSocket update:', data)
  
  if (data.type === 'job_update') {
    // Handle job status updates
    if (data.status === 'processing' && data.progress) {
      progress.value = data.progress.progress_percentage || 0
      currentStage.value = data.progress.current_step || 'Processing...'
      stageDetails.value = data.progress.message || ''
    } else if (data.status === 'failed' && data.error) {
      processingStatus.value = 'failed'
      processing.value = false
      currentStage.value = 'Processing failed'
      stageDetails.value = data.error.error_message || 'An error occurred'
    }
  } else if (data.type === 'job_completed') {
    // Handle job completion
    processingStatus.value = 'completed'
    processing.value = false
    progress.value = 100
    currentStage.value = 'Complete'
    stageDetails.value = 'Document processed successfully'
    
    // Extract character count from data if available
    if (data.data && data.data.character_count) {
      characterCount.value = data.data.character_count
    } else {
      // Load metadata to get character count
      loadResults()
    }
    
    // Save to recent jobs
    saveToRecentJobs()
  } else if (data.type === 'error') {
    processingStatus.value = 'failed'
    processing.value = false
    currentStage.value = 'Processing failed'
    stageDetails.value = data.error?.error_message || 'An error occurred'
  }
}

const formatResults = (backendResults) => {
  // Extract character count from metadata
  characterCount.value = backendResults.character_count || 0
  
  // Keep results for potential future use but don't display
  results.value = {
    pageCount: backendResults.total_pages || 1,
    wordCount: backendResults.word_count || 0,
    tableCount: backendResults.table_count || 0,
    confidence: backendResults.confidence_stats?.document_level?.mean || 0.95,
    extractedText: 'Results available for download',
    tables: [],
    processingTime: backendResults.processing_time_seconds || 0,
    confidenceStats: backendResults.confidence_stats
  }
}

const formatTables = (csvFiles) => {
  // For now, return empty array since CSV parsing would need additional logic
  // In a real implementation, you'd parse the CSV content or get structured data from backend
  return []
}

const loadResults = async () => {
  try {
    const metadata = await documentIntelligenceService.getResultsMetadata(jobId.value)
    // Update UI with metadata
    console.log('Results metadata:', metadata)
    
    // Format and display results
    if (metadata) {
      formatResults(metadata)
    }
  } catch (error) {
    console.error('Error loading results:', error)
    // If metadata fetch fails, assume some content was extracted
    characterCount.value = 1 // Show download button
  }
}

const cancelProcessing = async () => {
  if (!jobId.value) return
  
  try {
    await documentIntelligenceService.cancelJob(jobId.value)
    processingStatus.value = 'cancelled'
    processing.value = false
    
    // Clean up WebSocket subscription
    if (websocketUnsubscribe.value) {
      websocketUnsubscribe.value()
      websocketUnsubscribe.value = null
    }
  } catch (error) {
    console.error('Error cancelling job:', error)
    // Force local cancellation
    processingStatus.value = 'cancelled'
    processing.value = false
  }
}

const retryProcessing = () => {
  // Reset state
  results.value = null
  processingStatus.value = 'idle'
  progress.value = 0
  
  // Clean up previous WebSocket subscription
  if (websocketUnsubscribe.value) {
    websocketUnsubscribe.value()
    websocketUnsubscribe.value = null
  }
  
  // Restart processing
  processDocument()
}

const downloadResults = async (format) => {
  if (!jobId.value) return
  
  try {
    downloading.value = true
    await documentIntelligenceService.downloadResults(
      jobId.value,
      `${selectedFile.value.name.split('.')[0]}_results.zip`
    )
  } catch (error) {
    console.error('Error downloading results:', error)
    // Fallback to text download if ZIP download fails
    if (results.value && results.value.extractedText) {
      const blob = new Blob([results.value.extractedText], { type: 'text/plain' })
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `extracted-${selectedFile.value.name.split('.')[0]}.${options.value.outputFormat}`
      a.click()
      window.URL.revokeObjectURL(url)
    }
  } finally {
    downloading.value = false
  }
}

const downloadProcessedResults = async () => {
  if (!jobId.value) return
  
  try {
    downloading.value = true
    
    await documentIntelligenceService.downloadResults(
      jobId.value,
      `${selectedFile.value.name.split('.')[0]}_results.zip`
    )
    
    // Show success message briefly
    downloadSuccess.value = true
    setTimeout(() => {
      downloadSuccess.value = false
    }, 3000)
    
    // Optionally load and display results after download
    loadResults()
  } catch (error) {
    console.error('Error downloading results:', error)
    // Show error message to user
    alert('Failed to download results. Please try again.')
  } finally {
    downloading.value = false
  }
}

const downloadTable = (index) => {
  const table = results.value.tables[index]
  let csv = table.headers.join(',') + '\n'
  table.rows.forEach(row => {
    csv += row.join(',') + '\n'
  })
  
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = window.URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `table-${index + 1}.csv`
  a.click()
  window.URL.revokeObjectURL(url)
}

const copyResults = () => {
  navigator.clipboard.writeText(results.value.extractedText)
  // Could add toast notification
}

const saveToRecentJobs = () => {
  const recentJobs = JSON.parse(localStorage.getItem('recentJobs') || '[]')
  recentJobs.unshift({
    id: jobId.value,
    service: 'document-intelligence',
    fileName: selectedFile.value.name,
    timestamp: new Date().toISOString(),
    status: 'completed'
  })
  localStorage.setItem('recentJobs', JSON.stringify(recentJobs.slice(0, 10)))
}

// Cleanup on component unmount
onUnmounted(() => {
  if (websocketUnsubscribe.value) {
    websocketUnsubscribe.value()
  }
})
</script>