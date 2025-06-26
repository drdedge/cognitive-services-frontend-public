<template>
  <div class="py-10">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-[#3B5781]">Document Translation</h1>
        <p class="mt-2 text-lg text-gray-600">
          Translate documents across 100+ languages with neural machine translation while preserving formatting
        </p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Main Content Area -->
        <div class="lg:col-span-2">
          <!-- Document Translation -->
          <div class="bg-white shadow rounded-lg">
            <div class="p-6">
                <!-- Language Selection for Documents -->
                <div class="mb-6">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Translate To</label>
                  <select 
                    v-model="docTargetLanguage" 
                    class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-[#4F78AB] focus:border-[#4F78AB] sm:text-sm"
                    :disabled="loadingLanguages"
                  >
                    <option value="">Select language</option>
                    <option v-if="loadingLanguages" disabled>Loading languages...</option>
                    <option v-for="lang in commonLanguages" :key="lang.code" :value="lang.code">
                      {{ lang.name }}
                    </option>
                  </select>
                  <p class="mt-2 text-sm text-gray-500">Source language will be automatically detected</p>
                </div>

                <!-- Document Upload -->
                <FileUpload
                  @files-selected="handleDocumentSelected"
                  @upload-error="handleUploadError"
                  :accept="'.txt,.docx,.html,.md'"
                  :multiple="false"
                  :max-size="5242880"
                />

                <!-- Translate Document Button -->
                <div v-if="selectedDocument && docTargetLanguage" class="mt-6 flex justify-center">
                  <button
                    @click="translateDocument"
                    :disabled="translatingDoc"
                    class="px-6 py-3 bg-[#4F78AB] text-white font-medium rounded-md hover:bg-[#3B5781] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#4F78AB] disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                  >
                    <span v-if="translatingDoc" class="flex items-center">
                      <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Translating Document...
                    </span>
                    <span v-else>Translate Document</span>
                  </button>
                </div>
            </div>
          </div>

          <!-- Progress Section -->
          <ProcessingStatus
            v-if="docJobId && !docResults"
            :job-id="docJobId"
            :service="{ id: 'translation', name: 'Translation' }"
            :status="docProcessingStatus"
            :progress="docProgress"
            :current-stage="docCurrentStage"
            :stage-details="docStageDetails"
            :start-time="docStartTime"
            class="mt-6"
            @cancel="cancelDocProcessing"
            @retry="retryDocProcessing"
          />

          <!-- Results -->
          <div v-if="docResults" class="mt-6 bg-white shadow rounded-lg">
            <div class="px-6 py-4 border-b border-gray-200">
              <h3 class="text-lg font-medium text-[#3B5781]">Translation Complete</h3>
            </div>
            <div class="p-6">
              <div class="grid grid-cols-2 gap-4 mb-6">
                <div class="bg-gray-50 px-4 py-3 rounded-lg">
                  <dt class="text-xs font-medium text-gray-500 uppercase tracking-wider">Source</dt>
                  <dd class="mt-1 text-sm font-medium text-[#3B5781]">{{ getLanguageName(docResults.sourceLanguage) }}</dd>
                </div>
                <div class="bg-gray-50 px-4 py-3 rounded-lg">
                  <dt class="text-xs font-medium text-gray-500 uppercase tracking-wider">Target</dt>
                  <dd class="mt-1 text-sm font-medium text-[#3B5781]">{{ getLanguageName(docResults.targetLanguage) }}</dd>
                </div>
                <div class="bg-gray-50 px-4 py-3 rounded-lg">
                  <dt class="text-xs font-medium text-gray-500 uppercase tracking-wider">Words</dt>
                  <dd class="mt-1 text-sm font-medium text-[#3B5781]">{{ docResults.wordCount }}</dd>
                </div>
                <div class="bg-gray-50 px-4 py-3 rounded-lg">
                  <dt class="text-xs font-medium text-gray-500 uppercase tracking-wider">Characters</dt>
                  <dd class="mt-1 text-sm font-medium text-[#3B5781]">{{ docResults.charCount }}</dd>
                </div>
              </div>
              
              <div class="flex">
                <button 
                  @click="downloadTranslatedDoc"
                  class="px-4 py-2 bg-[#4F78AB] text-white font-medium rounded-md hover:bg-[#3B5781] transition-colors"
                >
                  <svg class="h-5 w-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                  </svg>
                  Download Results
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="lg:col-span-1 space-y-6">
          <!-- Cost Estimator -->
          <CostEstimator
            :service="{ id: 'translation', name: 'Translation' }"
            :file-info="fileInfo"
            :options="costOptions"
          />

          <!-- Language Stats -->
          <div class="bg-white shadow rounded-lg p-6">
            <h3 class="text-lg font-medium text-[#3B5781] mb-4">Supported Languages</h3>
            <div class="space-y-3">
              <div class="flex items-center justify-between text-sm">
                <span class="text-gray-600">Total Languages</span>
                <span class="font-medium text-[#3B5781]">100+</span>
              </div>
              <div class="flex items-center justify-between text-sm">
                <span class="text-gray-600">Neural Translation</span>
                <span class="font-medium text-[#3B5781]">95%</span>
              </div>
              <div class="flex items-center justify-between text-sm">
                <span class="text-gray-600">Real-time</span>
                <span class="font-medium text-[#3B5781]">Yes</span>
              </div>
            </div>
          </div>

          <!-- Popular Languages -->
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 class="text-sm font-medium text-blue-900 mb-2">Popular Languages</h3>
            <div class="flex flex-wrap gap-2">
              <span 
                v-for="lang in popularLanguages" 
                :key="lang.code"
                @click="setTargetLanguage(lang.code)"
                class="px-3 py-1 bg-white text-sm text-blue-700 rounded-full border border-blue-300 cursor-pointer hover:bg-blue-100 transition-colors"
              >
                {{ lang.name }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import FileUpload from '@/components/FileUpload.vue'
import ProcessingStatus from '@/components/ProcessingStatus.vue'
import CostEstimator from '@/components/CostEstimator.vue'
import translationService from '@/services/translationService'
import websocketService from '@/services/websocketService'

// State
// Document translation state
const selectedDocument = ref(null)
const docTargetLanguage = ref('en')
const translatingDoc = ref(false)
const docJobId = ref(null)
const docProgress = ref(0)
const docProcessingStatus = ref('idle')
const docCurrentStage = ref('')
const docStageDetails = ref('')
const docStartTime = ref(null)
const docResults = ref(null)

// Language data
const commonLanguages = ref([])
const popularLanguages = ref([])
const loadingLanguages = ref(false)
const languageError = ref(null)

// WebSocket state
const unsubscribeWebSocket = ref(null)

// Computed properties
const fileInfo = computed(() => {
  if (selectedDocument.value) {
    return {
      count: 1,
      totalSize: selectedDocument.value.size
    }
  }
  return null
})

const costOptions = computed(() => {
  if (selectedDocument.value) {
    return {
      fileSize: selectedDocument.value.size,
      fileType: selectedDocument.value.name.split('.').pop(),
      targetLanguage: docTargetLanguage.value,
      sourceLanguage: 'auto'
    }
  }
  return {}
})

// Methods
const getLanguageName = (code) => {
  const lang = commonLanguages.value.find(l => l.code === code)
  return lang ? lang.name : code
}

const setTargetLanguage = (code) => {
  docTargetLanguage.value = code
}

const handleDocumentSelected = (files) => {
  if (files.length > 0) {
    selectedDocument.value = files[0].file
    docResults.value = null
    docJobId.value = null
  }
}

const handleUploadError = (errors) => {
  console.error('Upload error:', errors)
}

const translateDocument = async () => {
  if (!selectedDocument.value || !docTargetLanguage.value) return

  translatingDoc.value = true
  docProcessingStatus.value = 'processing'
  docStartTime.value = new Date()
  docProgress.value = 0
  docResults.value = null
  
  try {
    // Start document translation with auto-detect
    const options = {
      targetLanguage: docTargetLanguage.value
      // Source language will be auto-detected
    }
    
    const result = await translationService.translateDocument(
      selectedDocument.value,
      options,
      // Upload progress callback
      (progressEvent) => {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        docProgress.value = Math.min(percentCompleted * 0.2, 20) // Upload is 20% of total
        docCurrentStage.value = 'Uploading document'
        docStageDetails.value = `Uploading: ${percentCompleted}%`
      }
    )
    
    // Store job ID
    docJobId.value = result.job_id
    
    // Subscribe to WebSocket updates
    if (unsubscribeWebSocket.value) {
      unsubscribeWebSocket.value()
    }
    
    unsubscribeWebSocket.value = websocketService.subscribe(
      docJobId.value,
      '*',
      handleWebSocketUpdate
    )
    
    // Save to recent jobs
    saveToRecentJobs()
  } catch (error) {
    console.error('Document translation error:', error)
    docProcessingStatus.value = 'failed'
    translatingDoc.value = false
    alert(`Translation failed: ${error.message || 'Unknown error'}`)
  }
}

const handleWebSocketUpdate = (data) => {
  if (data.type === 'job_update') {
    if (data.progress) {
      docProgress.value = data.progress.progress_percentage || 0
      docCurrentStage.value = data.progress.current_step || 'Processing'
      docStageDetails.value = data.progress.message || ''
    }
    
    if (data.status === 'processing') {
      docProcessingStatus.value = 'processing'
    }
  } else if (data.type === 'job_completed') {
    docProcessingStatus.value = 'completed'
    docProgress.value = 100
    translatingDoc.value = false
    
    // Set results
    docResults.value = {
      jobId: docJobId.value,
      sourceLanguage: data.data?.source_language || 'auto',
      targetLanguage: data.data?.target_language || docTargetLanguage.value,
      wordCount: data.data?.word_count || 0,
      charCount: data.data?.character_count || 0,
      downloadUrl: data.data?.download_url || data.results_url
    }
    
    // Unsubscribe from WebSocket
    if (unsubscribeWebSocket.value) {
      unsubscribeWebSocket.value()
      unsubscribeWebSocket.value = null
    }
  } else if (data.type === 'error' || data.status === 'failed') {
    docProcessingStatus.value = 'failed'
    translatingDoc.value = false
    
    const errorMessage = data.error || data.message || 'Translation failed'
    console.error('Translation error:', errorMessage)
    alert(`Translation failed: ${errorMessage}`)
    
    // Unsubscribe from WebSocket
    if (unsubscribeWebSocket.value) {
      unsubscribeWebSocket.value()
      unsubscribeWebSocket.value = null
    }
  }
}

const cancelDocProcessing = () => {
  docProcessingStatus.value = 'cancelled'
  translatingDoc.value = false
  
  // Unsubscribe from WebSocket
  if (unsubscribeWebSocket.value) {
    unsubscribeWebSocket.value()
    unsubscribeWebSocket.value = null
  }
  
  // TODO: Call backend cancel endpoint if implemented
  // translationService.cancelJob(docJobId.value)
}

const retryDocProcessing = () => {
  translateDocument()
}

const downloadTranslatedDoc = async () => {
  if (!docResults.value || !docResults.value.jobId) return
  
  try {
    await translationService.downloadResults(
      docResults.value.jobId, 
      `translation_results_${docResults.value.jobId}.zip`
    )
  } catch (error) {
    console.error('Download error:', error)
    alert(`Failed to download translated document: ${error.message || 'Unknown error'}`)
  }
}


const saveToRecentJobs = () => {
  const recentJobs = JSON.parse(localStorage.getItem('recentJobs') || '[]')
  recentJobs.unshift({
    id: docJobId.value,
    service: 'translation',
    fileName: selectedDocument.value.name,
    timestamp: new Date().toISOString(),
    status: 'completed'
  })
  localStorage.setItem('recentJobs', JSON.stringify(recentJobs.slice(0, 10)))
}

// Fetch supported languages on mount
const fetchLanguages = async () => {
  loadingLanguages.value = true
  languageError.value = null
  
  try {
    const response = await translationService.getLanguages()
    
    // The response has a 'languages' array based on the backend implementation
    if (response.languages && Array.isArray(response.languages)) {
      commonLanguages.value = response.languages
        .map(lang => ({
          code: lang.code,
          name: lang.name || lang.native_name || lang.code
        }))
        .sort((a, b) => a.name.localeCompare(b.name))
      
      // Select popular languages
      const popularCodes = ['es', 'fr', 'de', 'zh-Hans', 'ja', 'ar', 'hi', 'pt', 'ru', 'ko']
      popularLanguages.value = commonLanguages.value
        .filter(lang => popularCodes.includes(lang.code))
        .slice(0, 5)
    } else {
      // Fallback to default languages if API doesn't return expected format
      console.warn('Unexpected language format, using defaults:', response)
      setDefaultLanguages()
    }
  } catch (error) {
    console.error('Failed to fetch languages:', error)
    languageError.value = error.message
    // Use default languages as fallback
    setDefaultLanguages()
  } finally {
    loadingLanguages.value = false
  }
}

// Set default languages as fallback
const setDefaultLanguages = () => {
  commonLanguages.value = [
    { code: 'en', name: 'English' },
    { code: 'es', name: 'Spanish' },
    { code: 'fr', name: 'French' },
    { code: 'de', name: 'German' },
    { code: 'it', name: 'Italian' },
    { code: 'pt', name: 'Portuguese' },
    { code: 'ru', name: 'Russian' },
    { code: 'zh-Hans', name: 'Chinese (Simplified)' },
    { code: 'ja', name: 'Japanese' },
    { code: 'ko', name: 'Korean' },
    { code: 'ar', name: 'Arabic' },
    { code: 'hi', name: 'Hindi' },
    { code: 'nl', name: 'Dutch' },
    { code: 'pl', name: 'Polish' },
    { code: 'tr', name: 'Turkish' },
    { code: 'vi', name: 'Vietnamese' },
    { code: 'th', name: 'Thai' },
    { code: 'sv', name: 'Swedish' },
    { code: 'da', name: 'Danish' },
    { code: 'no', name: 'Norwegian' }
  ]
  
  popularLanguages.value = [
    { code: 'es', name: 'Spanish' },
    { code: 'fr', name: 'French' },
    { code: 'de', name: 'German' },
    { code: 'zh-Hans', name: 'Chinese' },
    { code: 'ja', name: 'Japanese' }
  ]
}

// Lifecycle hooks
onMounted(() => {
  fetchLanguages()
})

onUnmounted(() => {
  // Cleanup WebSocket subscription
  if (unsubscribeWebSocket.value) {
    unsubscribeWebSocket.value()
    unsubscribeWebSocket.value = null
  }
})
</script>