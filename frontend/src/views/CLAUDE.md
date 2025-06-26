# Views Documentation

## Overview
Views are page-level components that represent different routes in the application. Each view orchestrates multiple components to create a complete user experience.

## View Architecture

### HomeView.vue
**Route**: `/`
**Purpose**: Landing page with service selection dashboard

**Features**:
- Service cards grid (3 services)
- Recent jobs display
- Quick stats summary
- Navigation to specific services

**Data Flow**:
```
HomeView
├── Fetches recent jobs from store
├── Displays ServiceCard components
└── Routes to service-specific views
```

### DocumentIntelligenceView.vue
**Route**: `/document-intelligence`
**Purpose**: Document processing with table extraction and analysis

**Workflow**:
1. File upload (PDF, DOCX, images)
2. Processing options selection
3. Cost estimation
4. Processing with real-time updates
5. Results display with downloads

**Components Used**:
- `FileUpload` - Document upload
- `ProcessingOptions` - Output format, confidence settings
- `CostEstimator` - Price calculation
- `ProcessingStatus` - Real-time progress
- `ResultsDisplay` - Tables, markdown, confidence scores

**State Management**:
```js
const documentStore = useDocumentStore()
const { currentJob, processDocument } = documentStore
```

### TranslationView.vue
**Route**: `/translation`
**Purpose**: Text and document translation interface

**Features**:
- Toggle between text input and file upload
- Language detection and selection
- Side-by-side preview
- Multiple output formats

**Workflow**:
1. Input method selection (text/file)
2. Source/target language selection
3. Translation preview
4. Export in original format

**Unique Components**:
- `InputMethodToggle` - Switch text/file
- `LanguageSelector` - Dropdowns with search
- `TranslationPreview` - Side-by-side view
- `CharacterCounter` - Real-time count

### TranscriptionView.vue
**Route**: `/transcription`
**Purpose**: Audio to text conversion with editing

**Supported Formats**: WAV, MP3, M4A, OGG
**Max Duration**: 2 hours

**Features**:
- Audio file upload with validation
- Language and option selection
- Audio player with controls
- Editable transcript
- Multiple export formats (TXT, SRT, VTT)

**Components**:
- `AudioUpload` - Specialized for audio files
- `TranscriptionOptions` - Language, profanity filter
- `AudioPlayer` - Playback with waveform
- `TranscriptEditor` - Rich text editing

## Common Patterns

### View Template Structure
```vue
<template>
  <div class="view-container">
    <!-- Page Header -->
    <header class="view-header">
      <h1 class="text-3xl font-bold text-text-color">{{ title }}</h1>
      <p class="text-gray-600">{{ description }}</p>
    </header>

    <!-- Main Content -->
    <main class="view-content">
      <!-- Step 1: Input -->
      <section class="input-section">
        <!-- Input components -->
      </section>

      <!-- Step 2: Options -->
      <section class="options-section" v-if="hasInput">
        <!-- Option components -->
      </section>

      <!-- Step 3: Process -->
      <section class="action-section" v-if="canProcess">
        <!-- Action buttons -->
      </section>

      <!-- Step 4: Results -->
      <section class="results-section" v-if="hasResults">
        <!-- Result components -->
      </section>
    </main>
  </div>
</template>
```

### State Management Pattern
```js
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProcessingStore } from '@/stores/processing'
import { useNotifications } from '@/composables/useNotifications'

// Store & Router
const router = useRouter()
const processingStore = useProcessingStore()
const { notify } = useNotifications()

// Local State
const files = ref([])
const options = ref({})
const processing = ref(false)
const results = ref(null)

// Computed
const canProcess = computed(() => 
  files.value.length > 0 && !processing.value
)

// Methods
const processFiles = async () => {
  processing.value = true
  try {
    const job = await processingStore.createJob({
      files: files.value,
      options: options.value
    })
    
    // Navigate to status or wait for completion
    results.value = await job.waitForCompletion()
    notify.success('Processing complete!')
  } catch (error) {
    notify.error(error.message)
  } finally {
    processing.value = false
  }
}

// Lifecycle
onMounted(() => {
  // Initialize view
})
</script>
```

### Responsive Design
```vue
<style scoped>
.view-container {
  @apply max-w-7xl mx-auto px-4 py-8;
}

.view-header {
  @apply mb-8 text-center md:text-left;
}

.view-content {
  @apply grid gap-8 lg:grid-cols-2;
}

/* Mobile-first sections */
.input-section,
.options-section,
.results-section {
  @apply bg-white rounded-lg shadow-md p-6;
}

/* Desktop layout */
@media (min-width: 1024px) {
  .input-section {
    @apply col-span-1;
  }
  
  .results-section {
    @apply col-span-2;
  }
}
</style>
```

## Navigation Guards

### Authentication Check
```js
// In router configuration
{
  path: '/document-intelligence',
  component: DocumentIntelligenceView,
  beforeEnter: (to, from, next) => {
    const auth = useAuthStore()
    if (!auth.isAuthenticated) {
      next('/login')
    } else {
      next()
    }
  }
}
```

### Unsaved Changes Warning
```js
// In view component
const hasUnsavedChanges = computed(() => 
  files.value.length > 0 && !results.value
)

onBeforeRouteLeave((to, from, next) => {
  if (hasUnsavedChanges.value) {
    const answer = window.confirm('Leave without processing files?')
    next(answer)
  } else {
    next()
  }
})
```

## Testing Views

### Integration Test Example
```js
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import DocumentIntelligenceView from './DocumentIntelligenceView.vue'

describe('DocumentIntelligenceView', () => {
  it('completes full workflow', async () => {
    const wrapper = mount(DocumentIntelligenceView, {
      global: {
        plugins: [createTestingPinia()]
      }
    })
    
    // Upload file
    const file = new File(['content'], 'test.pdf')
    await wrapper.findComponent({ name: 'FileUpload' })
      .vm.$emit('files-selected', [file])
    
    // Set options
    await wrapper.find('[data-test="extract-tables"]').setChecked()
    
    // Process
    await wrapper.find('[data-test="process-btn"]').trigger('click')
    
    // Check results
    expect(wrapper.find('.results-section').exists()).toBe(true)
  })
})
```