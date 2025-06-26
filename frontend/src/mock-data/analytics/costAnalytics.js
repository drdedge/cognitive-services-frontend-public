/**
 * Cost Analytics Mock Data
 * Comprehensive financial metrics and spending analysis
 */

// Helper function to generate monthly data
const generateMonthlyData = (months = 12) => {
  const data = [];
  const baseDate = new Date();
  
  for (let i = months - 1; i >= 0; i--) {
    const date = new Date(baseDate);
    date.setMonth(date.getMonth() - i);
    
    // Simulate growth in spending
    const monthFactor = (months - i) / months; // Earlier months have less spending
    const baseSpending = 120 + (monthFactor * 200); // Growing from $120 to $320
    const variation = Math.random() * 0.3 + 0.85; // 85-115% variation
    
    const totalSpending = baseSpending * variation;
    
    data.push({
      month: date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' }),
      date: date.toISOString().split('T')[0],
      totalSpending: Math.round(totalSpending * 100) / 100,
      documentIntelligence: Math.round(totalSpending * 0.42 * 100) / 100,
      translation: Math.round(totalSpending * 0.35 * 100) / 100,
      transcription: Math.round(totalSpending * 0.23 * 100) / 100,
      jobCount: Math.floor(totalSpending / 0.38), // Average cost per job
      averageCostPerJob: 0.38
    });
  }
  
  return data;
};

