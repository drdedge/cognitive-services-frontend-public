<template>
  <div class="py-10">
    <header>
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 class="text-3xl font-bold leading-tight text-[#3B5781]">
          Usage Analytics & History
        </h1>
        <p class="mt-2 text-lg text-gray-600">
          Track your Azure Cognitive Services usage, analyze trends, and download processing results
        </p>
      </div>
    </header>

    <main>
      <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
        <!-- Analytics Overview -->
        <div class="mt-8 mx-4 sm:mx-0">
          <AnalyticsOverview />
        </div>

        <!-- Jobs Table -->
        <div class="mt-8 mx-4 sm:mx-0">
          <JobsTable 
            :highlight-job-id="highlightJobId"
            @download-results="handleDownloadResults"
          />
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import AnalyticsOverview from '@/components/analytics/AnalyticsOverview.vue'
import JobsTable from '@/components/JobsTable.vue'
import JSZip from 'jszip'

const route = useRoute()

// Get job ID from query params if navigated from recent jobs
const highlightJobId = computed(() => route.query.jobId)

// Handle downloading results
const handleDownloadResults = async (job) => {
  try {
    const zip = new JSZip()
    
    // Add files based on service type
    switch (job.service) {
      case 'document-intelligence':
        // Add extracted files
        zip.file('extracted_text.md', `# ${job.fileName} - Extracted Content\n\nThis is sample extracted text from your document.\n\n## Tables Found\n${job.results?.tablesExtracted || 0} tables were extracted.\n\n## Confidence Score\nAverage confidence: ${job.results?.confidenceScore || 0.95}`)
        if (job.results?.extractedTables) {
          job.results.extractedTables.forEach(table => {
            zip.file(table.name, 'Sample CSV data\nColumn1,Column2,Column3\nData1,Data2,Data3')
          })
        }
        break
        
      case 'translation':
        // Add translated document
        zip.file(`translated_${job.fileName}`, `Translated content of ${job.fileName}\n\nSource: ${job.results?.sourceLanguage || 'auto'}\nTarget: ${job.results?.targetLanguage || 'en'}\n\nThis is the translated content...`)
        zip.file('translation_metadata.json', JSON.stringify({
          sourceLanguage: job.results?.sourceLanguage,
          targetLanguage: job.results?.targetLanguage,
          confidence: job.results?.confidenceScore,
          wordCount: job.results?.wordCount
        }, null, 2))
        break
        
      case 'transcription':
        // Add transcript files
        if (job.results?.transcriptFormats) {
          job.results.transcriptFormats.forEach(format => {
            let content = `Transcript of ${job.fileName}`
            if (format.format === 'srt') {
              content = `1\n00:00:00,000 --> 00:00:05,000\nSample subtitle content\n\n2\n00:00:05,000 --> 00:00:10,000\nMore subtitle content`
            } else if (format.format === 'json') {
              content = JSON.stringify({
                fileName: job.fileName,
                duration: job.audioDuration,
                speakers: job.results?.speakers,
                transcript: 'Sample transcript content...'
              }, null, 2)
            }
            zip.file(format.file, content)
          })
        }
        break
    }
    
    // Add processing report
    zip.file('processing_report.txt', `Processing Report
================
Job ID: ${job.id}
File: ${job.fileName}
Service: ${job.service}
Status: ${job.status}
Processing Time: ${job.processingTime}ms
Cost: $${job.cost}
Timestamp: ${new Date(job.timestamp).toLocaleString()}

This is a sample results package. In production, this would contain your actual processed files.`)
    
    // Generate and download the ZIP file
    const blob = await zip.generateAsync({ type: 'blob' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `results_${job.id}.zip`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
  } catch (error) {
    console.error('Error downloading results:', error)
    alert('Failed to download results. Please try again.')
  }
}

// Scroll to highlighted job if navigated from recent jobs
onMounted(() => {
  if (highlightJobId.value) {
    // Give the table time to render, then scroll
    setTimeout(() => {
      const element = document.querySelector(`[data-job-id="${highlightJobId.value}"]`)
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' })
        element.classList.add('highlight-row')
      }
    }, 500)
  }
})
</script>

<style scoped>
:deep(.highlight-row) {
  animation: highlight 2s ease-in-out;
}

@keyframes highlight {
  0%, 100% { background-color: transparent; }
  50% { background-color: #FEF3C7; }
}
</style>