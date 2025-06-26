<template>
  <div class="analytics-overview">
    <!-- Statistics Cards -->
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Total Jobs</dt>
                <dd class="text-lg font-medium text-gray-900">{{ formatNumber(overview.totalJobs) }}</dd>
              </dl>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 px-5 py-3">
          <div class="text-sm">
            <span class="font-medium text-green-600">{{ formatPercentage(trends.jobVolume.change) }}%</span>
            <span class="text-gray-500">from last period</span>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Success Rate</dt>
                <dd class="text-lg font-medium text-gray-900">{{ formatPercentage(overview.successRate) }}%</dd>
              </dl>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 px-5 py-3">
          <div class="text-sm">
            <span class="font-medium text-green-600">+{{ formatPercentage(trends.successRate.change) }}%</span>
            <span class="text-gray-500">improvement</span>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Total Cost</dt>
                <dd class="text-lg font-medium text-gray-900">${{ formatNumber(overview.totalCost) }}</dd>
              </dl>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 px-5 py-3">
          <div class="text-sm">
            <span class="font-medium text-blue-600">${{ formatNumber(overview.averageCostPerJob) }}</span>
            <span class="text-gray-500">per job</span>
          </div>
        </div>
      </div>

      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">Avg Processing Time</dt>
                <dd class="text-lg font-medium text-gray-900">{{ formatProcessingTime(overview.averageProcessingTime) }}</dd>
              </dl>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 px-5 py-3">
          <div class="text-sm">
            <span class="font-medium text-green-600">{{ formatPercentage(Math.abs(trends.processingTime.change)) }}%</span>
            <span class="text-gray-500">faster</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Charts Row -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
      <!-- Service Distribution Chart -->
      <div class="bg-white p-6 rounded-lg shadow">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Jobs by Service</h3>
        <div class="h-64">
          <Doughnut
            :data="serviceChartData"
            :options="chartOptions.doughnut"
          />
        </div>
        <div class="mt-4 grid grid-cols-3 gap-4 text-sm">
          <div class="text-center">
            <div class="font-medium text-blue-600">{{ serviceBreakdown.documentIntelligence.total }}</div>
            <div class="text-gray-500">Document Intel</div>
          </div>
          <div class="text-center">
            <div class="font-medium text-green-600">{{ serviceBreakdown.translation.total }}</div>
            <div class="text-gray-500">Translation</div>
          </div>
          <div class="text-center">
            <div class="font-medium text-purple-600">{{ serviceBreakdown.transcription.total }}</div>
            <div class="text-gray-500">Transcription</div>
          </div>
        </div>
      </div>

      <!-- Jobs Over Time Chart -->
      <div class="bg-white p-6 rounded-lg shadow">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Jobs Over Time (Last 30 Days)</h3>
        <div class="h-64">
          <Line
            :data="timeSeriesChartData"
            :options="chartOptions.line"
          />
        </div>
      </div>
    </div>

    <!-- Success Rate Trends -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Weekly Pattern -->
      <div class="bg-white p-6 rounded-lg shadow">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Weekly Pattern</h3>
        <div class="h-48">
          <Bar
            :data="weeklyPatternData"
            :options="chartOptions.bar"
          />
        </div>
      </div>

      <!-- Error Categories -->
      <div class="bg-white p-6 rounded-lg shadow">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Error Categories</h3>
        <div class="space-y-3">
          <div v-for="error in errorAnalytics.errorCategories.slice(0, 5)" :key="error.category" class="flex items-center justify-between">
            <div class="flex items-center">
              <div class="w-3 h-3 bg-red-500 rounded-full mr-3"></div>
              <span class="text-sm text-gray-700">{{ error.description }}</span>
            </div>
            <span class="text-sm font-medium text-gray-900">{{ error.count }}</span>
          </div>
        </div>
      </div>

      <!-- Top Users -->
      <div class="bg-white p-6 rounded-lg shadow">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Top Users</h3>
        <div class="space-y-3">
          <div v-for="user in topUsers.slice(0, 5)" :key="user.userId" class="flex items-center justify-between">
            <div>
              <div class="text-sm font-medium text-gray-900">{{ user.name }}</div>
              <div class="text-xs text-gray-500">{{ user.department }}</div>
            </div>
            <div class="text-right">
              <div class="text-sm font-medium text-gray-900">{{ user.totalJobs }}</div>
              <div class="text-xs text-gray-500">${{ user.totalSpent.toFixed(2) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  BarElement
} from 'chart.js'
import { Doughnut, Line, Bar } from 'vue-chartjs'

// Register Chart.js components
ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  BarElement
)

