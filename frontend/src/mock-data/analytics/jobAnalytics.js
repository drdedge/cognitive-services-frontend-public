/**
 * Job Analytics Mock Data
 * Comprehensive statistics and aggregated data about job processing
 */

// Generate analytics data based on realistic patterns
const generateTimeSeriesData = (days = 30) => {
  const data = [];
  const baseDate = new Date();
  
  for (let i = days; i >= 0; i--) {
    const date = new Date(baseDate);
    date.setDate(date.getDate() - i);
    
    // Simulate realistic daily patterns
    const dayOfWeek = date.getDay();
    const isWeekend = dayOfWeek === 0 || dayOfWeek === 6;
    const baseJobs = isWeekend ? 3 : 12; // Less activity on weekends
    
    // Add some randomness
    const variation = Math.random() * 0.4 + 0.8; // 80-120% of base
    const totalJobs = Math.floor(baseJobs * variation);
    
    data.push({
      date: date.toISOString().split('T')[0],
      totalJobs,
      completedJobs: Math.floor(totalJobs * 0.85), // 85% success rate
      failedJobs: Math.floor(totalJobs * 0.08), // 8% failure rate
      processingJobs: totalJobs - Math.floor(totalJobs * 0.85) - Math.floor(totalJobs * 0.08),
      documentIntelligence: Math.floor(totalJobs * 0.45),
      translation: Math.floor(totalJobs * 0.35),
      transcription: Math.floor(totalJobs * 0.20)
    });
  }
  
  return data;
};

// Generate hourly distribution data
const generateHourlyDistribution = () => {
  const hours = [];
  for (let hour = 0; hour < 24; hour++) {
    let activity;
    if (hour >= 9 && hour <= 17) {
      // Business hours - high activity
      activity = Math.floor(Math.random() * 15) + 20;
    } else if (hour >= 18 && hour <= 22) {
      // Evening - medium activity
      activity = Math.floor(Math.random() * 8) + 5;
    } else {
      // Night/early morning - low activity
      activity = Math.floor(Math.random() * 3) + 1;
    }
    
    hours.push({
      hour,
      jobs: activity,
      label: `${hour.toString().padStart(2, '0')}:00`
    });
  }
  return hours;
};

