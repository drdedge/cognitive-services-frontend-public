# Frontend Development Guide

## Overview
Vue 3 + Vite + Tailwind CSS frontend application for Azure Cognitive Services.

## Project Structure
```
frontend/
├── src/
│   ├── components/      # Reusable UI components
│   ├── views/          # Page components (routed views)
│   ├── composables/    # Vue composition API utilities
│   ├── services/       # API communication layer
│   ├── stores/         # Pinia state management
│   ├── router/         # Vue Router configuration
│   ├── assets/         # Static assets (images, fonts)
│   └── styles/         # Global styles and Tailwind config
```

## Quick Start
```bash
cd frontend
npm install
npm run dev
```

### Windows Users - Rollup Fix
If you encounter `Cannot find module @rollup/rollup-win32-x64-msvc`:
```bash
npm install @rollup/rollup-win32-x64-msvc
npm run dev
```

## Component Architecture

### Component-Page Relationships
```
src/
├── App.vue (Root component)
│   ├── components/AppHeader.vue (All pages)
│   ├── components/AppNavigation.vue (Mobile menu - All pages)
│   └── <RouterView> (Dynamic page content)
│
├── views/ (Pages/Routes)
│   ├── DashboardView.vue (/)
│   │   └── Uses:
│   │       ├── components/ServiceCard.vue (×3)
│   │       ├── components/LoadingSpinner.vue
│   │       └── services/apiClient.js
│   │
│   ├── DocumentIntelligenceView.vue (/document-intelligence)
│   │   └── Uses:
│   │       ├── components/FileUpload.vue
│   │       ├── components/CostEstimator.vue
│   │       ├── components/ProcessingStatus.vue
│   │       ├── components/ErrorAlert.vue
│   │       ├── composables/useWebSocket.js
│   │       ├── composables/useNotifications.js
│   │       └── services/documentIntelligence.js
│   │
│   ├── TranslationView.vue (/translation)
│   │   └── Uses:
│   │       ├── components/FileUpload.vue
│   │       ├── components/CostEstimator.vue
│   │       ├── components/ProcessingStatus.vue
│   │       ├── components/ErrorAlert.vue
│   │       ├── composables/useWebSocket.js
│   │       └── services/translation.js
│   │
│   └── TranscriptionView.vue (/transcription)
│       └── Uses:
│           ├── components/FileUpload.vue
│           ├── components/CostEstimator.vue
│           ├── components/ProcessingStatus.vue
│           ├── components/ErrorAlert.vue
│           ├── composables/useWebSocket.js
│           └── services/transcription.js
│
├── components/ (Reusable UI Components)
│   ├── FileUpload.vue
│   │   └── Used by: All service views
│   │   └── Features: Drag-drop, validation, progress
│   │
│   ├── ServiceCard.vue
│   │   └── Used by: DashboardView
│   │   └── Features: Service info, navigation
│   │
│   ├── CostEstimator.vue
│   │   └── Used by: All service views
│   │   └── Features: Price calculation, display
│   │
│   ├── ProcessingStatus.vue
│   │   └── Used by: All service views
│   │   └── Features: Progress bar, status updates
│   │
│   ├── ErrorAlert.vue
│   │   └── Used by: All views
│   │   └── Features: Error display, retry action
│   │
│   └── LoadingSpinner.vue
│       └── Used by: All views
│       └── Features: Loading indicator
│
├── composables/ (Shared Logic)
│   ├── useWebSocket.js
│   │   └── Used by: All service views
│   │   └── Provides: Real-time job updates
│   │
│   ├── useNotifications.js
│   │   └── Used by: All views
│   │   └── Provides: Toast notifications
│   │
│   └── useFileValidation.js
│       └── Used by: FileUpload component
│       └── Provides: File type/size validation
│
└── services/ (API Layer)
    ├── apiClient.js
    │   └── Used by: All other services
    │   └── Provides: HTTP client, auth, error handling
    │
    ├── documentIntelligence.js
    │   └── Used by: DocumentIntelligenceView
    │   └── Endpoints: process, estimate, status, results
    │
    ├── translation.js
    │   └── Used by: TranslationView
    │   └── Endpoints: translate, languages, estimate
    │
    ├── transcription.js
    │   └── Used by: TranscriptionView
    │   └── Endpoints: transcribe, estimate, status
    │
    └── websocket.js
        └── Used by: useWebSocket composable
        └── Provides: WebSocket connection management
```

### Component Data Flow
```
View Component (e.g., DocumentIntelligenceView)
     │
     ├── Imports components
     │   ├── FileUpload (file selection)
     │   ├── CostEstimator (pricing display)
     │   └── ProcessingStatus (progress tracking)
     │
     ├── Uses composables
     │   ├── useWebSocket (real-time updates)
     │   └── useNotifications (user feedback)
     │
     └── Calls services
         └── documentIntelligence.js (API calls)
             └── apiClient.js (HTTP handling)
```