export const costAnalytics = {
  // Overall Financial Overview
  overview: {
    totalSpent: 456.78,
    currentMonthSpent: 89.45,
    lastMonthSpent: 76.32,
    monthOverMonthChange: 17.2, // percentage
    averageCostPerJob: 0.37,
    totalJobs: 1247,
    projectedMonthlySpend: 94.50
  },
  
  // Spending by Service
  serviceSpending: {
    documentIntelligence: {
      totalSpent: 187.34,
      percentage: 41.0,
      jobCount: 561,
      averageCostPerJob: 0.33,
      monthlySpend: 36.78,
      trend: 'increasing'
    },
    translation: {
      totalSpent: 152.67,
      percentage: 33.4,
      jobCount: 436,
      averageCostPerJob: 0.35,
      monthlySpend: 31.24,
      trend: 'stable'
    },
    transcription: {
      totalSpent: 116.77,
      percentage: 25.6,
      jobCount: 250,
      averageCostPerJob: 0.47,
      monthlySpend: 21.43,
      trend: 'decreasing'
    }
  },
  
  // Monthly Spending Trends
  monthlyTrends: generateMonthlyData(12),
  
  // Cost Distribution by Job Size
  costDistribution: [
    {
      range: '< $0.10',
      count: 234,
      totalCost: 15.67,
      percentage: 18.8,
      averageCost: 0.067,
      description: 'Small documents/short text'
    },
    {
      range: '$0.10 - $0.50',
      count: 678,
      totalCost: 203.45,
      percentage: 54.4,
      averageCost: 0.30,
      description: 'Medium documents/moderate content'
    },
    {
      range: '$0.50 - $1.00',
      count: 234,
      totalCost: 156.78,
      percentage: 18.8,
      averageCost: 0.67,
      description: 'Large documents/long content'
    },
    {
      range: '$1.00 - $5.00',
      count: 89,
      totalCost: 198.23,
      percentage: 7.1,
      averageCost: 2.23,
      description: 'Very large documents/extensive content'
    },
    {
      range: '> $5.00',
      count: 12,
      totalCost: 82.65,
      percentage: 1.0,
      averageCost: 6.89,
      description: 'Massive documents/enterprise content'
    }
  ],
  
  // Department Spending
  departmentSpending: [
    {
      department: 'Legal',
      totalSpent: 89.45,
      percentage: 19.6,
      jobCount: 234,
      averageCostPerJob: 0.38,
      topService: 'document-intelligence',
      monthlyBudget: 25.00,
      budgetUtilization: 142.7
    },
    {
      department: 'Marketing',
      totalSpent: 76.32,
      percentage: 16.7,
      jobCount: 298,
      averageCostPerJob: 0.26,
      topService: 'translation',
      monthlyBudget: 30.00,
      budgetUtilization: 101.8
    },
    {
      department: 'Operations',
      totalSpent: 67.89,
      percentage: 14.9,
      jobCount: 187,
      averageCostPerJob: 0.36,
      topService: 'transcription',
      monthlyBudget: 20.00,
      budgetUtilization: 135.7
    },
    {
      department: 'Finance',
      totalSpent: 54.23,
      percentage: 11.9,
      jobCount: 156,
      averageCostPerJob: 0.35,
      topService: 'document-intelligence',
      monthlyBudget: 15.00,
      budgetUtilization: 144.6
    },
    {
      department: 'HR',
      totalSpent: 43.67,
      percentage: 9.6,
      jobCount: 198,
      averageCostPerJob: 0.22,
      topService: 'translation',
      monthlyBudget: 18.00,
      budgetUtilization: 97.1
    },
    {
      department: 'IT',
      totalSpent: 125.22,
      percentage: 27.4,
      jobCount: 174,
      averageCostPerJob: 0.72,
      topService: 'document-intelligence',
      monthlyBudget: 35.00,
      budgetUtilization: 143.1
    }
  ],
  
  // User Spending Leaders
  topSpenders: [
    {
      userId: 'user-alice',
      name: 'Alice Johnson',
      department: 'Legal',
      totalSpent: 58.34,
      jobCount: 167,
      averageCostPerJob: 0.35,
      percentageOfTotal: 12.8
    },
    {
      userId: 'user-bob',
      name: 'Bob Smith',
      department: 'Marketing',
      totalSpent: 47.89,
      jobCount: 142,
      averageCostPerJob: 0.34,
      percentageOfTotal: 10.5
    },
    {
      userId: 'user-charlie',
      name: 'Charlie Brown',
      department: 'Operations',
      totalSpent: 41.23,
      jobCount: 98,
      averageCostPerJob: 0.42,
      percentageOfTotal: 9.0
    },
    {
      userId: 'user-diana',
      name: 'Diana Prince',
      department: 'HR',
      totalSpent: 29.67,
      jobCount: 89,
      averageCostPerJob: 0.33,
      percentageOfTotal: 6.5
    },
    {
      userId: 'user-eve',
      name: 'Eve Wilson',
      department: 'Finance',
      totalSpent: 34.12,
      jobCount: 76,
      averageCostPerJob: 0.45,
      percentageOfTotal: 7.5
    }
  ],
  
  // Cost Efficiency Metrics
  efficiency: {
    costPerSuccessfulJob: 0.39, // Total cost / successful jobs
    costSavingsFromBatchProcessing: 67.34, // Savings from using batch vs real-time
    failedJobCostImpact: 0.00, // No cost for failed jobs
    
    // Cost optimization opportunities
    optimizations: [
      {
        opportunity: 'Batch Transcription Usage',
        potentialSavings: 28.45,
        description: 'Switch from fast to batch transcription where timing allows',
        affectedJobs: 89
      },
      {
        opportunity: 'File Size Optimization',
        potentialSavings: 15.67,
        description: 'Compress large files before processing',
        affectedJobs: 45
      },
      {
        opportunity: 'Retry Reduction',
        potentialSavings: 8.23,
        description: 'Improve file validation to reduce failed attempts',
        affectedJobs: 23
      }
    ]
  },
  
  // Budget vs Actual Analysis
  budgetAnalysis: {
    totalBudget: 150.00, // Monthly budget
    actualSpend: 89.45, // Current month
    remaining: 60.55,
    utilizationRate: 59.6, // percentage
    projectedOverrun: false,
    daysLeftInPeriod: 15,
    
    // Budget allocation vs actual
    allocation: [
      {
        service: 'document-intelligence',
        budgeted: 65.00,
        actual: 36.78,
        variance: -28.22,
        utilizationRate: 56.6
      },
      {
        service: 'translation',
        budgeted: 50.00,
        actual: 31.24,
        variance: -18.76,
        utilizationRate: 62.5
      },
      {
        service: 'transcription',
        budgeted: 35.00,
        actual: 21.43,
        variance: -13.57,
        utilizationRate: 61.2
      }
    ]
  },
  
  // Cost Forecasting
  forecasting: {
    nextMonthPrediction: 94.50,
    quarterPrediction: 278.45,
    yearPrediction: 1124.67,
    
    // Trend factors
    trendFactors: {
      userGrowth: 1.08, // 8% monthly user growth
      usageIncrease: 1.12, // 12% monthly usage increase per user
      seasonality: 0.95, // 5% decrease expected next month (seasonal)
    },
    
    // Confidence intervals
    confidence: {
      low: 267.34, // Quarter low estimate
      high: 298.76, // Quarter high estimate
      mostLikely: 278.45
    }
  },
  
  // ROI and Value Metrics
  valueMetrics: {
    estimatedTimeSaved: 2847, // hours
    hourlyValueOfTimeSaved: 75.00, // $ per hour
    totalValueGenerated: 213525.00, // Time saved * hourly value
    roi: 46650, // percentage (value / cost * 100)
    
    // Service-specific value
    serviceValue: {
      documentIntelligence: {
        timeSavedPerJob: 2.5, // hours
        valuePerJob: 187.50,
        totalValue: 105187.50
      },
      translation: {
        timeSavedPerJob: 1.8,
        valuePerJob: 135.00,
        totalValue: 58860.00
      },
      transcription: {
        timeSavedPerJob: 3.2,
        valuePerJob: 240.00,
        totalValue: 60000.00
      }
    }
  },
  
  // Billing and Invoice Data
  billing: {
    currentInvoicePeriod: {
      startDate: '2025-06-01',
      endDate: '2025-06-30',
      currentCharges: 89.45,
      estimatedTotal: 94.50
    },
    
    recentInvoices: [
      {
        period: 'May 2025',
        amount: 76.32,
        dueDate: '2025-06-15',
        status: 'paid',
        services: {
          documentIntelligence: 32.14,
          translation: 26.78,
          transcription: 17.40
        }
      },
      {
        period: 'April 2025',
        amount: 68.91,
        dueDate: '2025-05-15',
        status: 'paid',
        services: {
          documentIntelligence: 29.45,
          translation: 24.12,
          transcription: 15.34
        }
      },
      {
        period: 'March 2025',
        amount: 71.23,
        dueDate: '2025-04-15',
        status: 'paid',
        services: {
          documentIntelligence: 30.87,
          translation: 25.34,
          transcription: 15.02
        }
      }
    ]
  },
  
  // Cost Alerts and Notifications
  alerts: {
    budgetAlerts: [
      {
        type: 'approaching_limit',
        department: 'Legal',
        currentSpend: 23.45,
        budgetLimit: 25.00,
        utilizationRate: 93.8,
        daysRemaining: 15
      }
    ],
    
    anomalies: [
      {
        type: 'unusual_spike',
        service: 'transcription',
        date: '2025-06-14',
        amount: 12.45,
        normalRange: '3.00-6.00',
        investigation: 'Large batch job from Operations team'
      }
    ],
    
    recommendations: [
      {
        type: 'cost_optimization',
        priority: 'medium',
        description: 'Consider batch processing for non-urgent transcription jobs',
        potentialSavings: 28.45
      },
      {
        type: 'budget_reallocation',
        priority: 'low',
        description: 'IT department consistently under-budget, consider reallocation',
        amount: 15.00
      }
    ]
  }
};

export default costAnalytics;