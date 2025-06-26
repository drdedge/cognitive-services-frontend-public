/**
 * Frontend-Backend Integration Example
 * ====================================
 * 
 * This example demonstrates how the frontend services integrate with the backend APIs.
 * Run this example to test the complete integration flow.
 */

import documentIntelligenceService from './frontend/src/services/documentIntelligenceService.js';
import translationService from './frontend/src/services/translationService.js';
import transcriptionService from './frontend/src/services/transcriptionService.js';
import websocketService from './frontend/src/services/websocketService.js';

/**
 * Example 1: Document Intelligence Integration
 */
async function documentIntelligenceExample() {
  console.log('🔍 Document Intelligence Integration Example');
  console.log('============================================\n');

  try {
    // 1. Get supported types
    console.log('📋 Getting supported document types...');
    const supportedTypes = await documentIntelligenceService.getSupportedTypes();
    console.log('Supported formats:', supportedTypes.formats.map(f => f.extension).join(', '));

    // 2. Get analysis types
    console.log('\n🔬 Getting analysis types...');
    const analysisTypes = await documentIntelligenceService.getAnalysisTypes();
    console.log('Available analysis types:', analysisTypes.types.map(t => t.id).join(', '));

    // 3. Estimate cost
    console.log('\n💰 Estimating processing cost...');
    const costEstimate = await documentIntelligenceService.estimateCost({
      fileSize: 1024 * 1024, // 1MB
      fileType: 'pdf',
      analysisType: 'layout'
    });
    console.log(`Estimated cost: $${costEstimate.estimated_cost} USD for ${costEstimate.estimated_pages} pages`);

    // 4. Simulate file processing
    console.log('\n📄 Simulating document processing...');
    
    // Create a mock file for demonstration
    const mockFile = new File(['Mock PDF content'], 'test.pdf', { type: 'application/pdf' });
    
    // Start processing
    const processingResult = await documentIntelligenceService.processDocument(
      mockFile,
      { analysisType: 'layout' },
      (progress) => console.log(`Upload progress: ${progress}%`)
    );
    
    console.log('Processing started:', processingResult);
    
    // Set up WebSocket to monitor progress
    const unsubscribe = websocketService.subscribe(
      processingResult.task_id,
      'progress',
      (data) => {
        console.log(`Processing progress: ${data.progress}% - ${data.message}`);
      }
    );
    
    // Monitor for completion
    websocketService.subscribe(
      processingResult.task_id,
      'completed',
      (data) => {
        console.log('✅ Document processing completed!', data);
        unsubscribe();
      }
    );
    
    // Check status periodically
    const status = await documentIntelligenceService.getStatus(processingResult.task_id);
    console.log('Current status:', status);

  } catch (error) {
    console.error('❌ Document Intelligence error:', error.message);
  }
}

/**
 * Example 2: Translation Integration
 */
async function translationExample() {
  console.log('\n🌐 Translation Integration Example');
  console.log('==================================\n');

  try {
    // 1. Get supported languages
    console.log('🗣️ Getting supported languages...');
    const languages = await translationService.getSupportedLanguages();
    console.log(`Found ${languages.length} supported languages`);

    // 2. Estimate translation cost
    console.log('\n💰 Estimating translation cost...');
    const costEstimate = await translationService.estimateCost({
      text: 'Hello world, this is a test translation.',
      targetLanguage: 'es'
    });
    console.log(`Estimated cost: $${costEstimate.estimated_cost} USD for ${costEstimate.character_count} characters`);

    // 3. Translate text
    console.log('\n🔄 Translating text...');
    const translation = await translationService.translateText({
      text: 'Hello world, how are you today?',
      targetLanguage: 'es',
      sourceLanguage: 'en'
    });
    console.log('Translation result:', translation);

    // 4. Batch translation
    console.log('\n📦 Batch translation...');
    const batchResult = await translationService.translateBatch({
      texts: ['Hello', 'Good morning', 'Thank you'],
      targetLanguage: 'fr'
    });
    console.log('Batch translation results:', batchResult);

    // 5. Simulate document translation
    console.log('\n📄 Simulating document translation...');
    const mockDoc = new File(['This is a document to translate.'], 'test.txt', { type: 'text/plain' });
    
    const docTranslation = await translationService.translateDocument(
      mockDoc,
      { targetLanguage: 'de', sourceLanguage: 'en' },
      (progress) => console.log(`Translation upload progress: ${progress}%`)
    );
    
    console.log('Document translation started:', docTranslation);

  } catch (error) {
    console.error('❌ Translation error:', error.message);
  }
}

/**
 * Example 3: Transcription Integration
 */
