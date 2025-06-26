import axios from 'axios'
import { ref } from 'vue'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('auth_token')
      // Redirect to login if needed
    }
    return Promise.reject(error)
  }
)

export function useApi() {
  const loading = ref(false)
  const error = ref(null)

  const request = async (method, url, data = null, options = {}) => {
    loading.value = true
    error.value = null

    try {
      const response = await api({
        method,
        url,
        data,
        ...options,
      })
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail || err.message || 'An error occurred'
      throw err
    } finally {
      loading.value = false
    }
  }

  const get = (url, options) => request('GET', url, null, options)
  const post = (url, data, options) => request('POST', url, data, options)
  const put = (url, data, options) => request('PUT', url, data, options)
  const del = (url, options) => request('DELETE', url, null, options)

  return {
    api,
    loading,
    error,
    get,
    post,
    put,
    del,
  }
}