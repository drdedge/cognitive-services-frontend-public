/**
 * Type definitions for API services
 * These provide documentation and IDE support for service methods
 */

/**
 * @typedef {Object} ApiError
 * @property {string} message - Error message
 * @property {number} status - HTTP status code
 * @property {Object} data - Error data from server
 */

/**
 * @typedef {Object} FileValidationResult
 * @property {boolean} valid - Whether file is valid
 * @property {string} [error] - Error message if invalid
 */

/**
 * @typedef {Object} JobStatus
 * @property {string} job_id - Unique job identifier
 * @property {string} status - Status: pending, processing, completed, failed
 * @property {number} progress - Progress percentage (0-100)
 * @property {string} [error] - Error message if failed
 * @property {Object} [results] - Results data if completed
 * @property {string} created_at - Job creation timestamp
 * @property {string} [completed_at] - Job completion timestamp
 */

/**
 * @typedef {Object} CostEstimate
 * @property {number} estimated_cost - Estimated cost in USD
 * @property {string} currency - Currency code (USD)
 * @property {Object} breakdown - Cost breakdown by service
 * @property {string} [warning] - Warning message if any
 */

// Document Intelligence Types

/**
 * @typedef {Object} DocumentProcessOptions
 * @property {string} [analysisType] - Type of analysis (layout, invoice, receipt, etc.)
 * @property {boolean} [enableTables] - Extract tables
 * @property {boolean} [enableKeyValuePairs] - Extract key-value pairs
 * @property {string} [locale] - Document locale
 */

/**
 * @typedef {Object} DocumentResult
 * @property {string} job_id - Job identifier
 * @property {Object} content - Extracted content
 * @property {Array} tables - Extracted tables
 * @property {Array} keyValuePairs - Key-value pairs
 * @property {Object} metadata - Document metadata
 * @property {number} confidence - Overall confidence score
 */

// Translation Types

/**
 * @typedef {Object} TranslationOptions
 * @property {string} targetLanguage - Target language code
 * @property {string} [sourceLanguage] - Source language (auto-detect if not provided)
 * @property {boolean} [preserveFormatting] - Preserve document formatting
 * @property {Array<string>} [customTerms] - Custom terminology
 */

/**
 * @typedef {Object} TranslationResult
 * @property {string} translatedText - Translated text
 * @property {string} sourceLanguage - Detected/provided source language
 * @property {string} targetLanguage - Target language
 * @property {number} confidence - Translation confidence
 * @property {Array} [alternatives] - Alternative translations
 */

/**
 * @typedef {Object} Language
 * @property {string} code - Language code (e.g., 'en', 'es', 'fr')
 * @property {string} name - Language name
 * @property {boolean} [supportsTranslation] - Whether translation is supported
 * @property {boolean} [supportsDetection] - Whether detection is supported
 */

// Transcription Types

/**
 * @typedef {Object} TranscriptionOptions
 * @property {string} [language] - Language code (auto-detect if not provided)
 * @property {boolean} [speakerDiarization] - Enable speaker identification
 * @property {string} [outputFormat] - Output format (text, srt, vtt, json)
 * @property {boolean} [punctuation] - Enable automatic punctuation
 * @property {boolean} [profanityFilter] - Enable profanity filtering
 * @property {Array<string>} [customVocabulary] - Custom vocabulary phrases
 */

/**
 * @typedef {Object} TranscriptionResult
 * @property {string} transcript - Full transcript text
 * @property {Array} segments - Time-segmented transcript
 * @property {Array} [speakers] - Speaker information (if diarization enabled)
 * @property {Object} metadata - Audio metadata
 * @property {number} confidence - Overall confidence score
 * @property {string} language - Detected/specified language
 */

/**
 * @typedef {Object} AudioMetadata
 * @property {number} duration - Duration in seconds
 * @property {string} format - Audio format
 * @property {number} sampleRate - Sample rate in Hz
 * @property {number} channels - Number of audio channels
 * @property {number} bitrate - Bitrate in kbps
 */

// WebSocket Types

/**
 * @typedef {Object} WebSocketMessage
 * @property {string} type - Message type
 * @property {Object} data - Message data
 */

/**
 * @typedef {Object} StatusUpdate
 * @property {string} job_id - Job identifier
 * @property {string} status - Current status
 * @property {number} progress - Progress percentage
 * @property {string} [message] - Status message
 * @property {Object} [data] - Additional data
 */

/**
 * @callback ProgressCallback
 * @param {number} percentage - Upload/download progress (0-100)
 */

/**
 * @callback StatusCallback
 * @param {StatusUpdate} status - Status update
 */

/**
 * @callback ErrorCallback
 * @param {ApiError} error - Error information
 */

// File Types

/**
 * @typedef {Object} SupportedFileTypes
 * @property {Array<string>} extensions - Supported file extensions
 * @property {Array<string>} mimeTypes - Supported MIME types
 * @property {number} maxSize - Maximum file size in bytes
 * @property {number} [maxDuration] - Maximum duration for audio files
 */

/**
 * @typedef {Object} FileInfo
 * @property {string} name - File name
 * @property {number} size - File size in bytes
 * @property {string} type - MIME type
 * @property {string} extension - File extension
 * @property {string} [hash] - File hash
 * @property {number} [duration] - Duration for audio/video files
 */

// Service Configuration

/**
 * @typedef {Object} ServiceConfig
 * @property {string} baseURL - API base URL
 * @property {number} timeout - Request timeout in milliseconds
 * @property {number} maxRetries - Maximum retry attempts
 * @property {Object} headers - Default headers
 */

/**
 * @typedef {Object} WebSocketConfig
 * @property {string} url - WebSocket URL
 * @property {number} maxReconnectAttempts - Maximum reconnection attempts
 * @property {number} reconnectDelay - Initial reconnect delay
 * @property {boolean} autoReconnect - Enable automatic reconnection
 */

export {
  // These are just for documentation - JavaScript doesn't have actual types
  // But IDEs can use these JSDoc comments for autocompletion and validation
};