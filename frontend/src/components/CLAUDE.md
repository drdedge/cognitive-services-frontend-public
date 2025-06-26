# Components Documentation

## Component Library Overview
Reusable Vue 3 components following composition API patterns with TypeScript support.

## Core Components

### FileUpload.vue
**Purpose**: Drag-and-drop file upload with validation and progress tracking

**Props**:
- `accept` (String): Accepted file types (e.g., ".pdf,.docx")
- `maxSize` (Number): Maximum file size in bytes
- `multiple` (Boolean): Allow multiple file selection

**Events**:
- `@files-selected`: Emitted with selected files array
- `@upload-progress`: Progress updates during upload
- `@upload-error`: Error during upload

**Usage**:
```vue
<FileUpload
  accept=".pdf,.docx"
  :max-size="10485760"
  @files-selected="handleFiles"
/>
```

### ServiceSelector.vue
**Purpose**: Display service cards for selection

**Props**:
- `services` (Array): Available services configuration
- `disabled` (Boolean): Disable selection

**Events**:
- `@service-selected`: Emitted with selected service

**Usage**:
```vue
<ServiceSelector
  :services="availableServices"
  @service-selected="selectService"
/>
```

### CostEstimator.vue
**Purpose**: Calculate and display estimated processing costs

**Props**:
- `service` (String): Selected service type
- `files` (Array): Files to process
- `options` (Object): Service-specific options

**Events**:
- `@estimate-calculated`: Cost estimate result
- `@estimate-error`: Estimation error

**Usage**:
```vue
<CostEstimator
  service="document-intelligence"
  :files="selectedFiles"
  :options="processingOptions"
  @estimate-calculated="showCost"
/>
```

### ProcessingStatus.vue
**Purpose**: Real-time job processing status with WebSocket updates

**Props**:
- `jobId` (String): Processing job ID
- `service` (String): Service type for display

**Events**:
- `@processing-complete`: Job completed successfully
- `@processing-error`: Job failed
- `@processing-cancelled`: User cancelled job

**Features**:
- WebSocket connection for real-time updates
- Progress bar with percentage
- Stage descriptions
- Cancel button
- Error display

**Usage**:
```vue
<ProcessingStatus
  :job-id="currentJobId"
  service="translation"
  @processing-complete="handleComplete"
/>
```

### ResultsDisplay.vue
**Purpose**: Display processing results with download options

**Props**:
- `results` (Object): Processing results
- `service` (String): Service type for layout

**Events**:
- `@download-requested`: User wants to download results
- `@preview-opened`: Preview modal requested

**Usage**:
```vue
<ResultsDisplay
  :results="jobResults"
  service="transcription"
  @download-requested="downloadResults"
/>
```

## Common Components

### LoadingSpinner.vue
Simple loading animation component
```vue
<LoadingSpinner size="large" color="primary" />
```

### ErrorAlert.vue
Error message display with optional retry
```vue
<ErrorAlert
  :error="errorMessage"
  dismissible
  @retry="retryAction"
/>
```

### SuccessMessage.vue
Success notification with auto-dismiss
```vue
<SuccessMessage
  message="Upload complete!"
  :duration="3000"
/>
```

## Component Patterns

### Composition API Structure
```vue
<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStore } from '@/composables/useStore'

// Props & Emits
const props = defineProps({...})
const emit = defineEmits([...])

// Composables
const { state, actions } = useStore()

// Local State
const localState = ref(initialValue)

// Computed Properties
const computedProp = computed(() => {
  return localState.value + props.value
})

// Lifecycle
onMounted(() => {
  // Initialize component
})

// Methods
const handleAction = () => {
  emit('action', payload)
}
</script>
```

### Styling Pattern
```vue
<style scoped>
/* Component container */
.component-name {
  @apply relative flex flex-col gap-4 p-4;
}

/* Responsive design */
@media (min-width: 768px) {
  .component-name {
    @apply flex-row;
  }
}

/* State variations */
.component-name--active {
  @apply border-primary-action;
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
  .component-name {
    @apply bg-gray-800 text-white;
  }
}
</style>
```

## Testing Components

### Unit Test Example
```js
import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import FileUpload from './FileUpload.vue'

describe('FileUpload', () => {
  it('validates file size', async () => {
    const wrapper = mount(FileUpload, {
      props: {
        maxSize: 1024 // 1KB
      }
    })
    
    const largeFile = new File(['x'.repeat(2048)], 'large.txt')
    await wrapper.vm.validateFile(largeFile)
    
    expect(wrapper.emitted('upload-error')).toBeTruthy()
  })
})
```

## Accessibility

All components follow WCAG 2.1 AA standards:
- Proper ARIA labels
- Keyboard navigation support
- Focus management
- Screen reader announcements
- Color contrast compliance

## Performance

### Optimization Techniques
- Lazy loading for heavy components
- Virtual scrolling for long lists
- Debounced input handlers
- Memoized expensive computations
- Proper key usage in v-for loops