import axios from 'axios';
import appConfig from './config';

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: appConfig.apiBaseUrl,
  timeout: appConfig.timeout,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for adding auth token and logging
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // Log request in development
    if (appConfig.enableLogging) {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
        params: config.params,
        data: config.data,
      });
    }

    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and logging
apiClient.interceptors.response.use(
  (response) => {
    // Log response in development
    if (appConfig.enableLogging) {
      console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url}`, {
        status: response.status,
        data: response.data,
      });
    }

    return response;
  },
  (error) => {
    // Log error details
    console.error('[API Response Error]', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      message: error.message,
      data: error.response?.data,
    });

    // Handle common error scenarios
    if (error.response) {
      // Server responded with error status
      switch (error.response.status) {
        case 401:
          // Unauthorized - clear auth and redirect to login
          localStorage.removeItem('authToken');
          // In a real app, you'd redirect to login here
          error.message = 'Authentication required. Please log in.';
          break;
        case 403:
          error.message = 'You do not have permission to perform this action.';
          break;
        case 404:
          error.message = 'The requested resource was not found.';
          break;
        case 413:
          error.message = 'The file is too large. Please select a smaller file.';
          break;
        case 429:
          error.message = 'Too many requests. Please try again later.';
          break;
        case 500:
          error.message = 'Server error. Please try again later.';
          break;
        default:
          error.message = error.response.data?.message || 'An unexpected error occurred.';
      }
    } else if (error.request) {
      // Request was made but no response received
      error.message = 'Network error. Please check your connection and try again.';
    } else {
      // Something else happened
      error.message = error.message || 'An unexpected error occurred.';
    }

    return Promise.reject(error);
  }
);

// Helper function to handle file uploads with progress
export const uploadFile = (url, file, onProgress, additionalData = {}) => {
  const formData = new FormData();
  formData.append('file', file);
  
  // Add any additional data to the form
  Object.keys(additionalData).forEach(key => {
    if (additionalData[key] !== undefined && additionalData[key] !== null) {
      formData.append(key, additionalData[key]);
    }
  });

  return apiClient.post(url, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
        onProgress(percentCompleted);
      }
    },
  });
};

// Helper function to download files
export const downloadFile = async (url, fileName) => {
  try {
    const response = await apiClient.get(url, {
      responseType: 'blob',
    });

    // Create a download link
    const downloadUrl = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = downloadUrl;
    link.setAttribute('download', fileName);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(downloadUrl);

    return response;
  } catch (error) {
    throw error;
  }
};

// Retry configuration for resilient requests
export const withRetry = async (fn, retries = appConfig.maxRetries) => {
  if (!appConfig.enableRetries) {
    return fn();
  }
  
  try {
    return await fn();
  } catch (error) {
    if (retries > 0 && (error.response?.status >= 500 || !error.response)) {
      // Retry on server errors or network errors
      await new Promise(resolve => setTimeout(resolve, appConfig.retryDelay));
      return withRetry(fn, retries - 1);
    }
    throw error;
  }
};

export default apiClient;