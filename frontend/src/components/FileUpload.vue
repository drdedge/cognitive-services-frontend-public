<template>
  <div class="file-upload-container">
    <!-- Drag and Drop Area -->
    <div
      @drop="handleDrop"
      @dragover.prevent
      @dragenter.prevent="handleDragEnter"
      @dragleave="handleDragLeave"
      :class="[
        'relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200',
        isDragging ? 'border-[#4F78AB] bg-blue-50 scale-[1.02]' : 'border-gray-300 hover:border-gray-400',
        isUploading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
      ]"
    >
      <input
        ref="fileInput"
        type="file"
        :accept="accept"
        :multiple="multiple"
        @change="handleFileSelect"
        class="hidden"
        :disabled="isUploading"
      />

      <div @click="!isUploading && $refs.fileInput.click()" class="space-y-4">
        <!-- Upload Icon -->
        <svg class="mx-auto h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" 
                d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
        </svg>
        
        <!-- Instructions -->
        <div>
          <p class="text-base font-medium text-[#3B5781]">
            Drop files here or click to browse
          </p>
          <p class="text-sm text-gray-500 mt-1">
            {{ accept ? `Accepted formats: ${formatAcceptedTypes(accept)}` : 'All file types accepted' }}
          </p>
          <p v-if="maxSize" class="text-sm text-gray-500">
            Maximum file size: {{ formatFileSize(maxSize) }}
          </p>
        </div>
      </div>

      <!-- Upload Progress Overlay -->
      <div v-if="isUploading" class="absolute inset-0 bg-white bg-opacity-95 flex items-center justify-center rounded-lg">
        <div class="text-center space-y-4">
          <svg class="animate-spin h-12 w-12 text-[#4F78AB] mx-auto" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" 
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <div>
            <p class="text-sm font-medium text-[#3B5781]">Uploading files...</p>
            <div class="w-48 bg-gray-200 rounded-full h-2 mt-2">
              <div class="bg-[#4F78AB] h-2 rounded-full transition-all duration-300" 
                   :style="`width: ${uploadProgress}%`"></div>
            </div>
            <p class="text-xs text-gray-500 mt-1">{{ uploadProgress }}%</p>
          </div>
        </div>
      </div>
    </div>

    <!-- File Preview Section -->
    <div v-if="uploadedFiles.length > 0" class="mt-6 space-y-3">
      <h3 class="text-sm font-medium text-[#3B5781]">Uploaded Files</h3>
      <div class="grid gap-3">
        <div v-for="(file, index) in uploadedFiles" :key="index" 
             class="flex items-center p-3 bg-gray-50 rounded-lg border border-gray-200">
          <!-- File Preview -->
          <div class="flex-shrink-0 mr-3">
            <img v-if="isImageFile(file)" :src="file.preview" alt="Preview" 
                 class="h-12 w-12 object-cover rounded">
            <div v-else class="h-12 w-12 bg-gray-200 rounded flex items-center justify-center">
              <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
          </div>
          
          <!-- File Info -->
          <div class="flex-1 min-w-0">
            <p class="text-sm font-medium text-[#3B5781] truncate">{{ file.name }}</p>
            <p class="text-xs text-gray-500">{{ formatFileSize(file.size) }}</p>
          </div>
          
          <!-- Remove Button -->
          <button
            @click="removeFile(index)"
            class="ml-2 p-1.5 text-gray-400 hover:text-red-500 transition-colors"
            :disabled="isUploading"
          >
            <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

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
    default: null // in bytes
  }
})

const emit = defineEmits(['files-selected', 'upload-error'])

// State
const isDragging = ref(false)
const isUploading = ref(false)
const uploadProgress = ref(0)
const uploadedFiles = ref([])
const fileInput = ref(null)

// Drag counter to handle nested elements
let dragCounter = 0

// Methods
const handleDragEnter = (e) => {
  e.preventDefault()
  dragCounter++
  isDragging.value = true
}

const handleDragLeave = (e) => {
  e.preventDefault()
  dragCounter--
  if (dragCounter === 0) {
    isDragging.value = false
  }
}

