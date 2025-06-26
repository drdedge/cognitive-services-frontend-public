<template>
  <div class="py-10">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- Header -->
      <div class="mb-8">
        <h1 class="text-3xl font-bold text-[#3B5781]">Transcription</h1>
        <p class="mt-2 text-lg text-gray-600">
          Convert speech to text with high accuracy, supporting multiple languages and audio formats
        </p>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Main Content Area -->
        <div class="lg:col-span-2 space-y-6">
          <!-- Upload Section -->
          <div class="bg-white shadow rounded-lg">
            <div class="px-6 py-4 border-b border-gray-200">
              <h2 class="text-lg font-medium text-[#3B5781]">Upload Audio</h2>
            </div>
            
            <div class="p-6">
              <!-- Language Selection -->
              <div class="mb-6">
                <label class="block text-sm font-medium text-gray-700 mb-2">Audio Language</label>
                <select 
                  v-model="selectedLanguage" 
                  class="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-[#4F78AB] focus:border-[#4F78AB] sm:text-sm"
                >
                  <option v-for="lang in languages" :key="lang.code" :value="lang.code">
                    {{ lang.name }}
                  </option>
                </select>
              </div>

              <!-- Audio Upload -->
              <FileUpload
                @files-selected="handleFilesSelected"
                @upload-error="handleUploadError"
                :accept="acceptedFormats"
                :multiple="false"
                :max-size="104857600"
              />

              <!-- Transcription Options -->
              <div v-if="selectedFile" class="mt-6 space-y-4">
                <h3 class="text-sm font-medium text-[#3B5781] mb-3">Transcription Options</h3>
                
                <div class="space-y-3">
                  <label class="flex items-start">
                    <input
                      type="checkbox"
                      v-model="options.enablePunctuation"
                      class="h-4 w-4 text-[#4F78AB] focus:ring-[#4F78AB] border-gray-300 rounded mt-0.5"
                    />
                    <div class="ml-3">
                      <span class="text-sm font-medium text-gray-700">Enable automatic punctuation</span>
                      <p class="text-xs text-gray-500">Add periods, commas, and other punctuation</p>
                    </div>
                  </label>

                  <label class="flex items-start">
                    <input
                      type="checkbox"
                      v-model="options.enableDiarization"
                      class="h-4 w-4 text-[#4F78AB] focus:ring-[#4F78AB] border-gray-300 rounded mt-0.5"
                    />
                    <div class="ml-3">
                      <span class="text-sm font-medium text-gray-700">Enable speaker diarization</span>
                      <p class="text-xs text-gray-500">Identify and separate different speakers</p>
                    </div>
                  </label>

                  <label class="flex items-start">
                    <input
                      type="checkbox"
                      v-model="options.enableTimestamps"
                      class="h-4 w-4 text-[#4F78AB] focus:ring-[#4F78AB] border-gray-300 rounded mt-0.5"
                    />
                    <div class="ml-3">
                      <span class="text-sm font-medium text-gray-700">Include timestamps</span>
                      <p class="text-xs text-gray-500">Add time markers to transcription</p>
                    </div>
                  </label>
                </div>


                <!-- Transcribe Button -->
                <div class="pt-4">
                  <button
                    @click="transcribeAudio"
                    :disabled="processing"
                    class="w-full sm:w-auto px-6 py-3 bg-[#4F78AB] text-white font-medium rounded-md hover:bg-[#3B5781] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#4F78AB] disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                  >
                    <span v-if="processing" class="flex items-center justify-center">
                      <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Transcribing...
                    </span>
                    <span v-else>Transcribe Audio</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Processing Status -->
          <ProcessingStatus
            v-if="jobId && !results"
            :job-id="jobId"
            :service="{ id: 'transcription', name: 'Transcription' }"
            :status="processingStatus"
            :progress="progress"
            :current-stage="currentStage"
            :stage-details="stageDetails"
            :start-time="startTime"
            @cancel="cancelProcessing"
            @retry="retryProcessing"
          />

          <!-- Results Section -->
          <div v-if="results" class="bg-white shadow rounded-lg">
            <div class="px-6 py-4 border-b border-gray-200">
              <h3 class="text-lg font-medium text-[#3B5781]">Transcription Complete</h3>
            </div>
        
            <div class="p-6">
              <!-- Statistics -->
              <div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
                <div class="bg-gray-50 px-4 py-3 rounded-lg">
                  <dt class="text-xs font-medium text-gray-500 uppercase tracking-wider">Duration</dt>
                  <dd class="mt-1 text-lg font-semibold text-[#3B5781]">
                    {{ formatDuration(results.duration || 0) }}
                  </dd>
                </div>
                <div class="bg-gray-50 px-4 py-3 rounded-lg">
                  <dt class="text-xs font-medium text-gray-500 uppercase tracking-wider">Words</dt>
                  <dd class="mt-1 text-lg font-semibold text-[#3B5781]">
                    {{ results.wordCount || 0 }}
                  </dd>
                </div>
                <div v-if="results.speakerCount" class="bg-gray-50 px-4 py-3 rounded-lg">
                  <dt class="text-xs font-medium text-gray-500 uppercase tracking-wider">Speakers</dt>
                  <dd class="mt-1 text-lg font-semibold text-[#3B5781]">
                    {{ results.speakerCount }}
                  </dd>
                </div>
                <div class="bg-gray-50 px-4 py-3 rounded-lg">
                  <dt class="text-xs font-medium text-gray-500 uppercase tracking-wider">Language</dt>
                  <dd class="mt-1 text-lg font-semibold text-[#3B5781]">
                    {{ getLanguageName(results.language) }}
                  </dd>
                </div>
                <div class="bg-gray-50 px-4 py-3 rounded-lg">
                  <dt class="text-xs font-medium text-gray-500 uppercase tracking-wider">Processing Time</dt>
                  <dd class="mt-1 text-lg font-semibold text-[#3B5781]">
                    {{ Math.round(results.processingTime || 0) }}s
                  </dd>
                </div>
              </div>

              <!-- Download Button -->
              <div class="flex justify-center">
                <button 
                  @click="downloadTranscription" 
                  :disabled="!downloadUrl"
                  class="px-6 py-3 bg-[#4F78AB] text-white font-medium rounded-md hover:bg-[#3B5781] focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#4F78AB] disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center"
                >
                  <svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  Download Results (ZIP)
                </button>
              </div>

              <!-- File Contents Info -->
              <div class="mt-4 text-center text-sm text-gray-600">
                <p>Your download will include:</p>
                <ul class="mt-2 space-y-1">
                  <li>• Transcript in multiple formats (TXT, SRT, VTT, JSON)</li>
                  <li v-if="options.enableDiarization">• Speaker analysis and statistics</li>
                  <li>• Processing metadata and summary</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="lg:col-span-1 space-y-6">
          <!-- Cost Estimator -->
          <CostEstimator
            :service="{ id: 'transcription', name: 'Transcription' }"
            :file-info="fileInfo"
            :options="costOptions"
          />

          <!-- Audio Format Info -->
          <div class="bg-white shadow rounded-lg p-6">
            <h3 class="text-lg font-medium text-[#3B5781] mb-4">Supported Formats</h3>
            <div class="space-y-3">
              <div>
                <h4 class="text-sm font-medium text-gray-700 mb-2">Audio Formats</h4>
                <div class="flex flex-wrap gap-2">
                  <span class="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">WAV</span>
                  <span class="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">MP3</span>
                  <span class="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">M4A</span>
                  <span class="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">FLAC</span>
                  <span class="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">OGG</span>
                  <span class="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">WebM</span>
                </div>
              </div>
              <div>
                <h4 class="text-sm font-medium text-gray-700 mb-2">Max File Size</h4>
                <p class="text-sm text-gray-600">100 MB</p>
              </div>
              <div>
                <h4 class="text-sm font-medium text-gray-700 mb-2">Max Duration</h4>
                <p class="text-sm text-gray-600">2 hours</p>
              </div>
            </div>
          </div>

          <!-- Tips -->
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 class="text-sm font-medium text-blue-900 mb-2">Tips for Best Results</h3>
            <ul class="text-sm text-blue-700 space-y-1">
              <li class="flex items-start">
                <svg class="h-4 w-4 mr-1 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                Use high-quality audio recordings
              </li>
              <li class="flex items-start">
                <svg class="h-4 w-4 mr-1 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                Minimize background noise
              </li>
              <li class="flex items-start">
                <svg class="h-4 w-4 mr-1 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                Speak clearly and at a moderate pace
              </li>
              <li class="flex items-start">
                <svg class="h-4 w-4 mr-1 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                </svg>
                Select the correct language for accuracy
              </li>
            </ul>
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
import transcriptionService from '@/services/transcriptionService'
import websocketService from '@/services/websocketService'

