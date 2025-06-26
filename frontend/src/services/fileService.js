/**
 * File Service
 * Helper utilities for file operations and validation
 */

// Supported file types by service
const SUPPORTED_TYPES = {
  documentIntelligence: {
    extensions: ['.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.heif', '.docx', '.xlsx', '.pptx', '.html'],
    mimeTypes: [
      'application/pdf',
      'image/png',
      'image/jpeg',
      'image/tiff',
      'image/bmp',
      'image/heif',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      'text/html'
    ],
    maxSize: 50 * 1024 * 1024, // 50MB
  },
  translation: {
    extensions: ['.txt', '.pdf', '.docx', '.xlsx', '.pptx', '.html', '.xml', '.xlf', '.tmx'],
    mimeTypes: [
      'text/plain',
      'application/pdf',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      'text/html',
      'application/xml',
      'text/xml',
      'application/xliff+xml',
      'application/x-tmx+xml'
    ],
    maxSize: 40 * 1024 * 1024, // 40MB
  },
  transcription: {
    extensions: ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.wma', '.aac', '.opus', '.webm'],
    mimeTypes: [
      'audio/wav',
      'audio/mpeg',
      'audio/mp4',
      'audio/flac',
      'audio/ogg',
      'audio/x-ms-wma',
      'audio/aac',
      'audio/opus',
      'audio/webm'
    ],
    maxSize: 200 * 1024 * 1024, // 200MB
    maxDuration: 120 * 60, // 120 minutes in seconds
  },
};

class FileService {
  /**
   * Validate file for a specific service
   * @param {File} file - File to validate
   * @param {string} service - Service name (documentIntelligence, translation, transcription)
   * @returns {Object} Validation result { valid, error }
   */
  validateFile(file, service) {
    if (!file) {
      return { valid: false, error: 'No file provided' };
    }

    const config = SUPPORTED_TYPES[service];
    if (!config) {
      return { valid: false, error: 'Invalid service type' };
    }

    // Check file size
    if (file.size > config.maxSize) {
      const maxSizeMB = config.maxSize / (1024 * 1024);
      return { valid: false, error: `File size exceeds ${maxSizeMB}MB limit` };
    }

    // Check file extension
    const extension = this.getFileExtension(file.name);
    if (!config.extensions.includes(extension.toLowerCase())) {
      return { 
        valid: false, 
        error: `File type ${extension} not supported. Supported types: ${config.extensions.join(', ')}`
      };
    }

    // Check MIME type if available
    if (file.type && !config.mimeTypes.includes(file.type)) {
      console.warn(`MIME type mismatch: ${file.type} not in supported list`);
      // Don't fail on MIME type alone as browsers can be inconsistent
    }

    return { valid: true };
  }

  /**
   * Get file extension
   * @param {string} filename - File name
   * @returns {string} File extension with dot
   */
  getFileExtension(filename) {
    const lastDot = filename.lastIndexOf('.');
    return lastDot === -1 ? '' : filename.substring(lastDot);
  }

  /**
   * Format file size for display
   * @param {number} bytes - Size in bytes
   * @returns {string} Formatted size
   */
  formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /**
   * Calculate file hash (SHA-256)
   * @param {File} file - File to hash
   * @returns {Promise<string>} Hex hash string
   */
  async calculateHash(file) {
    const buffer = await file.arrayBuffer();
    const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  }

  /**
   * Read file as text
   * @param {File} file - File to read
   * @param {string} encoding - Text encoding (default: UTF-8)
   * @returns {Promise<string>} File content
   */
  readAsText(file, encoding = 'UTF-8') {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsText(file, encoding);
    });
  }

  /**
   * Read file as data URL (base64)
   * @param {File} file - File to read
   * @returns {Promise<string>} Data URL
   */
  readAsDataURL(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  /**
   * Create thumbnail for image file
   * @param {File} file - Image file
   * @param {number} maxWidth - Maximum width
   * @param {number} maxHeight - Maximum height
   * @returns {Promise<string>} Thumbnail data URL
   */
  async createThumbnail(file, maxWidth = 200, maxHeight = 200) {
    if (!file.type.startsWith('image/')) {
      throw new Error('File is not an image');
    }

    const dataUrl = await this.readAsDataURL(file);
    
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');

        // Calculate new dimensions
        let width = img.width;
        let height = img.height;

        if (width > height) {
          if (width > maxWidth) {
            height *= maxWidth / width;
            width = maxWidth;
          }
        } else {
          if (height > maxHeight) {
            width *= maxHeight / height;
            height = maxHeight;
          }
        }

        canvas.width = width;
        canvas.height = height;

        // Draw resized image
        ctx.drawImage(img, 0, 0, width, height);

        resolve(canvas.toDataURL('image/jpeg', 0.8));
      };
      img.onerror = reject;
      img.src = dataUrl;
    });
  }

  /**
   * Get audio file duration
   * @param {File} file - Audio file
   * @returns {Promise<number>} Duration in seconds
   */
  getAudioDuration(file) {
    return new Promise((resolve, reject) => {
      const audio = new Audio();
      audio.onloadedmetadata = () => {
        resolve(audio.duration);
      };
      audio.onerror = reject;
      audio.src = URL.createObjectURL(file);
    });
  }

  /**
   * Compress file if possible
   * @param {File} file - File to compress
   * @param {Object} options - Compression options
   * @returns {Promise<File>} Compressed file or original if compression not beneficial
   */
  async compressFile(file, options = {}) {
    // For now, return original file
    // In production, you might use libraries like pako for compression
    return file;
  }

  /**
   * Get supported file types for a service
   * @param {string} service - Service name
   * @returns {Object} Supported types configuration
   */
  getSupportedTypes(service) {
    return SUPPORTED_TYPES[service] || null;
  }

  /**
   * Check if file type is supported
   * @param {string} filename - File name
   * @param {string} service - Service name
   * @returns {boolean} True if supported
   */
  isSupported(filename, service) {
    const config = SUPPORTED_TYPES[service];
    if (!config) return false;

    const extension = this.getFileExtension(filename);
    return config.extensions.includes(extension.toLowerCase());
  }
}

// Export singleton instance
export default new FileService();

// Export class for testing
export { FileService };