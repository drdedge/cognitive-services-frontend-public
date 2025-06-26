<template>
  <div
    @drop="handleDrop"
    @dragover.prevent
    @dragenter.prevent
    @dragleave="dragging = false"
    :class="[
      'relative border-2 border-dashed rounded-lg p-6 text-center hover:border-gray-400 transition-colors',
      dragging ? 'border-primary bg-blue-50' : 'border-gray-300',
      uploading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
    ]"
  >
    <input
      ref="fileInput"
      type="file"
      :accept="accept"
      :multiple="multiple"
      @change="handleFileSelect"
      class="hidden"
      :disabled="uploading"
    />

    <div @click="!uploading && $refs.fileInput.click()">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
      </svg>
      <p class="mt-2 text-sm text-gray-600">
        {{ placeholder || 'Drag and drop your file here, or click to select' }}
      </p>
      <p class="text-xs text-gray-500 mt-1">
        {{ accept ? `Accepted formats: ${accept}` : 'All file types accepted' }}
      </p>
      <p v-if="maxSize" class="text-xs text-gray-500">
        Maximum file size: {{ formatFileSize(maxSize) }}
      </p>
    </div>

    <!-- Upload Progress -->
    <div v-if="uploading" class="absolute inset-0 bg-white bg-opacity-90 flex items-center justify-center rounded-lg">
      <div class="text-center">
        <svg class="animate-spin h-10 w-10 text-primary mx-auto" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <p class="mt-2 text-sm text-gray-600">Uploading...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  accept: {
    type: String,
    default: ''
  },
  multiple: {
    type: Boolean,
    default: false
  },
  maxSize: {
    type: Number,
    default: null
  },
  uploading: {
    type: Boolean,
    default: false
  },
  placeholder: {
    type: String,
    default: null
  }
})

const emit = defineEmits(['files-dropped'])

const dragging = ref(false)
const fileInput = ref(null)

const handleDrop = (e) => {
  e.preventDefault()
  dragging.value = false
  
  if (props.uploading) return
  
  const files = Array.from(e.dataTransfer.files)
  validateAndEmit(files)
}

const handleFileSelect = (e) => {
  const files = Array.from(e.target.files)
  validateAndEmit(files)
}

const validateAndEmit = (files) => {
  // Filter by accept attribute if provided
  let validFiles = files
  
  if (props.accept) {
    const acceptedExtensions = props.accept.split(',').map(ext => ext.trim().toLowerCase())
    validFiles = files.filter(file => {
      const ext = `.${file.name.split('.').pop().toLowerCase()}`
      return acceptedExtensions.includes(ext)
    })
  }
  
  // Check file size if maxSize is set
  if (props.maxSize) {
    validFiles = validFiles.filter(file => file.size <= props.maxSize)
  }
  
  // Limit to single file if multiple is false
  if (!props.multiple && validFiles.length > 0) {
    validFiles = [validFiles[0]]
  }
  
  if (validFiles.length > 0) {
    emit('files-dropped', validFiles)
  }
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>