// State
const selectedFile = ref(null)
const selectedLanguage = ref('auto-detect')
const processing = ref(false)
const jobId = ref(null)
const progress = ref(0)
const processingStatus = ref('idle')
const currentStage = ref('Initializing...')
const stageDetails = ref('')
const startTime = ref(null)
const results = ref(null)
const uploadError = ref(null)
const uploadProgress = ref(0)
const audioDuration = ref(null)
const wordCount = ref(null)
const speakerCount = ref(null)
const downloadUrl = ref(null)

// Options
const options = ref({
  enablePunctuation: true,
  enableDiarization: false,
  enableTimestamps: true
})

// Accepted formats
const acceptedFormats = '.wav,.mp3,.mp4,.m4a,.flac,.ogg,.opus,.webm'

// Languages list
const languages = ref([])

// Computed properties
const fileInfo = computed(() => {
  if (!selectedFile.value) return null
  return {
    count: 1,
    totalSize: selectedFile.value.size
  }
})

const costOptions = computed(() => {
  const opts = {}
  if (options.value.enableDiarization) opts.speakerDiarization = true
  if (options.value.enableTimestamps) opts.timestamps = true
  return opts
})

// Methods
const handleFilesSelected = (files) => {
  if (files.length > 0) {
    selectedFile.value = files[0].file
    results.value = null
    jobId.value = null
    uploadError.value = null
  }
}

