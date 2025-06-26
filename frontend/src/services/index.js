/**
 * Services Index
 * Central export point for all API services
 */

// Import all services
import apiClient from './apiClient';
import documentIntelligenceService from './documentIntelligenceService';
import translationService from './translationService';
import transcriptionService from './transcriptionService';
import websocketService from './websocketService';
import fileService from './fileService';
import config from './config';

// Export services
export {
  apiClient,
  documentIntelligenceService,
  translationService,
  transcriptionService,
  websocketService,
  fileService,
  config,
};

// Export service-specific utilities
export { uploadFile, downloadFile, withRetry } from './apiClient';
export { getWebSocketUrl, isDevelopment, isProduction } from './config';

// Convenience object with all services
const services = {
  documentIntelligence: documentIntelligenceService,
  translation: translationService,
  transcription: transcriptionService,
  websocket: websocketService,
  file: fileService,
  config,
};

export default services;