export const jobAnalytics = {
  // Overall Statistics
  overview: {
    totalJobs: 1247,
    completedJobs: 1059,
    failedJobs: 94,
    processingJobs: 94,
    successRate: 84.9, // percentage
    averageProcessingTime: 28500, // milliseconds
    totalCost: 456.78, // USD
    averageCostPerJob: 0.37
  },
  
  // Service Distribution
  serviceBreakdown: {
    documentIntelligence: {
      total: 561,
      completed: 485,
      failed: 38,
      processing: 38,
      successRate: 86.5,
      averageProcessingTime: 22000,
      totalCost: 187.34,
      averageCostPerJob: 0.33
    },
    translation: {
      total: 436,
      completed: 374,
      failed: 31,
      processing: 31,
      successRate: 85.8,
      averageProcessingTime: 12500,
      totalCost: 152.67,
      averageCostPerJob: 0.35
    },
    transcription: {
      total: 250,
      completed: 200,
      failed: 25,
      processing: 25,
      successRate: 80.0,
      averageProcessingTime: 75000,
      totalCost: 116.77,
      averageCostPerJob: 0.47
    }
  },
  
  // Time-based Analytics
  timeSeriesData: generateTimeSeriesData(30),
  
  // Hourly Distribution
  hourlyDistribution: generateHourlyDistribution(),
  
  // Weekly Pattern
  weeklyPattern: [
    { day: 'Monday', jobs: 198, avgProcessingTime: 26500 },
    { day: 'Tuesday', jobs: 215, avgProcessingTime: 24800 },
    { day: 'Wednesday', jobs: 189, avgProcessingTime: 29200 },
    { day: 'Thursday', jobs: 207, avgProcessingTime: 27300 },
    { day: 'Friday', jobs: 184, avgProcessingTime: 31200 },
    { day: 'Saturday', jobs: 128, avgProcessingTime: 35600 },
    { day: 'Sunday', jobs: 126, avgProcessingTime: 33400 }
  ],
  
  // File Size Analytics
  fileSizeDistribution: {
    small: { range: '< 1MB', count: 456, percentage: 36.6 },
    medium: { range: '1-10MB', count: 523, percentage: 41.9 },
    large: { range: '10-50MB', count: 201, percentage: 16.1 },
    extraLarge: { range: '> 50MB', count: 67, percentage: 5.4 }
  },
  
  // Processing Time Analytics
  processingTimeDistribution: {
    fast: { range: '< 10s', count: 398, percentage: 31.9 },
    normal: { range: '10-60s', count: 623, percentage: 50.0 },
    slow: { range: '1-5min', count: 187, percentage: 15.0 },
    verySlow: { range: '> 5min', count: 39, percentage: 3.1 }
  },
  
  // Error Analytics
  errorAnalytics: {
    totalErrors: 94,
    errorCategories: [
      { category: 'file_error', count: 28, percentage: 29.8, description: 'Corrupted or invalid files' },
      { category: 'size_error', count: 15, percentage: 16.0, description: 'File size limitations' },
      { category: 'content_error', count: 21, percentage: 22.3, description: 'No processable content' },
      { category: 'quality_error', count: 12, percentage: 12.8, description: 'Poor quality input' },
      { category: 'language_error', count: 9, percentage: 9.6, description: 'Unsupported languages' },
      { category: 'access_error', count: 6, percentage: 6.4, description: 'Password protected files' },
      { category: 'system_error', count: 3, percentage: 3.2, description: 'Internal system errors' }
    ],
    retryableErrors: 43, // 45.7% of errors are retryable
    nonRetryableErrors: 51
  },
  
  // Cost Analytics
  costAnalytics: {
    totalSpent: 456.78,
    averageJobCost: 0.37,
    costByService: {
      documentIntelligence: { total: 187.34, average: 0.33, percentage: 41.0 },
      translation: { total: 152.67, average: 0.35, percentage: 33.4 },
      transcription: { total: 116.77, average: 0.47, percentage: 25.6 }
    },
    costDistribution: [
      { range: '< $0.10', count: 234, totalCost: 15.67 },
      { range: '$0.10-$0.50', count: 678, totalCost: 203.45 },
      { range: '$0.50-$1.00', count: 234, totalCost: 156.78 },
      { range: '$1.00-$5.00', count: 89, totalCost: 198.23 },
      { range: '> $5.00', count: 12, totalCost: 82.65 }
    ],
    monthlyTrend: [
      { month: 'Jan', spent: 145.23 },
      { month: 'Feb', spent: 167.89 },
      { month: 'Mar', spent: 134.56 },
      { month: 'Apr', spent: 189.34 },
      { month: 'May', spent: 156.78 },
      { month: 'Jun', spent: 163.42 }
    ]
  },
  
  // Performance Metrics
  performanceMetrics: {
    averageProcessingTime: {
      overall: 28500, // ms
      documentIntelligence: 22000,
      translation: 12500,
      transcription: 75000
    },
    throughput: {
      jobsPerHour: 5.2,
      jobsPerDay: 124.7,
      peakHourThroughput: 12.3
    },
    reliability: {
      uptime: 99.7, // percentage
      successRate: 84.9,
      errorRate: 7.5,
      retryRate: 7.6
    }
  },
  
  // Quality Metrics
  qualityMetrics: {
    averageConfidenceScores: {
      documentIntelligence: 0.924,
      translation: 0.943,
      transcription: 0.891
    },
    qualityDistribution: {
      high: { range: '> 0.9', count: 756, percentage: 71.4 },
      medium: { range: '0.7-0.9', count: 234, percentage: 22.1 },
      low: { range: '< 0.7', count: 69, percentage: 6.5 }
    }
  },
  
  // Recent Trends (Last 7 days vs Previous 7 days)
  trends: {
    jobVolume: { current: 87, previous: 78, change: 11.5 }, // percentage change
    successRate: { current: 86.2, previous: 83.7, change: 2.5 },
    averageCost: { current: 0.39, previous: 0.35, change: 11.4 },
    processingTime: { current: 26800, previous: 29200, change: -8.2 }
  }
};

export default jobAnalytics;