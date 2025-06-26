import apiClient, { uploadFile, downloadFile, withRetry } from './apiClient';

const BASE_PATH = '/api/document-intelligence';

/**
 * Document Intelligence Service
 * Handles all API interactions for document processing
 */
class DocumentIntelligenceService {
  /**
   * Process a document for extraction
   * @param {File} file - The document file to process
   * @param {Object} options - Processing options
   * @param {string} options.analysisType - Type of analysis (layout, invoice, receipt, etc.)
   * @param {Function} onProgress - Progress callback for upload
   * @returns {Promise<Object>} Job details including job_id
   */
  async processDocument(file, options = {}, onProgress = null) {
    return withRetry(async () => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('model_id', options.analysisType || 'layout');
      formData.append('extract_tables', options.extractTables !== undefined ? options.extractTables : true);
      formData.append('extract_text', options.extractText !== undefined ? options.extractText : true);
      formData.append('output_format', options.outputFormat || 'markdown');
      
      const response = await apiClient.post(`${BASE_PATH}/process`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: onProgress
      });
      
      return response.data.data; // Backend returns response wrapped in success format
    });
  }

  /**
   * Estimate the cost of processing a document
   * @param {Object} params - Estimation parameters
   * @param {number} params.fileSize - File size in bytes
   * @param {string} params.fileType - File type/extension
   * @param {string} params.analysisType - Type of analysis
   * @returns {Promise<Object>} Cost estimation details
   */
  async estimateCost(params) {
    const response = await apiClient.post(`${BASE_PATH}/estimate-cost`, {
      file_size: params.fileSize,
      file_type: params.fileType,
      model_id: params.analysisType || 'layout',
      extract_tables: params.extractTables || false
    });
    return response.data.data; // Backend returns response wrapped in success format
  }

  /**
   * Get the status of a processing job
   * @param {string} jobId - The job ID to check
   * @returns {Promise<Object>} Job status details
   */
  async getStatus(jobId) {
    const response = await apiClient.get(`${BASE_PATH}/status/${jobId}`);
    return response.data.data; // Backend returns response wrapped in success format
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
            reject(new Error(status.error || 'Processing failed'));
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
   * Download processing results
   * @param {string} jobId - The job ID
   * @param {string} fileName - Desired filename for download
   * @returns {Promise<void>}
   */
  async downloadResults(jobId, fileName = 'results.zip') {
    return downloadFile(`${BASE_PATH}/results/${jobId}`, fileName);
  }

  /**
   * Get results metadata without downloading
   * @param {string} jobId - The job ID
   * @returns {Promise<Object>} Results metadata
   */
  async getResultsMetadata(jobId) {
    const response = await apiClient.get(`${BASE_PATH}/results/${jobId}/metadata`);
    return response.data.data; // Backend returns response wrapped in success format
  }

  /**
   * Cancel a processing job
   * @param {string} jobId - The job ID to cancel
   * @returns {Promise<Object>} Cancellation result
   */
  async cancelJob(jobId) {
    const response = await apiClient.post(`${BASE_PATH}/cancel/${jobId}`);
    return response.data.data; // Backend returns response wrapped in success format
  }

  /**
   * Get supported document types
   * @returns {Promise<Array>} List of supported document types
   */
  async getSupportedTypes() {
    const response = await apiClient.get(`${BASE_PATH}/supported-formats`);
    return response.data.data; // Backend returns response wrapped in success format
  }

  /**
   * Get available analysis types
   * @returns {Promise<Array>} List of analysis types
   */
  async getAnalysisTypes() {
    const response = await apiClient.get(`${BASE_PATH}/models`);
    return response.data.data; // Backend returns response wrapped in success format
  }
}

// Export singleton instance
export default new DocumentIntelligenceService();

// Export class for testing purposes
export { DocumentIntelligenceService };