const handleDrop = async (e) => {
  e.preventDefault()
  isDragging.value = false
  dragCounter = 0
  
  if (isUploading.value) return
  
  const files = Array.from(e.dataTransfer.files)
  await processFiles(files)
}

const handleFileSelect = async (e) => {
  const files = Array.from(e.target.files)
  await processFiles(files)
}

const processFiles = async (files) => {
  // Validate files
  const validationResults = validateFiles(files)
  
  if (validationResults.errors.length > 0) {
    emit('upload-error', validationResults.errors)
    return
  }
  
  // Create file objects with preview
  const processedFiles = await Promise.all(
    validationResults.validFiles.map(async (file) => {
      const fileObj = {
        name: file.name,
        size: file.size,
        type: file.type,
        file: file,
        preview: null
      }
      
      // Generate preview for images
      if (isImageFile(file)) {
        fileObj.preview = await generateImagePreview(file)
      }
      
      return fileObj
    })
  )
  
  // Add to uploaded files
  if (props.multiple) {
    uploadedFiles.value.push(...processedFiles)
  } else {
    uploadedFiles.value = processedFiles
  }
  
  // Simulate upload progress (replace with actual upload logic)
  await simulateUpload()
  
  // Emit files
  emit('files-selected', uploadedFiles.value)
  
  // Reset file input
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const validateFiles = (files) => {
  const errors = []
  let validFiles = files
  
  // Check file types
  if (props.accept) {
    const acceptedTypes = props.accept.split(',').map(type => type.trim().toLowerCase())
    validFiles = validFiles.filter(file => {
      const fileExt = `.${file.name.split('.').pop().toLowerCase()}`
      const isValid = acceptedTypes.some(type => {
        if (type.startsWith('.')) {
          return fileExt === type
        }
        return file.type.startsWith(type.replace('*', ''))
      })
      
      if (!isValid) {
        errors.push({
          file: file.name,
          error: `File type not accepted. Accepted types: ${formatAcceptedTypes(props.accept)}`
        })
      }
      
      return isValid
    })
  }
  
  // Check file size
  if (props.maxSize) {
    validFiles = validFiles.filter(file => {
      if (file.size > props.maxSize) {
        errors.push({
          file: file.name,
          error: `File size exceeds maximum allowed size of ${formatFileSize(props.maxSize)}`
        })
        return false
      }
      return true
    })
  }
  
  // Check multiple files
  if (!props.multiple && validFiles.length > 1) {
    validFiles = [validFiles[0]]
    errors.push({
      error: 'Only one file can be uploaded at a time'
    })
  }
  
  return { validFiles, errors }
}

const simulateUpload = async () => {
  isUploading.value = true
  uploadProgress.value = 0
  
  // Simulate upload progress
  const interval = setInterval(() => {
    uploadProgress.value += 10
    if (uploadProgress.value >= 100) {
      clearInterval(interval)
      isUploading.value = false
      uploadProgress.value = 0
    }
  }, 200)
  
  return new Promise(resolve => {
    setTimeout(resolve, 2000)
  })
}

const generateImagePreview = (file) => {
  return new Promise((resolve) => {
    const reader = new FileReader()
    reader.onload = (e) => resolve(e.target.result)
    reader.readAsDataURL(file)
  })
}

const removeFile = (index) => {
  uploadedFiles.value.splice(index, 1)
  emit('files-selected', uploadedFiles.value)
}

// Utility functions
const isImageFile = (file) => {
  return file.type?.startsWith('image/') || 
         /\.(jpg|jpeg|png|gif|webp|svg)$/i.test(file.name)
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatAcceptedTypes = (accept) => {
  return accept
    .split(',')
    .map(type => type.trim())
    .map(type => {
      if (type.startsWith('.')) return type.toUpperCase()
      if (type.includes('/')) return type.split('/')[1].toUpperCase()
      return type
    })
    .join(', ')
}
</script>

<style scoped>
/* Add any component-specific styles here */
</style>