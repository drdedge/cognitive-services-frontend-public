import { ref } from 'vue'
import { useApi } from './useApi'
import { useWebSocket } from './useWebSocket'

export function useTranscription() {
  const { api, get, post } = useApi()
  const { connect, disconnect } = useWebSocket()
  
  const languages = ref([])
  const transcribing = ref(false)

  const getSupportedLanguages = async () => {
    try {
      const response = await get('/api/transcription/languages')
      languages.value = response.languages
      return response.languages
    } catch (error) {
      console.error('Failed to fetch languages:', error)
      throw error
    }
  }

  const transcribeAudio = async (file, language, options, progressCallback) => {
    transcribing.value = true
    
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('language', language)
      formData.append('enable_diarization', options.enableDiarization)
      formData.append('enable_punctuation', options.enablePunctuation)
      formData.append('output_format', options.outputFormat)

      const response = await post('/api/transcription/transcribe', formData, {
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
      console.error('Transcription error:', error)
      throw error
    } finally {
      transcribing.value = false
    }
  }

  const startRealtimeTranscription = async (language) => {
    try {
      const response = await post('/api/transcription/transcribe-realtime', {
        language,
      })
      
      return response
    } catch (error) {
      console.error('Realtime transcription error:', error)
      throw error
    }
  }

  const downloadTranscription = async (taskId, format = 'text') => {
    try {
      const response = await api.get(`/api/transcription/download/${taskId}?format=${format}`, {
        responseType: 'blob',
      })

      // Determine file extension based on format
      const extensions = {
        text: 'txt',
        srt: 'srt',
        vtt: 'vtt',
        json: 'json',
      }
      const ext = extensions[format] || 'txt'

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `transcription_${taskId}.${ext}`)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Download error:', error)
      throw error
    }
  }

  const getAudioInsights = async (file, language) => {
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('language', language)

      const response = await post('/api/transcription/audio-insights', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      
      return response
    } catch (error) {
      console.error('Audio insights error:', error)
      throw error
    }
  }

  return {
    languages,
    transcribing,
    getSupportedLanguages,
    transcribeAudio,
    startRealtimeTranscription,
    downloadTranscription,
    getAudioInsights,
  }
}