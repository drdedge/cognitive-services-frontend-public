/**
 * User Analytics Mock Data
 * User behavior, activity patterns, and usage statistics
 */

export const userAnalytics = {
  // Overall User Statistics
  overview: {
    totalUsers: 47,
    activeUsersLast30Days: 34,
    activeUsersLast7Days: 28,
    newUsersThisMonth: 6,
    averageJobsPerUser: 26.5,
    averageSpendPerUser: 9.72
  },
  
  // Top Users by Activity
  topUsersByJobs: [
    {
      userId: 'user-alice',
      name: 'Alice Johnson',
      department: 'Legal',
      totalJobs: 167,
      completedJobs: 145,
      failedJobs: 12,
      processingJobs: 10,
      successRate: 86.8,
      totalSpent: 58.34,
      averageJobCost: 0.35,
      lastActivity: '2025-06-15T14:30:00Z',
      preferredService: 'document-intelligence',
      joinDate: '2024-08-15'
    },
    {
      userId: 'user-bob',
      name: 'Bob Smith',
      department: 'Marketing',
      totalJobs: 142,
      completedJobs: 124,
      failedJobs: 8,
      processingJobs: 10,
      successRate: 87.3,
      totalSpent: 62.78,
      averageJobCost: 0.44,
      lastActivity: '2025-06-15T16:45:00Z',
      preferredService: 'translation',
      joinDate: '2024-07-22'
    },
    {
      userId: 'user-charlie',
      name: 'Charlie Brown',
      department: 'Operations',
      totalJobs: 98,
      completedJobs: 82,
      failedJobs: 9,
      processingJobs: 7,
      successRate: 83.7,
      totalSpent: 41.23,
      averageJobCost: 0.42,
      lastActivity: '2025-06-15T11:20:00Z',
      preferredService: 'transcription',
      joinDate: '2024-09-10'
    },
    {
      userId: 'user-diana',
      name: 'Diana Prince',
      department: 'HR',
      totalJobs: 89,
      completedJobs: 78,
      failedJobs: 6,
      processingJobs: 5,
      successRate: 87.6,
      totalSpent: 29.67,
      averageJobCost: 0.33,
      lastActivity: '2025-06-15T09:15:00Z',
      preferredService: 'translation',
      joinDate: '2024-06-30'
    },
    {
      userId: 'user-eve',
      name: 'Eve Wilson',
      department: 'Finance',
      totalJobs: 76,
      completedJobs: 68,
      failedJobs: 4,
      processingJobs: 4,
      successRate: 89.5,
      totalSpent: 34.12,
      averageJobCost: 0.45,
      lastActivity: '2025-06-15T15:30:00Z',
      preferredService: 'document-intelligence',
      joinDate: '2024-05-18'
    }
  ],
  
  // Top Users by Spending
  topUsersBySpending: [
    {
      userId: 'user-bob',
      name: 'Bob Smith',
      totalSpent: 62.78,
      jobCount: 142,
      averageJobCost: 0.44
    },
    {
      userId: 'user-alice',
      name: 'Alice Johnson',
      totalSpent: 58.34,
      jobCount: 167,
      averageJobCost: 0.35
    },
    {
      userId: 'user-charlie',
      name: 'Charlie Brown',
      totalSpent: 41.23,
      jobCount: 98,
      averageJobCost: 0.42
    },
    {
      userId: 'user-eve',
      name: 'Eve Wilson',
      totalSpent: 34.12,
      jobCount: 76,
      averageJobCost: 0.45
    },
    {
      userId: 'user-diana',
      name: 'Diana Prince',
      totalSpent: 29.67,
      jobCount: 89,
      averageJobCost: 0.33
    }
  ],
  
  // Department Analytics
  departmentBreakdown: {
    Legal: {
      users: 8,
      totalJobs: 234,
      totalSpent: 89.45,
      averageJobsPerUser: 29.3,
      successRate: 85.9,
      preferredService: 'document-intelligence'
    },
    Marketing: {
      users: 12,
      totalJobs: 298,
      totalSpent: 143.67,
      averageJobsPerUser: 24.8,
      successRate: 87.2,
      preferredService: 'translation'
    },
    Operations: {
      users: 9,
      totalJobs: 187,
      totalSpent: 78.23,
      averageJobsPerUser: 20.8,
      successRate: 82.4,
      preferredService: 'transcription'
    },
    Finance: {
      users: 6,
      totalJobs: 156,
      totalSpent: 67.89,
      averageJobsPerUser: 26.0,
      successRate: 89.1,
      preferredService: 'document-intelligence'
    },
    HR: {
      users: 7,
      totalJobs: 198,
      totalSpent: 56.34,
      averageJobsPerUser: 28.3,
      successRate: 86.4,
      preferredService: 'translation'
    },
    IT: {
      users: 5,
      totalJobs: 174,
      totalSpent: 21.20,
      averageJobsPerUser: 34.8,
      successRate: 84.5,
      preferredService: 'document-intelligence'
    }
  },
  
  // User Activity Patterns
  activityPatterns: {
    // Users by activity level
    activityLevels: {
      high: { threshold: '50+ jobs/month', users: 12, percentage: 25.5 },
      medium: { threshold: '20-49 jobs/month', users: 18, percentage: 38.3 },
      low: { threshold: '5-19 jobs/month', users: 11, percentage: 23.4 },
      minimal: { threshold: '< 5 jobs/month', users: 6, percentage: 12.8 }
    },
    
    // Peak usage hours by user type
    usagePatterns: {
      earlyBirds: { hours: '6-9 AM', userCount: 8, jobPercentage: 15.2 },
      businessHours: { hours: '9 AM-5 PM', userCount: 34, jobPercentage: 68.4 },
      eveningUsers: { hours: '5-9 PM', userCount: 12, jobPercentage: 13.7 },
      nightOwls: { hours: '9 PM-6 AM', userCount: 3, jobPercentage: 2.7 }
    }
  },
  
  // User Service Preferences
  servicePreferences: {
    documentIntelligence: {
      primaryUsers: 18,
      occasionalUsers: 23,
      totalJobs: 561,
      averageJobsPerUser: 31.2
    },
    translation: {
      primaryUsers: 15,
      occasionalUsers: 19,
      totalJobs: 436,
      averageJobsPerUser: 29.1
    },
    transcription: {
      primaryUsers: 8,
      occasionalUsers: 14,
      totalJobs: 250,
      averageJobsPerUser: 31.3
    }
  },
  
  // User Growth Analytics
  userGrowth: {
    monthlyNewUsers: [
      { month: 'Jan 2024', newUsers: 5, totalUsers: 20 },
      { month: 'Feb 2024', newUsers: 3, totalUsers: 23 },
      { month: 'Mar 2024', newUsers: 4, totalUsers: 27 },
      { month: 'Apr 2024', newUsers: 6, totalUsers: 33 },
      { month: 'May 2024', newUsers: 8, totalUsers: 41 },
      { month: 'Jun 2024', newUsers: 6, totalUsers: 47 }
    ],
    retentionRates: {
      month1: 94.7, // percentage of users active after 1 month
      month3: 87.2,
      month6: 81.5,
      month12: 76.8
    }
  },
  
  // User Behavior Analytics
  behaviorMetrics: {
    averageSessionDuration: 24.5, // minutes
    averageJobsPerSession: 3.2,
    returnUserRate: 78.4, // percentage
    
    // File size preferences by user
    fileSizePreferences: {
      smallFiles: { userCount: 28, preference: '< 5MB' },
      mediumFiles: { userCount: 15, preference: '5-25MB' },
      largeFiles: { userCount: 4, preference: '> 25MB' }
    },
    
    // Error recovery behavior
    errorRecovery: {
      retryImmediately: { userCount: 23, percentage: 48.9 },
      retryAfterChanges: { userCount: 18, percentage: 38.3 },
      giveUp: { userCount: 6, percentage: 12.8 }
    }
  },
  
  // User Success Metrics
  successMetrics: {
    overallSuccessRate: 85.7,
    powerUsers: { // Users with >90% success rate
      count: 15,
      averageSuccessRate: 92.3,
      averageJobsPerMonth: 42.1
    },
    strugglingUsers: { // Users with <75% success rate
      count: 6,
      averageSuccessRate: 68.4,
      commonIssues: ['large files', 'poor quality uploads', 'unsupported formats']
    }
  },
  
  // Recent User Activity (Last 24 hours)
  recentActivity: [
    {
      userId: 'user-alice',
      name: 'Alice Johnson',
      lastSeen: '2025-06-15T16:45:00Z',
      jobsToday: 8,
      status: 'active'
    },
    {
      userId: 'user-bob',
      name: 'Bob Smith',
      lastSeen: '2025-06-15T16:30:00Z',
      jobsToday: 5,
      status: 'active'
    },
    {
      userId: 'user-charlie',
      name: 'Charlie Brown',
      lastSeen: '2025-06-15T15:20:00Z',
      jobsToday: 3,
      status: 'active'
    },
    {
      userId: 'user-diana',
      name: 'Diana Prince',
      lastSeen: '2025-06-15T14:15:00Z',
      jobsToday: 6,
      status: 'active'
    },
    {
      userId: 'user-eve',
      name: 'Eve Wilson',
      lastSeen: '2025-06-15T13:45:00Z',
      jobsToday: 4,
      status: 'active'
    }
  ],
  
  // User Satisfaction Indicators
  satisfactionIndicators: {
    highSatisfaction: { // Based on repeat usage and success rates
      userCount: 32,
      criteria: 'Regular usage + high success rate',
      percentage: 68.1
    },
    mediumSatisfaction: {
      userCount: 11,
      criteria: 'Occasional usage or moderate success rate',
      percentage: 23.4
    },
    lowSatisfaction: {
      userCount: 4,
      criteria: 'Rare usage or low success rate',
      percentage: 8.5
    }
  }
};

export default userAnalytics;