## Styling Guide

### Color Scheme
```css
/* CSS Variables defined in style.css */
:root {
  --background: #F5F9FA;       /* Main background */
  --header-bg: #283857;        /* Header/navigation */
  --primary-action: #4F78AB;   /* Buttons, links */
  --text-color: #3B5781;       /* Body text */
  --highlight: #4F78AB;        /* Highlights, accents */
  --success: #28a745;          /* Success states */
  --warning: #ffc107;          /* Warnings */
}
```

### Tailwind Custom Classes
```js
// tailwind.config.js extensions
colors: {
  'background': 'var(--background)',
  'header-bg': 'var(--header-bg)',
  'primary-action': 'var(--primary-action)',
  'text-color': 'var(--text-color)',
  'highlight': 'var(--highlight)',
  'success': 'var(--success)',
  'warning': 'var(--warning)',
}
```

## Component Development

### Component Template
```vue
<template>
  <div class="component-name">
    <!-- Component content -->
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Props
const props = defineProps({
  propName: {
    type: String,
    required: true
  }
})

// Emits
const emit = defineEmits(['event-name'])

// State
const state = ref(initialValue)

// Computed
const computedValue = computed(() => {
  return state.value
})

// Methods
const handleAction = () => {
  emit('event-name', payload)
}
</script>

<style scoped>
/* Component-specific styles */
</style>
```

## State Management (Pinia)

### Store Structure
```js
// stores/processing.js
export const useProcessingStore = defineStore('processing', () => {
  // State
  const jobs = ref([])
  const activeJob = ref(null)
  
  // Getters
  const pendingJobs = computed(() => 
    jobs.value.filter(job => job.status === 'pending')
  )
  
  // Actions
  const createJob = async (jobData) => {
    const job = await api.createJob(jobData)
    jobs.value.push(job)
    return job
  }
  
  return {
    jobs,
    activeJob,
    pendingJobs,
    createJob
  }
})
```

## API Integration

### Backend Structure Overview

The backend is built with FastAPI and follows a modular architecture:

```
backend/
├── main.py                 # FastAPI app, middleware, WebSocket endpoint
├── api/                    # API endpoints by service
│   ├── document_intelligence.py
│   ├── translation.py
│   └── transcription.py
├── services/               # Business logic implementation
│   ├── document_intelligence/
│   │   ├── service.py          # Main service class
│   │   ├── processor.py        # Document processing logic
│   │   ├── table_extractor.py  # Table extraction
│   │   └── confidence_dashboard.py  # Visualization
│   ├── translation/        # Translation service (pending)
│   ├── transcription/      # Transcription service (pending)
│   ├── storage/            # Azure Blob Storage operations
│   └── websocket/          # WebSocket connection management
├── models/                 # Pydantic models for validation
├── utils/                  # Shared utilities
│   ├── azure_clients.py    # Azure SDK management
│   ├── file_handler.py     # File operations
│   ├── job_manager.py      # Job queue management
│   └── websocket_manager.py # WebSocket broadcasting
└── tests/                  # Comprehensive test suite
```

### API Endpoints Reference

#### Document Intelligence Service (✅ Fully Operational)
```
POST   /api/document-intelligence/process
       Body: FormData with file, analysis_type, extract_tables, etc.
       Returns: { job_id, status, created_at }

POST   /api/document-intelligence/estimate-cost
       Body: { file_size_bytes, file_type }
       Returns: { estimated_cost_usd, estimated_pages }

GET    /api/document-intelligence/status/{job_id}
       Returns: { job_id, status, progress, message }

GET    /api/document-intelligence/results/{job_id}
       Returns: File download (ZIP with all extracted content)
```

#### Translation Service (🚧 In Progress)
```
POST   /api/translation/translate-text
       Body: { text, source_language, target_language }
       Returns: { translated_text, detected_language }

POST   /api/translation/translate-document
       Body: FormData with file and language settings
       Returns: { job_id, status }

GET    /api/translation/languages
       Returns: { languages: [...] }
```

#### Transcription Service (🚧 In Progress)
```
POST   /api/transcription/transcribe
       Body: FormData with audio file and options
       Returns: { job_id, status }

GET    /api/transcription/status/{job_id}
       Returns: { job_id, status, progress }

GET    /api/transcription/results/{job_id}
       Returns: File download (transcript in requested format)
```

#### WebSocket Connection
```
WS     /ws/{job_id}
       Sends: { type, job_id, status, progress, data }
```

