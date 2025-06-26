/**
 * Service Usage Examples
 * Examples of how to use the API services in components
 */

import {
  documentIntelligenceService,
  translationService,
  transcriptionService,
  websocketService,
  fileService,
} from './index';

/**
 * Example: Document Intelligence Processing
 */
export const processDocumentExample = async (file) => {
  try {
    // 1. Validate file
    const validation = fileService.validateFile(file, 'documentIntelligence');
    if (!validation.valid) {
      throw new Error(validation.error);
    }

    // 2. Estimate cost
    const costEstimate = await documentIntelligenceService.estimateCost({
      fileSize: file.size,
      fileType: fileService.getFileExtension(file.name),
      analysisType: 'layout'
    });
    console.log('Estimated cost:', costEstimate);

    // 3. Start processing with progress tracking
    const job = await documentIntelligenceService.processDocument(
      file,
      { analysisType: 'layout' },
      (progress) => console.log(`Upload progress: ${progress}%`)
    );

    // 4. Monitor progress with WebSocket
    const unsubscribe = websocketService.subscribe(job.job_id, '*', (data) => {
      console.log('Job update:', data);
    });

    // 5. Poll for completion (alternative to WebSocket)
    const result = await documentIntelligenceService.pollStatus(
      job.job_id,
      (status) => console.log('Status:', status.status, status.progress + '%')
    );

    // 6. Download results
    await documentIntelligenceService.downloadResults(job.job_id, 'document_results.zip');

    // 7. Cleanup
    unsubscribe();

    return result;
  } catch (error) {
    console.error('Document processing failed:', error.message);
    throw error;
  }
};

/**
 * Example: Text Translation
 */
export const translateTextExample = async (text, targetLanguage) => {
  try {
    // 1. Detect language if needed
    const detection = await translationService.detectLanguage(text);
    console.log('Detected language:', detection.language);

    // 2. Estimate cost
    const costEstimate = await translationService.estimateCost({
      characterCount: text.length,
      targetLanguage,
      sourceLanguage: detection.language
    });
    console.log('Translation cost:', costEstimate);

    // 3. Translate text
    const result = await translationService.translateText({
      text,
      targetLanguage,
      sourceLanguage: detection.language
    });

    console.log('Translation result:', result);
    return result;
  } catch (error) {
    console.error('Translation failed:', error.message);
    throw error;
  }
};

/**
 * Example: Document Translation
 */
export const translateDocumentExample = async (file, targetLanguage) => {
  try {
    // 1. Validate file
    const validation = fileService.validateFile(file, 'translation');
    if (!validation.valid) {
      throw new Error(validation.error);
    }

    // 2. Start translation
    const job = await translationService.translateDocument(
      file,
      { targetLanguage },
      (progress) => console.log(`Upload progress: ${progress}%`)
    );

    // 3. Monitor with WebSocket
    websocketService.subscribe(job.job_id, 'completed', async (data) => {
      console.log('Translation completed!');
      await translationService.downloadResults(job.job_id, 'translated_document');
    });

    return job;
  } catch (error) {
    console.error('Document translation failed:', error.message);
    throw error;
  }
};

/**
 * Example: Audio Transcription
 */
export const transcribeAudioExample = async (file) => {
  try {
    // 1. Validate file
    const validation = fileService.validateFile(file, 'transcription');
    if (!validation.valid) {
      throw new Error(validation.error);
    }

    // 2. Get audio metadata
    const metadata = await transcriptionService.getAudioMetadata(file);
    console.log('Audio metadata:', metadata);

    // 3. Estimate cost
    const costEstimate = await transcriptionService.estimateCost({
      duration: metadata.duration,
      fileSize: file.size,
      fileType: fileService.getFileExtension(file.name),
      speakerDiarization: true
    });
    console.log('Transcription cost:', costEstimate);

    // 4. Start transcription
    const job = await transcriptionService.transcribeAudio(
      file,
      {
        speakerDiarization: true,
        outputFormat: 'json',
        punctuation: true
      },
      (progress) => console.log(`Upload progress: ${progress}%`)
    );

    // 5. Monitor progress
    const result = await transcriptionService.pollStatus(
      job.job_id,
      (status) => {
        console.log(`Transcription: ${status.status} (${status.progress}%)`);
      },
      3000 // 3 second intervals
    );

    // 6. Download all formats
    await transcriptionService.downloadResults(job.job_id, 'all', 'transcript');

    return result;
  } catch (error) {
    console.error('Transcription failed:', error.message);
    throw error;
  }
};

/**
 * Example: WebSocket Connection Management
 */
export const webSocketExample = () => {
  // Connect to WebSocket
  websocketService.connect().then(() => {
    console.log('WebSocket connected');
  });

  // Subscribe to a specific job
  const jobId = 'example-job-123';
  const unsubscribe = websocketService.subscribe(jobId, '*', (data) => {
    switch (data.type) {
      case 'status_update':
        console.log('Status update:', data);
        break;
      case 'progress_update':
        console.log('Progress:', data.progress + '%');
        break;
      case 'job_completed':
        console.log('Job completed!');
        unsubscribe(); // Stop listening
        break;
      case 'job_failed':
        console.log('Job failed:', data.error);
        unsubscribe(); // Stop listening
        break;
    }
  });

  // Cleanup function
  return () => {
    unsubscribe();
    websocketService.disconnect();
  };
};

/**
 * Example: File Operations
 */
export const fileOperationsExample = async (file) => {
  try {
    // Basic file info
    console.log('File name:', file.name);
    console.log('File size:', fileService.formatFileSize(file.size));
    console.log('File extension:', fileService.getFileExtension(file.name));

    // Check if supported
    const isSupported = fileService.isSupported(file.name, 'documentIntelligence');
    console.log('Supported for Document Intelligence:', isSupported);

    // Calculate hash
    const hash = await fileService.calculateHash(file);
    console.log('File hash:', hash);

    // Create thumbnail for images
    if (file.type.startsWith('image/')) {
      const thumbnail = await fileService.createThumbnail(file, 150, 150);
      console.log('Thumbnail created:', thumbnail.substring(0, 50) + '...');
    }

    // Get audio duration for audio files
    if (file.type.startsWith('audio/')) {
      const duration = await fileService.getAudioDuration(file);
      console.log('Audio duration:', duration, 'seconds');
    }

    return {
      name: file.name,
      size: file.size,
      formattedSize: fileService.formatFileSize(file.size),
      extension: fileService.getFileExtension(file.name),
      hash,
      isSupported
    };
  } catch (error) {
    console.error('File operations failed:', error.message);
    throw error;
  }
};