/**
 * Service Metrics Mock Data
 * Detailed performance metrics for each Azure Cognitive Service
 */

export const serviceMetrics = {
  // Document Intelligence Metrics
  documentIntelligence: {
    overview: {
      totalJobs: 561,
      completedJobs: 485,
      failedJobs: 38,
      processingJobs: 38,
      successRate: 86.5,
      averageProcessingTime: 22000, // ms
      totalRevenue: 187.34,
      averageCostPerJob: 0.33
    },
    
    // Performance by file type
    performanceByFileType: [
      {
        fileType: 'PDF',
        count: 342,
        successRate: 89.2,
        averageProcessingTime: 25000,
        averagePageCount: 12.4,
        averageCost: 0.31,
        commonIssues: ['scanned documents', 'poor image quality']
      },
      {
        fileType: 'DOCX',
        count: 124,
        successRate: 94.4,
        averageProcessingTime: 15000,
        averagePageCount: 8.7,
        averageCost: 0.29,
        commonIssues: ['complex layouts', 'embedded objects']
      },
      {
        fileType: 'Images (PNG/JPG)',
        count: 67,
        successRate: 78.2,
        averageProcessingTime: 18000,
        averagePageCount: 1.0,
        averageCost: 0.41,
        commonIssues: ['low resolution', 'handwritten text']
      },
      {
        fileType: 'XLSX',
        count: 28,
        successRate: 85.7,
        averageProcessingTime: 12000,
        averagePageCount: 3.2,
        averageCost: 0.25,
        commonIssues: ['complex formulas', 'merged cells']
      }
    ],
    
    // Processing time distribution
    processingTimeDistribution: {
      fast: { range: '< 10s', count: 134, percentage: 23.9 },
      normal: { range: '10-30s', count: 289, percentage: 51.5 },
      slow: { range: '30-60s', count: 108, percentage: 19.2 },
      verySlow: { range: '> 60s', count: 30, percentage: 5.3 }
    },
    
    // Quality metrics
    qualityMetrics: {
      averageConfidenceScore: 0.924,
      highConfidence: { threshold: '> 0.9', count: 398, percentage: 70.9 },
      mediumConfidence: { threshold: '0.7-0.9', count: 134, percentage: 23.9 },
      lowConfidence: { threshold: '< 0.7', count: 29, percentage: 5.2 },
      
      extractionAccuracy: {
        textExtraction: 94.2, // percentage
        tableExtraction: 89.7,
        layoutDetection: 91.5,
        formFieldExtraction: 87.3
      }
    },
    
    // Common failure reasons
    failureAnalysis: {
      totalFailures: 38,
      reasons: [
        { reason: 'Corrupted file', count: 12, percentage: 31.6 },
        { reason: 'Unsupported format', count: 8, percentage: 21.1 },
        { reason: 'Poor image quality', count: 7, percentage: 18.4 },
        { reason: 'File too large', count: 5, percentage: 13.2 },
        { reason: 'Password protected', count: 4, percentage: 10.5 },
        { reason: 'System error', count: 2, percentage: 5.3 }
      ]
    },
    
    // Page count analytics
    pageAnalytics: {
      averagePages: 12.4,
      distribution: {
        single: { range: '1 page', count: 98, percentage: 17.5 },
        few: { range: '2-5 pages', count: 167, percentage: 29.8 },
        medium: { range: '6-20 pages', count: 201, percentage: 35.8 },
        many: { range: '21-50 pages', count: 78, percentage: 13.9 },
        massive: { range: '> 50 pages', count: 17, percentage: 3.0 }
      }
    }
  },
  
  // Translation Service Metrics
  translation: {
    overview: {
      totalJobs: 436,
      completedJobs: 374,
      failedJobs: 31,
      processingJobs: 31,
      successRate: 85.8,
      averageProcessingTime: 12500, // ms
      totalRevenue: 152.67,
      averageCostPerJob: 0.35
    },
    
    // Language pair analytics
    languagePairs: [
      {
        source: 'Spanish',
        target: 'English',
        count: 89,
        successRate: 92.1,
        averageQuality: 0.94,
        averageProcessingTime: 8500
      },
      {
        source: 'French',
        target: 'English',
        count: 76,
        successRate: 88.2,
        averageQuality: 0.91,
        averageProcessingTime: 9200
      },
      {
        source: 'German',
        target: 'English',
        count: 54,
        successRate: 85.2,
        averageQuality: 0.89,
        averageProcessingTime: 11000
      },
      {
        source: 'Japanese',
        target: 'English',
        count: 43,
        successRate: 79.1,
        averageQuality: 0.86,
        averageProcessingTime: 15500
      },
      {
        source: 'Chinese',
        target: 'English',
        count: 38,
        successRate: 81.6,
        averageQuality: 0.87,
        averageProcessingTime: 14200
      },
      {
        source: 'Auto-detect',
        target: 'English',
        count: 136,
        successRate: 83.8,
        averageQuality: 0.88,
        averageProcessingTime: 13800
      }
    ],
    
    // Content type performance
    contentTypes: [
      {
        type: 'Business Documents',
        count: 187,
        successRate: 89.3,
        averageQuality: 0.92,
        commonTerms: ['contract', 'agreement', 'policy']
      },
      {
        type: 'Technical Documentation',
        count: 134,
        successRate: 85.1,
        averageQuality: 0.89,
        commonTerms: ['specification', 'manual', 'guide']
      },
      {
        type: 'Marketing Content',
        count: 78,
        successRate: 91.0,
        averageQuality: 0.94,
        commonTerms: ['product', 'service', 'customer']
      },
      {
        type: 'Legal Documents',
        count: 37,
        successRate: 82.4,
        averageQuality: 0.87,
        commonTerms: ['terms', 'conditions', 'liability']
      }
    ],
    
    // Quality distribution
    qualityMetrics: {
      averageQualityScore: 0.943,
      excellent: { threshold: '> 0.95', count: 245, percentage: 56.2 },
      good: { threshold: '0.85-0.95', count: 156, percentage: 35.8 },
      fair: { threshold: '0.7-0.85', count: 28, percentage: 6.4 },
      poor: { threshold: '< 0.7', count: 7, percentage: 1.6 }
    },
    
    // Character count analytics
    characterAnalytics: {
      averageCharacters: 98750,
      distribution: {
        short: { range: '< 1K chars', count: 67, percentage: 15.4 },
        medium: { range: '1K-10K chars', count: 189, percentage: 43.3 },
        long: { range: '10K-100K chars', count: 156, percentage: 35.8 },
        veryLong: { range: '> 100K chars', count: 24, percentage: 5.5 }
      }
    },
    
    // Failure analysis
    failureAnalysis: {
      totalFailures: 31,
      reasons: [
        { reason: 'Unsupported language', count: 9, percentage: 29.0 },
        { reason: 'Empty document', count: 7, percentage: 22.6 },
        { reason: 'Mixed languages', count: 6, percentage: 19.4 },
        { reason: 'Poor text quality', count: 4, percentage: 12.9 },
        { reason: 'File format issue', count: 3, percentage: 9.7 },
        { reason: 'System error', count: 2, percentage: 6.5 }
      ]
    }
  },
  
  // Transcription Service Metrics
  transcription: {
    overview: {
      totalJobs: 250,
      completedJobs: 200,
      failedJobs: 25,
      processingJobs: 25,
      successRate: 80.0,
      averageProcessingTime: 75000, // ms
      totalRevenue: 116.77,
      averageCostPerJob: 0.47
    },
    
    // Audio format performance
    audioFormats: [
      {
        format: 'WAV',
        count: 98,
        successRate: 87.8,
        averageQuality: 0.92,
        averageProcessingTime: 65000,
        preferredFor: 'high quality recordings'
      },
      {
        format: 'MP3',
        count: 89,
        successRate: 78.7,
        averageQuality: 0.86,
        averageProcessingTime: 82000,
        preferredFor: 'general purpose'
      },
      {
        format: 'M4A',
        count: 43,
        successRate: 81.4,
        averageQuality: 0.88,
        averageProcessingTime: 71000,
        preferredFor: 'apple devices'
      },
      {
        format: 'FLAC',
        count: 20,
        successRate: 95.0,
        averageQuality: 0.96,
        averageProcessingTime: 58000,
        preferredFor: 'professional recordings'
      }
    ],
    
    // Transcription type performance
    transcriptionTypes: {
      fast: {
        count: 167,
        averageProcessingTime: 45000,
        successRate: 82.0,
        averageQuality: 0.88,
        costPerHour: 0.36,
        useCase: 'real-time applications'
      },
      batch: {
        count: 83,
        averageProcessingTime: 135000,
        successRate: 76.5,
        averageQuality: 0.93,
        costPerHour: 0.18,
        useCase: 'high accuracy needs'
      }
    },
    
    // Audio duration analytics
    durationAnalytics: {
      averageDuration: 2847, // seconds (47.5 minutes)
      distribution: {
        short: { range: '< 5 min', count: 45, percentage: 18.0 },
        medium: { range: '5-30 min', count: 112, percentage: 44.8 },
        long: { range: '30-60 min', count: 67, percentage: 26.8 },
        veryLong: { range: '> 60 min', count: 26, percentage: 10.4 }
      }
    },
    
    // Quality factors
    qualityFactors: {
      speakerCount: {
        single: { count: 89, successRate: 89.9, avgQuality: 0.94 },
        two: { count: 78, successRate: 84.6, avgQuality: 0.90 },
        multiple: { count: 83, successRate: 69.9, avgQuality: 0.83 }
      },
      backgroundNoise: {
        quiet: { count: 134, successRate: 91.0, avgQuality: 0.95 },
        moderate: { count: 89, successRate: 76.4, avgQuality: 0.86 },
        noisy: { count: 27, successRate: 51.9, avgQuality: 0.72 }
      },
      audioQuality: {
        high: { count: 123, successRate: 89.4, avgQuality: 0.94 },
        medium: { count: 89, successRate: 78.7, avgQuality: 0.87 },
        low: { count: 38, successRate: 60.5, avgQuality: 0.75 }
      }
    },
    
    // Word accuracy metrics
    accuracyMetrics: {
      averageWordAccuracy: 89.1, // percentage
      distribution: {
        excellent: { range: '> 95%', count: 89, percentage: 35.6 },
        good: { range: '85-95%', count: 78, percentage: 31.2 },
        fair: { range: '70-85%', count: 56, percentage: 22.4 },
        poor: { range: '< 70%', count: 27, percentage: 10.8 }
      }
    },
    
    // Failure analysis
    failureAnalysis: {
      totalFailures: 25,
      reasons: [
        { reason: 'Poor audio quality', count: 8, percentage: 32.0 },
        { reason: 'No speech detected', count: 6, percentage: 24.0 },
        { reason: 'Unsupported format', count: 4, percentage: 16.0 },
        { reason: 'File too large', count: 3, percentage: 12.0 },
        { reason: 'Audio too short', count: 2, percentage: 8.0 },
        { reason: 'System error', count: 2, percentage: 8.0 }
      ]
    }
  },
  
  // Cross-service comparisons
  serviceComparison: {
    processingSpeed: {
      fastest: { service: 'translation', avgTime: 12500 },
      medium: { service: 'document-intelligence', avgTime: 22000 },
      slowest: { service: 'transcription', avgTime: 75000 }
    },
    reliability: {
      highest: { service: 'document-intelligence', successRate: 86.5 },
      medium: { service: 'translation', successRate: 85.8 },
      lowest: { service: 'transcription', successRate: 80.0 }
    },
    costEfficiency: {
      lowest: { service: 'document-intelligence', avgCost: 0.33 },
      medium: { service: 'translation', avgCost: 0.35 },
      highest: { service: 'transcription', avgCost: 0.47 }
    }
  },
  
  // Service health indicators
  healthIndicators: {
    documentIntelligence: {
      status: 'healthy',
      uptime: 99.8,
      responseTime: 1850, // ms
      errorRate: 2.1,
      lastIncident: '2025-06-10T14:30:00Z'
    },
    translation: {
      status: 'healthy',
      uptime: 99.6,
      responseTime: 1200,
      errorRate: 1.8,
      lastIncident: '2025-06-08T09:15:00Z'
    },
    transcription: {
      status: 'degraded',
      uptime: 98.9,
      responseTime: 2400,
      errorRate: 4.2,
      lastIncident: '2025-06-14T16:45:00Z'
    }
  }
};

export default serviceMetrics;