### Service Layer Pattern
```js
// services/apiClient.js - Base HTTP client with retry logic
import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor for auth and logging
apiClient.interceptors.request.use(config => {
  // Add auth token if available
  const token = localStorage.getItem('auth_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  
  // Log request in development
  if (import.meta.env.DEV) {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
  }
  
  return config
})

// Response interceptor with retry logic
apiClient.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config
    
    // Retry logic for 5xx errors
    if (error.response?.status >= 500 && !originalRequest._retry) {
      originalRequest._retry = true
      await new Promise(resolve => setTimeout(resolve, 1000))
      return apiClient(originalRequest)
    }
    
    // Handle specific error cases
    if (error.response?.status === 401) {
      // Clear auth and redirect to login
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    
    return Promise.reject(error)
  }
)

export default apiClient
```

### Backend Communication Flow

```
1. File Upload & Processing Flow:
   Frontend                    Backend
      │                           │
      ├─POST /process────────────▶│ Create job
      │◀─────{job_id}─────────────┤ Return immediately
      │                           │
      ├─WS /ws/{job_id}──────────▶│ Connect WebSocket
      │◀──{progress: 10%}─────────┤ Progress updates
      │◀──{progress: 50%}─────────┤ Real-time status
      │◀──{progress: 100%}────────┤ Processing complete
      │                           │
      ├─GET /results/{job_id}────▶│ Download results
      │◀────results.zip───────────┤ ZIP file stream

2. WebSocket Message Format:
   {
     "type": "job_update",
     "job_id": "uuid-here",
     "status": "processing",
     "progress": {
       "percentage": 45,
       "current_step": "Extracting tables",
       "message": "Found 3 tables"
     }
   }

3. Error Response Format:
   {
     "error": {
       "code": "FILE_TOO_LARGE",
       "message": "File size exceeds 50MB limit",
       "details": {
         "max_size_mb": 50,
         "file_size_mb": 75.5
       }
     }
   }
```

### Service Implementation Examples

```js
// services/documentIntelligence.js
import apiClient from './apiClient'

export const documentIntelligenceService = {
  async processDocument(file, options) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('analysis_type', options.analysisType || 'layout')
    formData.append('extract_tables', options.extractTables ?? true)
    formData.append('extract_text', options.extractText ?? true)
    formData.append('output_format', options.outputFormat || 'markdown')
    
    const response = await apiClient.post(
      '/api/document-intelligence/process',
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
          options.onUploadProgress?.(percentCompleted)
        }
      }
    )
    
    return response.data
  },
  
  async getStatus(jobId) {
    const response = await apiClient.get(
      `/api/document-intelligence/status/${jobId}`
    )
    return response.data
  },
  
  async downloadResults(jobId) {
    const response = await apiClient.get(
      `/api/document-intelligence/results/${jobId}`,
      { responseType: 'blob' }
    )
    
    // Create download link
    const url = window.URL.createObjectURL(response.data)
    const link = document.createElement('a')
    link.href = url
    link.download = `results_${jobId}.zip`
    link.click()
    window.URL.revokeObjectURL(url)
  }
}
```

## Composables

### Example Composable
```js
// composables/useFileUpload.js
import { ref } from 'vue'
import { useNotifications } from './useNotifications'

export function useFileUpload(options = {}) {
  const files = ref([])
  const uploading = ref(false)
  const progress = ref(0)
  const { notify } = useNotifications()
  
  const validateFile = (file) => {
    if (options.maxSize && file.size > options.maxSize) {
      notify.error(`File size exceeds ${options.maxSize} bytes`)
      return false
    }
    if (options.accept && !options.accept.includes(file.type)) {
      notify.error('Invalid file type')
      return false
    }
    return true
  }
  
  const upload = async (file) => {
    if (!validateFile(file)) return
    
    uploading.value = true
    try {
      // Upload logic
      files.value.push(file)
      notify.success('File uploaded successfully')
    } catch (error) {
      notify.error('Upload failed')
    } finally {
      uploading.value = false
    }
  }
  
  return {
    files,
    uploading,
    progress,
    upload
  }
}
```

## Testing

### Component Testing
```js
// tests/components/FileUpload.spec.js
import { mount } from '@vue/test-utils'
import FileUpload from '@/components/FileUpload.vue'

describe('FileUpload', () => {
  it('emits file-selected event when file is dropped', async () => {
    const wrapper = mount(FileUpload)
    
    const file = new File(['content'], 'test.pdf', { type: 'application/pdf' })
    await wrapper.vm.handleDrop({ dataTransfer: { files: [file] } })
    
    expect(wrapper.emitted('file-selected')).toBeTruthy()
    expect(wrapper.emitted('file-selected')[0][0]).toBe(file)
  })
})
```

## Build & Deployment

### Development
```bash
npm run dev          # Start dev server
npm run test         # Run tests
npm run lint         # Lint code
```

### Production
```bash
npm run build        # Build for production
npm run preview      # Preview production build
```

### Docker
```dockerfile
FROM node:18-alpine as builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```