// Import mock data
import { jobAnalytics, userAnalytics } from '@/mock-data'

// Destructure analytics data
const overview = jobAnalytics.overview
const serviceBreakdown = jobAnalytics.serviceBreakdown
const timeSeriesData = jobAnalytics.timeSeriesData
const weeklyPattern = jobAnalytics.weeklyPattern
const errorAnalytics = jobAnalytics.errorAnalytics
const trends = jobAnalytics.trends
const topUsers = userAnalytics.topUsersByJobs

// Chart data configurations
const serviceChartData = computed(() => ({
  labels: ['Document Intelligence', 'Translation', 'Transcription'],
  datasets: [{
    data: [
      serviceBreakdown.documentIntelligence.total,
      serviceBreakdown.translation.total,
      serviceBreakdown.transcription.total
    ],
    backgroundColor: [
      '#3B82F6', // Blue
      '#10B981', // Green  
      '#8B5CF6'  // Purple
    ],
    borderWidth: 2,
    borderColor: '#ffffff'
  }]
}))

const timeSeriesChartData = computed(() => ({
  labels: timeSeriesData.slice(-14).map(d => new Date(d.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })),
  datasets: [
    {
      label: 'Completed Jobs',
      data: timeSeriesData.slice(-14).map(d => d.completedJobs),
      borderColor: '#10B981',
      backgroundColor: 'rgba(16, 185, 129, 0.1)',
      tension: 0.4
    },
    {
      label: 'Failed Jobs', 
      data: timeSeriesData.slice(-14).map(d => d.failedJobs),
      borderColor: '#EF4444',
      backgroundColor: 'rgba(239, 68, 68, 0.1)',
      tension: 0.4
    }
  ]
}))

const weeklyPatternData = computed(() => {
  // Generate service-specific data for stacked bars
  const days = weeklyPattern.map(d => d.day.substring(0, 3))
  
  // Simulate service breakdown for each day
  const documentIntelData = weeklyPattern.map(d => Math.floor(d.jobs * 0.45))
  const translationData = weeklyPattern.map(d => Math.floor(d.jobs * 0.35))
  const transcriptionData = weeklyPattern.map(d => Math.floor(d.jobs * 0.20))
  
  return {
    labels: days,
    datasets: [
      {
        label: 'Document Intelligence',
        data: documentIntelData,
        backgroundColor: '#3B82F6',
        borderRadius: 4
      },
      {
        label: 'Translation',
        data: translationData,
        backgroundColor: '#10B981',
        borderRadius: 4
      },
      {
        label: 'Transcription',
        data: transcriptionData,
        backgroundColor: '#8B5CF6',
        borderRadius: 4
      }
    ]
  }
})

// Chart options
const chartOptions = {
  doughnut: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom'
      }
    }
  },
  line: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top'
      }
    },
    scales: {
      y: {
        beginAtZero: true
      }
    }
  },
  bar: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: true,
        position: 'bottom'
      }
    },
    scales: {
      x: {
        stacked: true
      },
      y: {
        stacked: true,
        beginAtZero: true
      }
    }
  }
}

// Utility functions
const formatNumber = (num) => {
  return new Intl.NumberFormat().format(num)
}

const formatPercentage = (num) => {
  return Math.round(num * 10) / 10
}

const formatProcessingTime = (ms) => {
  const seconds = Math.floor(ms / 1000)
  return `${seconds}s`
}
</script>

<style scoped>
.analytics-overview {
  /* Any additional styling if needed */
}
</style>