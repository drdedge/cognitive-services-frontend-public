import { ref } from 'vue'
import { useApi } from './useApi'
import { useWebSocket } from './useWebSocket'

export function useDocumentIntelligence() {
  const { api, post } = useApi()
  const { connect, disconnect } = useWebSocket()
  
  const processing = ref(false)
  const results = ref(null)

  const processDocument = async (file, options, progressCallback) => {
    processing.value = true
    results.value = null

    try {
      // Create FormData
      const formData = new FormData()
      formData.append('file', file)
      formData.append('extract_tables', options.extractTables)
      formData.append('extract_text', options.extractText)
      formData.append('output_format', options.outputFormat)

      // Upload and start processing
      const response = await post('/api/document-intelligence/process', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      // Connect to WebSocket for progress updates
      if (response.task_id && progressCallback) {
        connect(response.task_id, (message) => {
          if (message.type === 'progress') {
            progressCallback(message.progress, message.message, message.data)
          } else if (message.type === 'error') {
            progressCallback(0, message.error, null)
          }
        })
      }

      return response
    } catch (error) {
      console.error('Document processing error:', error)
      throw error
    } finally {
      processing.value = false
    }
  }

  const getProcessingStatus = async (taskId) => {
    try {
      const response = await api.get(`/api/document-intelligence/status/${taskId}`)
      return response.data
    } catch (error) {
      console.error('Status check error:', error)
      throw error
    }
  }

  const downloadResult = async (taskId, fileType) => {
    try {
      const response = await api.get(`/api/document-intelligence/download/${taskId}/${fileType}`, {
        responseType: 'blob',
      })

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `${taskId}_${fileType}.${fileType}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Download error:', error)
      throw error
    }
  }

  return {
    processing,
    results,
    processDocument,
    getProcessingStatus,
    downloadResult,
  }
}