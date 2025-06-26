# Mock Data Directory

This directory contains comprehensive mock data for the Azure Cognitive Services frontend dashboard. The data is organized to provide realistic analytics and demonstrate the application's capabilities.

## Directory Structure

```
mock-data/
├── analytics/          # Analytics and aggregated data
│   ├── jobAnalytics.js       # Job statistics and performance metrics
│   ├── userAnalytics.js      # User activity and behavior data
│   ├── serviceMetrics.js     # Service-specific performance data
│   └── costAnalytics.js      # Cost breakdown and financial analytics
├── jobs/              # Detailed job data
│   ├── completedJobs.js      # Successfully completed jobs with results
│   ├── processingJobs.js     # Currently processing jobs
│   └── failedJobs.js         # Failed jobs with error details
└── index.js           # Main export file for all mock data
```

## Customizing Mock Data

### Adding New Jobs
Edit the appropriate file in the `jobs/` directory to add new job records. Each job should follow this schema:

```javascript
{
  id: 'unique-job-id',
  userId: 'user-identifier',
  service: 'document-intelligence' | 'translation' | 'transcription',
  fileName: 'original-filename.ext',
  fileSize: 1234567, // size in bytes
  pageCount: 10, // for documents
  characterCount: 5000, // for translation
  audioDuration: 3600, // for transcription (seconds)
  processingTime: 30000, // processing time in milliseconds
  cost: 1.25, // actual cost in USD
  timestamp: '2025-06-15T10:30:00Z',
  status: 'completed' | 'processing' | 'failed' | 'cancelled',
  results: { /* service-specific results */ },
  metadata: { /* additional file metadata */ }
}
```

### Service-Specific Fields

**Document Intelligence:**
- `pageCount`: Number of pages processed
- `tablesExtracted`: Number of tables found
- `confidenceScore`: Average confidence (0-1)

**Translation:**
- `characterCount`: Total characters translated
- `sourceLanguage`: Source language code
- `targetLanguage`: Target language code
- `autoDetected`: Whether language was auto-detected

**Transcription:**
- `audioDuration`: Duration in seconds
- `transcriptionType`: 'fast' | 'batch'
- `speakers`: Number of speakers identified
- `wordCount`: Number of words transcribed

### Analytics Customization

The analytics files contain aggregated data and can be customized to show different trends, user patterns, and business metrics. Modify these files to reflect your desired dashboard analytics.

## Data Refresh

The mock data is designed to be easily refreshed or regenerated. You can:
1. Modify individual job records
2. Add new user patterns
3. Adjust cost calculations
4. Update service performance metrics

## Usage in Components

Import specific data sets as needed:

```javascript
// Import specific analytics
import { jobAnalytics } from '@/mock-data/analytics/jobAnalytics'

// Import all job data
import { completedJobs, processingJobs } from '@/mock-data/jobs'

// Import everything
import mockData from '@/mock-data'
```

## Data Generation

The mock data is generated with realistic patterns:
- **Temporal Distribution**: Jobs spread across realistic time periods
- **User Behavior**: Some users are more active than others
- **Service Usage**: Reflects typical enterprise usage patterns
- **File Sizes**: Realistic file size distributions
- **Processing Times**: Based on actual Azure service performance
- **Costs**: Calculated using real Azure pricing