const handleUploadError = (errors) => {
  uploadError.value = errors[0]?.error || 'Upload failed'
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDuration = (seconds) => {
  if (!seconds) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const formatTimestamp = (seconds) => {
  if (!seconds) return '0:00'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  const ms = Math.floor((seconds % 1) * 100)
  return `${mins}:${secs.toString().padStart(2, '0')}.${ms.toString().padStart(2, '0')}`
}

const getLanguageName = (code) => {
  const lang = languages.value.find(l => l.code === code)
  return lang ? lang.name : code
}

const transcribeAudio = async () => {
  if (!selectedFile.value) return

  try {
    processing.value = true
    processingStatus.value = 'processing'
    startTime.value = new Date()
    progress.value = 0
    results.value = null
    uploadProgress.value = 0
    
    // Prepare transcription options
    const transcriptionOptions = {
      language: selectedLanguage.value === 'auto-detect' ? 'en-US' : selectedLanguage.value,
      speakerDiarization: options.value.enableDiarization,
      maxSpeakers: 20
    }
    
    // Start transcription
    const response = await transcriptionService.transcribeAudio(
      selectedFile.value,
      transcriptionOptions,
      (progressEvent) => {
        uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        progress.value = Math.round(uploadProgress.value * 0.3) // Upload is 30% of total
        currentStage.value = 'Uploading audio file'
        stageDetails.value = `${uploadProgress.value}% complete`
      }
    )
    
    jobId.value = response.job_id
    
    // Subscribe to WebSocket updates
    subscribeToJobUpdates()
    
  } catch (error) {
    console.error('Transcription error:', error)
    processing.value = false
    processingStatus.value = 'failed'
    console.error('Transcription failed:', error.response?.data?.detail?.message || error.message || 'Failed to start transcription')
  }
}

const subscribeToJobUpdates = () => {
  // Subscribe to all event types for this job
  websocketService.subscribe(jobId.value, '*', handleWebSocketUpdate)
}

const handleWebSocketUpdate = (data) => {
  console.log('WebSocket update:', data)
  
  if (data.type === 'job_update' && data.status === 'processing') {
    progress.value = data.progress?.progress_percentage || 0
    currentStage.value = data.progress?.current_step || 'Processing'
    stageDetails.value = data.progress?.message || ''
  } else if (data.type === 'job_completed') {
    processingStatus.value = 'completed'
    progress.value = 100
    currentStage.value = 'Complete'
    stageDetails.value = 'Transcription finished successfully'
    
    // Set results data from the WebSocket message
    if (data.results_url) {
      downloadUrl.value = data.results_url
      console.log('Download URL set:', downloadUrl.value)
    } else {
      console.warn('No results_url in WebSocket message:', data)
    }
    
    if (data.data) {
      audioDuration.value = data.data.duration
      wordCount.value = data.data.word_count
      speakerCount.value = data.data.speakers?.length || 0
      
      results.value = {
        duration: data.data.duration,
        wordCount: data.data.word_count,
        speakerCount: data.data.speakers?.length || 0,
        language: selectedLanguage.value,
        processingTime: Math.round((new Date() - startTime.value) / 1000)
      }
    }
    
    processing.value = false
    
    // Save to recent jobs
    saveToRecentJobs()
    
    console.log('Transcription completed successfully')
  } else if (data.type === 'job_failed') {
    processingStatus.value = 'failed'
    processing.value = false
    console.error('Transcription failed:', data.error || 'An error occurred during transcription')
  }
}

const cancelProcessing = () => {
  processingStatus.value = 'cancelled'
  processing.value = false
}

const retryProcessing = () => {
  transcribeAudio()
}

const downloadTranscription = async () => {
  if (!jobId.value || !downloadUrl.value) return
  
  try {
    const fileName = selectedFile.value 
      ? `transcription_${selectedFile.value.name.split('.')[0]}` 
      : `transcription_${jobId.value}`
    
    await transcriptionService.downloadResults(jobId.value, 'all', fileName)
    console.log('Download started successfully')
  } catch (error) {
    console.error('Download error:', error)
    console.error('Failed to download transcription results')
  }
}

// Lifecycle hooks
onMounted(async () => {
  // Load supported languages
  try {
    const response = await transcriptionService.getLanguages()
    languages.value = response.languages || []
  } catch (error) {
    console.error('Failed to load languages:', error)
    // Use default languages if API fails
    languages.value = [
      { code: 'auto-detect', name: 'Auto-detect' },
      { code: 'en-US', name: 'English (US)' },
      { code: 'es-ES', name: 'Spanish' },
      { code: 'fr-FR', name: 'French' },
      { code: 'de-DE', name: 'German' },
      { code: 'zh-CN', name: 'Chinese (Mandarin)' },
      { code: 'ja-JP', name: 'Japanese' }
    ]
  }
})

onUnmounted(() => {
  // Unsubscribe from WebSocket updates
  if (jobId.value) {
    websocketService.unsubscribe(jobId.value, '*', handleWebSocketUpdate)
  }
})

const saveToRecentJobs = () => {
  const recentJobs = JSON.parse(localStorage.getItem('recentJobs') || '[]')
  recentJobs.unshift({
    id: jobId.value,
    service: 'transcription',
    fileName: selectedFile.value.name,
    timestamp: new Date().toISOString(),
    status: 'completed'
  })
  localStorage.setItem('recentJobs', JSON.stringify(recentJobs.slice(0, 10)))
}
</script>