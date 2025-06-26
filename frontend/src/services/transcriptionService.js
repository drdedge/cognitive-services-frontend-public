import apiClient, { uploadFile, downloadFile, withRetry } from './apiClient';

const BASE_PATH = '/api/transcription';

/**
 * Transcription Service
 * Handles all API interactions for audio transcription
 */
class TranscriptionService {
  /**
   * Start audio transcription
   * @param {File} file - Audio file to transcribe
   * @param {Object} options - Transcription options
   * @param {string} options.language - Language code (optional, auto-detect if not provided)
   * @param {boolean} options.speakerDiarization - Enable speaker identification
   * @param {string} options.outputFormat - Output format (text, srt, vtt, json)
   * @param {boolean} options.punctuation - Enable punctuation
   * @param {boolean} options.profanityFilter - Enable profanity filtering
   * @param {Function} onProgress - Progress callback for upload
   * @returns {Promise<Object>} Job details including job_id
   */
  async transcribeAudio(file, options = {}, onProgress = null) {
    // Debug logging
    const params = {
      language: options.language || 'en-US',
      enable_diarization: options.speakerDiarization || false,
      max_speakers: options.maxSpeakers || 20
    };
    
    console.log('Transcription request:', {
      url: `${BASE_PATH}/transcribe`,
      file: file.name,
      fileSize: file.size,
      fileType: file.type,
      params: params
    });
    
    return withRetry(async () => {
      const response = await uploadFile(
        `${BASE_PATH}/transcribe`,
        file,
        onProgress,
        params
      );
      return response.data;
    });
  }

  /**
   * Estimate transcription cost
   * @param {Object} params - Cost estimation parameters
   * @param {number} params.duration - Audio duration in seconds
   * @param {number} params.fileSize - File size in bytes
   * @param {string} params.fileType - Audio file type
   * @param {boolean} params.speakerDiarization - If speaker identification is needed
   * @returns {Promise<Object>} Cost estimation details
   */
  async estimateCost(params) {
    const response = await apiClient.post(`${BASE_PATH}/estimate-cost`, {
      duration: params.duration,
      file_size: params.fileSize,
      file_type: params.fileType,
      speaker_diarization: params.speakerDiarization || false,
    });
    return response.data;
  }

  /**
   * Get transcription job status
   * @param {string} jobId - The job ID to check
   * @returns {Promise<Object>} Job status details
   */
  async getStatus(jobId) {
    const response = await apiClient.get(`${BASE_PATH}/status/${jobId}`);
    return response.data;
  }

  /**
   * Poll for job completion
   * @param {string} jobId - The job ID to monitor
   * @param {Function} onStatusUpdate - Callback for status updates
   * @param {number} interval - Polling interval in milliseconds
   * @returns {Promise<Object>} Final job status
   */
  async pollStatus(jobId, onStatusUpdate = null, interval = 3000) {
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          const status = await this.getStatus(jobId);
          
          if (onStatusUpdate) {
            onStatusUpdate(status);
          }

          if (status.status === 'completed') {
            resolve(status);
          } else if (status.status === 'failed') {
            reject(new Error(status.error || 'Transcription failed'));
          } else {
            // Continue polling
            setTimeout(poll, interval);
          }
        } catch (error) {
          reject(error);
        }
      };

      poll();
    });
  }

  /**
   * Download transcription results
   * @param {string} jobId - The job ID
   * @param {string} format - Download format (text, srt, vtt, json, all)
   * @param {string} fileName - Desired filename for download
   * @returns {Promise<void>}
   */
  async downloadResults(jobId, format = 'all', fileName = 'transcript') {
    const url = format === 'all' 
      ? `${BASE_PATH}/results/${jobId}`
      : `${BASE_PATH}/results/${jobId}?format=${format}`;
    
    const extension = format === 'all' ? 'zip' : format;
    return downloadFile(url, `${fileName}.${extension}`);
  }

  /**
   * Get transcription preview (first few lines)
   * @param {string} jobId - The job ID
   * @returns {Promise<Object>} Transcript preview
   */
  async getPreview(jobId) {
    const response = await apiClient.get(`${BASE_PATH}/results/${jobId}/preview`);
    return response.data;
  }

  /**
   * Get supported audio formats
   * @returns {Promise<Array>} List of supported audio formats
   */
  async getSupportedFormats() {
    const response = await apiClient.get(`${BASE_PATH}/supported-formats`);
    return response.data;
  }

  /**
   * Get supported languages
   * @returns {Promise<Array>} List of supported languages for transcription
   */
  async getLanguages() {
    const response = await apiClient.get(`${BASE_PATH}/languages`);
    return response.data;
  }

  /**
   * Cancel a transcription job
   * @param {string} jobId - The job ID to cancel
   * @returns {Promise<Object>} Cancellation result
   */
  async cancelJob(jobId) {
    const response = await apiClient.post(`${BASE_PATH}/cancel/${jobId}`);
    return response.data;
  }

  /**
   * Get audio file metadata (duration, format, etc.)
   * @param {File} file - Audio file to analyze
   * @returns {Promise<Object>} Audio metadata
   */
  async getAudioMetadata(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post(`${BASE_PATH}/analyze-audio`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  /**
   * Create custom vocabulary for better recognition
   * @param {Object} vocabulary - Custom vocabulary details
   * @param {string} vocabulary.name - Vocabulary name
   * @param {Array<string>} vocabulary.phrases - Custom phrases
   * @param {string} vocabulary.language - Language code
   * @returns {Promise<Object>} Created vocabulary details
   */
  async createVocabulary(vocabulary) {
    const response = await apiClient.post(`${BASE_PATH}/vocabulary`, vocabulary);
    return response.data;
  }

  /**
   * Get transcription history
   * @param {Object} params - Query parameters
   * @param {number} params.limit - Number of items to return
   * @param {number} params.offset - Offset for pagination
   * @returns {Promise<Object>} Transcription history
   */
  async getHistory(params = {}) {
    const response = await apiClient.get(`${BASE_PATH}/history`, { params });
    return response.data;
  }
}

// Export singleton instance
export default new TranscriptionService();

// Export class for testing purposes
export { TranscriptionService };