import apiClient, { uploadFile, downloadFile, withRetry } from './apiClient';

const BASE_PATH = '/api/translation';

/**
 * Translation Service
 * Handles all API interactions for text and document translation
 */
class TranslationService {
  /**
   * Translate text
   * @param {Object} params - Translation parameters
   * @param {string} params.text - Text to translate
   * @param {string} params.targetLanguage - Target language code
   * @param {string} params.sourceLanguage - Source language code (optional, auto-detect if not provided)
   * @returns {Promise<Object>} Translation result
   */
  async translateText(params) {
    return withRetry(async () => {
      const payload = {
        text: params.text,
        target_language: params.targetLanguage,
      };
      // Only include source_language if it's provided and not 'auto'
      if (params.sourceLanguage && params.sourceLanguage !== 'auto') {
        payload.source_language = params.sourceLanguage;
      }
      const response = await apiClient.post(`${BASE_PATH}/translate-text`, payload);
      return response.data;
    });
  }

  /**
   * Translate multiple texts in batch
   * @param {Object} params - Batch translation parameters
   * @param {Array<string>} params.texts - Array of texts to translate
   * @param {string} params.targetLanguage - Target language code
   * @param {string} params.sourceLanguage - Source language code (optional)
   * @returns {Promise<Object>} Batch translation results
   */
  async translateBatch(params) {
    return withRetry(async () => {
      const payload = {
        texts: params.texts,
        target_language: params.targetLanguage,
      };
      // Only include source_language if it's provided and not 'auto'
      if (params.sourceLanguage && params.sourceLanguage !== 'auto') {
        payload.source_language = params.sourceLanguage;
      }
      const response = await apiClient.post(`${BASE_PATH}/translate-batch`, payload);
      return response.data;
    });
  }

  /**
   * Translate a document
   * @param {File} file - Document file to translate
   * @param {Object} options - Translation options
   * @param {string} options.targetLanguage - Target language code
   * @param {string} options.sourceLanguage - Source language code (optional)
   * @param {Function} onProgress - Progress callback for upload
   * @returns {Promise<Object>} Job details including job_id
   */
  async translateDocument(file, options = {}, onProgress = null) {
    return withRetry(async () => {
      const response = await uploadFile(
        `${BASE_PATH}/translate-document`,
        file,
        onProgress,
        {
          target_language: options.targetLanguage,
          source_language: options.sourceLanguage && options.sourceLanguage !== 'auto' ? options.sourceLanguage : undefined,
          ...options
        }
      );
      return response.data;
    });
  }

  /**
   * Get supported languages
   * @returns {Promise<Object>} Object with source and target languages
   */
  async getLanguages() {
    const response = await apiClient.get(`${BASE_PATH}/languages`);
    return response.data;
  }

  /**
   * Detect language of text
   * @param {string} text - Text to analyze
   * @returns {Promise<Object>} Detected language information
   */
  async detectLanguage(text) {
    const response = await apiClient.post(`${BASE_PATH}/detect-language`, { text });
    return response.data;
  }

  /**
   * Estimate translation cost
   * @param {Object} params - Cost estimation parameters
   * @param {number} params.characterCount - Number of characters (for text)
   * @param {number} params.fileSize - File size in bytes (for documents)
   * @param {string} params.fileType - File type/extension
   * @param {string} params.targetLanguage - Target language
   * @param {string} params.sourceLanguage - Source language
   * @returns {Promise<Object>} Cost estimation details
   */
  async estimateCost(params) {
    const response = await apiClient.post(`${BASE_PATH}/estimate-cost`, {
      character_count: params.characterCount,
      file_size: params.fileSize,
      file_type: params.fileType,
      target_language: params.targetLanguage,
      source_language: params.sourceLanguage || 'auto',
    });
    return response.data;
  }

  /**
   * Get translation job status
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
  async pollStatus(jobId, onStatusUpdate = null, interval = 2000) {
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
            reject(new Error(status.error || 'Translation failed'));
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
   * Download translated document
   * @param {string} jobId - The job ID
   * @param {string} fileName - Desired filename for download
   * @returns {Promise<void>}
   */
  async downloadResults(jobId, fileName = 'translated_document') {
    return downloadFile(`${BASE_PATH}/results/${jobId}`, fileName);
  }

  /**
   * Get translation glossary (custom terminology)
   * @returns {Promise<Array>} List of glossary terms
   */
  async getGlossary() {
    const response = await apiClient.get(`${BASE_PATH}/glossary`);
    return response.data;
  }

  /**
   * Add term to glossary
   * @param {Object} term - Glossary term
   * @param {string} term.source - Source term
   * @param {string} term.target - Target translation
   * @param {string} term.language - Language pair
   * @returns {Promise<Object>} Added term details
   */
  async addGlossaryTerm(term) {
    const response = await apiClient.post(`${BASE_PATH}/glossary`, term);
    return response.data;
  }

  /**
   * Get translation history
   * @param {Object} params - Query parameters
   * @param {number} params.limit - Number of items to return
   * @param {number} params.offset - Offset for pagination
   * @returns {Promise<Object>} Translation history
   */
  async getHistory(params = {}) {
    const response = await apiClient.get(`${BASE_PATH}/history`, { params });
    return response.data;
  }
}

// Export singleton instance
export default new TranslationService();

// Export class for testing purposes
export { TranslationService };