async function transcriptionExample() {
  console.log('\n🎤 Transcription Integration Example');
  console.log('====================================\n');

  try {
    // 1. Get supported languages
    console.log('🗣️ Getting supported languages...');
    const languages = await transcriptionService.getSupportedLanguages();
    console.log('Supported languages for transcription:', languages);

    // 2. Estimate transcription cost
    console.log('\n💰 Estimating transcription cost...');
    const costEstimate = await transcriptionService.estimateCost({
      duration: 300, // 5 minutes
      fileSize: 5 * 1024 * 1024, // 5MB
      speakerDiarization: true
    });
    console.log(`Estimated cost: $${costEstimate.estimated_cost} USD for ${costEstimate.estimated_duration / 60} minutes`);

    // 3. Simulate audio transcription
    console.log('\n🎵 Simulating audio transcription...');
    const mockAudio = new File(['Mock audio data'], 'test.wav', { type: 'audio/wav' });
    
    const transcription = await transcriptionService.transcribeAudio(
      mockAudio,
      {
        language: 'en-US',
        speakerDiarization: true,
        outputFormat: 'text',
        punctuation: true
      },
      (progress) => console.log(`Audio upload progress: ${progress}%`)
    );
    
    console.log('Transcription started:', transcription);
    
    // Monitor transcription progress
    const unsubscribe = websocketService.subscribe(
      transcription.task_id,
      '*',
      (data) => {
        console.log('Transcription update:', data);
      }
    );

  } catch (error) {
    console.error('❌ Transcription error:', error.message);
  }
}

/**
 * Example 4: WebSocket Integration
 */
async function websocketExample() {
  console.log('\n🔌 WebSocket Integration Example');
  console.log('=================================\n');

  try {
    // 1. Test WebSocket connection
    console.log('🔗 Connecting to WebSocket...');
    await websocketService.connect();
    console.log('WebSocket state:', websocketService.getState());

    // 2. Subscribe to updates for a mock task
    const mockTaskId = 'demo_task_123';
    console.log(`📡 Subscribing to updates for task: ${mockTaskId}`);
    
    const unsubscribe = websocketService.subscribeToAll(mockTaskId, (data) => {
      console.log('📨 WebSocket message received:', data);
    });

    // 3. Simulate sending messages
    console.log('📤 Sending test messages...');
    websocketService.sendMessage('subscribe', { task_id: mockTaskId });
    
    // Send ping
    setTimeout(() => {
      websocketService.sendMessage('ping', {});
    }, 1000);

    // Cleanup after demo
    setTimeout(() => {
      unsubscribe();
      console.log('🧹 Cleaned up WebSocket subscriptions');
    }, 5000);

  } catch (error) {
    console.error('❌ WebSocket error:', error.message);
  }
}

/**
 * Example 5: Error Handling Integration
 */
async function errorHandlingExample() {
  console.log('\n🚨 Error Handling Integration Example');
  console.log('======================================\n');

  // Test various error scenarios
  try {
    console.log('Testing invalid file type...');
    const invalidFile = new File(['test'], 'test.xyz', { type: 'application/octet-stream' });
    await documentIntelligenceService.processDocument(invalidFile);
  } catch (error) {
    console.log('✅ Caught expected error:', error.message);
  }

  try {
    console.log('\nTesting invalid task ID status...');
    await documentIntelligenceService.getStatus('invalid_task_id');
  } catch (error) {
    console.log('✅ Caught expected error:', error.message);
  }

  try {
    console.log('\nTesting translation with empty text...');
    await translationService.translateText({
      text: '',
      targetLanguage: 'es'
    });
  } catch (error) {
    console.log('✅ Caught expected error:', error.message);
  }
}

/**
 * Main integration test runner
 */
async function runIntegrationTests() {
  console.log('🚀 Starting Frontend-Backend Integration Tests');
  console.log('===============================================\n');

  console.log('ℹ️  Note: Some tests may show errors if the backend is not running');
  console.log('   or if Azure services are not configured. This is expected in demo mode.\n');

  try {
    await documentIntelligenceExample();
    await translationExample();
    await transcriptionExample();
    await websocketExample();
    await errorHandlingExample();
    
    console.log('\n🎉 Integration tests completed!');
    console.log('\nNext steps:');
    console.log('- Start the backend server: cd backend && python main.py');
    console.log('- Start the frontend: cd frontend && npm run dev');
    console.log('- Configure Azure service credentials');
    console.log('- Test with real files and data');
    
  } catch (error) {
    console.error('\n💥 Integration test failed:', error);
  }
}

// Export for use in different environments
export {
  documentIntelligenceExample,
  translationExample,
  transcriptionExample,
  websocketExample,
  errorHandlingExample,
  runIntegrationTests
};

// Run if this script is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  runIntegrationTests();
}