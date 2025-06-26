import { ref } from 'vue'
import { useApi } from './useApi'
import { useWebSocket } from './useWebSocket'

export function useTranslation() {
  const { api, get, post } = useApi()
  const { connect, disconnect } = useWebSocket()
  
  const languages = ref([])
  const translating = ref(false)

  const getSupportedLanguages = async () => {
    try {
      const response = await get('/api/translation/languages')
      languages.value = response.languages
      return response.languages
    } catch (error) {
      console.error('Failed to fetch languages:', error)
      throw error
    }
  }

  const translateText = async (text, targetLanguages, sourceLanguage = null) => {
    translating.value = true
    
    try {
      const response = await post('/api/translation/translate', {
        text,
        target_languages: targetLanguages,
        source_language: sourceLanguage,
      })
      
      return response
    } catch (error) {
      console.error('Translation error:', error)
      throw error
    } finally {
      translating.value = false
    }
  }

  const translateDocument = async (file, targetLanguage, sourceLanguage = null, progressCallback) => {
    translating.value = true
    
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('target_language', targetLanguage)
      if (sourceLanguage) {
        formData.append('source_language', sourceLanguage)
      }

      const response = await post('/api/translation/translate-document', formData, {
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
      console.error('Document translation error:', error)
      throw error
    } finally {
      translating.value = false
    }
  }

  const detectLanguage = async (text) => {
    try {
      const response = await post('/api/translation/detect-language', { text })
      return response
    } catch (error) {
      console.error('Language detection error:', error)
      throw error
    }
  }

  const translateBatch = async (texts, targetLanguages, sourceLanguage = null) => {
    try {
      const response = await post('/api/translation/translate-batch', {
        texts,
        target_languages: targetLanguages,
        source_language: sourceLanguage,
      })
      
      return response
    } catch (error) {
      console.error('Batch translation error:', error)
      throw error
    }
  }

  const downloadTranslation = async (taskId) => {
    try {
      const response = await api.get(`/api/translation/download/${taskId}`, {
        responseType: 'blob',
      })

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `translation_${taskId}.txt`)
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
    languages,
    translating,
    getSupportedLanguages,
    translateText,
    translateDocument,
    detectLanguage,
    translateBatch,
    downloadTranslation,
  }
}