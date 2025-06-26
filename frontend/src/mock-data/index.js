/**
 * Mock Data Index
 * Central export point for all mock data used in the application
 */

// Job Data
import { completedJobs } from './jobs/completedJobs.js';
import { processingJobs } from './jobs/processingJobs.js';
import { failedJobs } from './jobs/failedJobs.js';

// Analytics Data
import { jobAnalytics } from './analytics/jobAnalytics.js';
import { userAnalytics } from './analytics/userAnalytics.js';
import { serviceMetrics } from './analytics/serviceMetrics.js';
import { costAnalytics } from './analytics/costAnalytics.js';

// Re-export for named imports
export { completedJobs, processingJobs, failedJobs };
export { jobAnalytics, userAnalytics, serviceMetrics, costAnalytics };

// Combined exports for convenience
export const allJobs = {
  completed: () => import('./jobs/completedJobs.js').then(m => m.completedJobs),
  processing: () => import('./jobs/processingJobs.js').then(m => m.processingJobs),
  failed: () => import('./jobs/failedJobs.js').then(m => m.failedJobs)
};

export const analytics = {
  jobs: () => import('./analytics/jobAnalytics.js').then(m => m.jobAnalytics),
  users: () => import('./analytics/userAnalytics.js').then(m => m.userAnalytics),
  services: () => import('./analytics/serviceMetrics.js').then(m => m.serviceMetrics),
  costs: () => import('./analytics/costAnalytics.js').then(m => m.costAnalytics)
};

// Helper function to get all job data
export const getAllJobs = () => {
  return {
    completed: completedJobs,
    processing: processingJobs,
    failed: failedJobs,
    all: [...completedJobs, ...processingJobs, ...failedJobs]
  };
};

// Helper function to get all analytics data
export const getAllAnalytics = () => {
  return {
    jobs: jobAnalytics,
    users: userAnalytics,
    services: serviceMetrics,
    costs: costAnalytics
  };
};

// Data generation utilities
export const dataUtils = {
  // Generate a random job ID
  generateJobId: (prefix = 'job') => `${prefix}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
  
  // Generate a timestamp within the last N days
  generateRecentTimestamp: (daysAgo = 7) => {
    const date = new Date();
    date.setDate(date.getDate() - Math.floor(Math.random() * daysAgo));
    return date.toISOString();
  },
  
  // Calculate cost based on service and file properties
  calculateCost: (service, fileSize, pageCount, characterCount, audioDuration) => {
    const pricing = {
      'document-intelligence': { pricePerThousandPages: 10.00 },
      'translation': { pricePerMillionCharacters: 10.00 },
      'transcription': { fastPerHour: 0.36, batchPerHour: 0.18 }
    };
    
    switch (service) {
      case 'document-intelligence':
        return (pageCount / 1000) * pricing['document-intelligence'].pricePerThousandPages;
      case 'translation':
        return (characterCount / 1000000) * pricing.translation.pricePerMillionCharacters;
      case 'transcription':
        const hours = audioDuration / 3600;
        return hours * pricing.transcription.fastPerHour; // Default to fast pricing
      default:
        return 0.50; // Default cost
    }
  },
  
  // Get file size in human readable format
  formatFileSize: (bytes) => {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
  },
  
  // Get processing time in human readable format
  formatProcessingTime: (milliseconds) => {
    const seconds = Math.floor(milliseconds / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes % 60}m ${seconds % 60}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${seconds % 60}s`;
    } else {
      return `${seconds}s`;
    }
  }
};

// Mock data configuration
export const mockConfig = {
  // Enable/disable different types of mock data
  enableJobData: true,
  enableAnalytics: true,
  enableRealTimeUpdates: true,
  
  // Data refresh intervals (for development)
  refreshIntervals: {
    processingJobs: 5000, // 5 seconds
    analytics: 30000, // 30 seconds
    recentActivity: 10000 // 10 seconds
  },
  
  // Data generation settings
  generation: {
    maxJobsPerDay: 50,
    maxUsersActive: 20,
    errorRate: 0.08, // 8% of jobs fail
    averageProcessingTime: 30000 // 30 seconds
  }
};

// Default export with everything
export default {
  jobs: {
    completed: completedJobs,
    processing: processingJobs,
    failed: failedJobs
  },
  analytics: {
    jobs: jobAnalytics,
    users: userAnalytics,
    services: serviceMetrics,
    costs: costAnalytics
  },
  utils: dataUtils,
  config: mockConfig
};