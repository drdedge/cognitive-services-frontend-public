# backend/services/translation/service.py
"""
Translation Service
===================

Service wrapper for Azure Translator operations.
"""

import os
import logging
import aiohttp
import asyncio
from typing import List, Dict, Any, Optional, Callable
from uuid import uuid4

logger = logging.getLogger(__name__)


class TranslationService:
    """Service for translation operations using Azure Translator."""
    
    def __init__(self):
        """Initialize the service with Azure credentials."""
        self.endpoint = os.getenv("AZURE_TRANSLATOR_ENDPOINT", "https://api.cognitive.microsofttranslator.com")
        self.key = os.getenv("AZURE_TRANSLATOR_KEY")
        self.region = os.getenv("AZURE_TRANSLATOR_REGION", "eastus")  # Default to eastus
        
        if not self.key or self.key == "your_translator_key_here":
            raise ValueError("Azure Translator key not configured properly")
        
        # Build base headers - X-ClientTraceId will be added per request
        self.headers = {
            'Ocp-Apim-Subscription-Key': self.key,
            'Content-type': 'application/json'
        }
        
        # Always add region header for Azure Cognitive Services endpoints
        if self.region:
            self.headers['Ocp-Apim-Subscription-Region'] = self.region
        
        logger.info(f"Translation service initialized with endpoint: {self.endpoint}, region: {self.region}")
    
    def _get_headers(self):
        """Get headers with fresh trace ID."""
        headers = self.headers.copy()
        headers['X-ClientTraceId'] = str(uuid4())
        return headers
    
    async def translate_text(
        self,
        text: str,
        target_languages: List[str],
        source_language: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Translate text to target languages.
        
        Args:
            text: Text to translate
            target_languages: List of target language codes
            source_language: Source language code (auto-detect if None)
        
        Returns:
            Translation results
        """
        # Handle both types of endpoints
        if "cognitiveservices.azure.com" in self.endpoint:
            # Azure Cognitive Services endpoint
            url = f"{self.endpoint.rstrip('/')}/translator/text/v3.0/translate"
        else:
            # Standard translator endpoint
            url = f"{self.endpoint.rstrip('/')}/translate"
        
        params = {
            'api-version': '3.0',
            'to': target_languages
        }
        
        # Only add 'from' parameter if source_language is provided and not 'auto'
        if source_language and source_language not in ['auto', 'auto-detect', '']:
            params['from'] = source_language
        
        body = [{'text': text}]
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params, headers=self._get_headers(), json=body) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Translation API error: {error_text}")
                
                result = await response.json()
                
                # Format response
                translations = []
                detected_language = None
                
                if result and len(result) > 0:
                    item = result[0]
                    
                    if 'detectedLanguage' in item:
                        detected_language = item['detectedLanguage']['language']
                    
                    for translation in item.get('translations', []):
                        translations.append({
                            'language': translation['to'],
                            'text': translation['text']
                        })
                
                return {
                    'translations': translations,
                    'detected_language': detected_language
                }
    
    async def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect the language of the provided text.
        
        Args:
            text: Text to analyze
        
        Returns:
            Detected language information
        """
        # Handle both types of endpoints
        if "cognitiveservices.azure.com" in self.endpoint:
            url = f"{self.endpoint.rstrip('/')}/translator/text/v3.0/detect"
        else:
            url = f"{self.endpoint.rstrip('/')}/detect"
        
        params = {'api-version': '3.0'}
        body = [{'text': text}]
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params, headers=self._get_headers(), json=body) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Language detection API error: {error_text}")
                
                result = await response.json()
                
                if result and len(result) > 0:
                    detection = result[0]
                    return {
                        'language': detection['language'],
                        'confidence': detection['score'],
                        'is_translation_supported': detection.get('isTranslationSupported', True),
                        'is_transliteration_supported': detection.get('isTransliterationSupported', False)
                    }
                
                raise Exception("No language detected")
    
    async def get_supported_languages(self) -> List[Dict[str, str]]:
        """Get list of supported languages."""
        # Handle both types of endpoints
        if "cognitiveservices.azure.com" in self.endpoint:
            url = f"{self.endpoint.rstrip('/')}/translator/text/v3.0/languages"
        else:
            url = f"{self.endpoint.rstrip('/')}/languages"
        
        params = {'api-version': '3.0', 'scope': 'translation'}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, headers=self._get_headers()) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Languages API error: {error_text}")
                
                result = await response.json()
                languages = []
                
                for code, info in result.get('translation', {}).items():
                    languages.append({
                        'code': code,
                        'name': info.get('name', code),
                        'native_name': info.get('nativeName', info.get('name', code)),
                        'direction': info.get('dir', 'ltr')
                    })
                
                return sorted(languages, key=lambda x: x['name'])
    
    async def translate_document(
        self,
        file,
        target_language: str,
        source_language: Optional[str] = None,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Translate a document file.
        
        Args:
            file: File object
            target_language: Target language code
            source_language: Source language code
            progress_callback: Progress callback function
        
        Returns:
            Translation results
        """
        # For now, extract text and translate
        # In production, use Azure Document Translation service
        
        if progress_callback:
            await progress_callback(10, "Reading document...")
        
        # Read file content
        content = await file.read()
        text = content.decode('utf-8', errors='ignore')
        
        if progress_callback:
            await progress_callback(30, "Detecting language...")
        
        # Detect language if not provided
        if not source_language:
            detection = await self.detect_language(text[:1000])  # Use first 1000 chars
            source_language = detection['language']
        
        if progress_callback:
            await progress_callback(50, f"Translating from {source_language} to {target_language}...")
        
        # Translate text
        result = await self.translate_text(text, [target_language], source_language)
        
        if progress_callback:
            await progress_callback(90, "Formatting results...")
        
        return {
            'original_text': text,
            'translated_text': result['translations'][0]['text'],
            'source_language': source_language,
            'target_language': target_language,
            'word_count': len(text.split())
        }
    
    async def translate_batch(
        self,
        texts: List[str],
        target_languages: List[str],
        source_language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Translate multiple texts in batch.
        
        Args:
            texts: List of texts to translate
            target_languages: Target language codes
            source_language: Source language code
        
        Returns:
            List of translation results
        """
        # Handle both types of endpoints
        if "cognitiveservices.azure.com" in self.endpoint:
            url = f"{self.endpoint.rstrip('/')}/translator/text/v3.0/translate"
        else:
            url = f"{self.endpoint.rstrip('/')}/translate"
        
        params = {
            'api-version': '3.0',
            'to': target_languages
        }
        
        # Only add 'from' parameter if source_language is provided and not 'auto'
        if source_language and source_language not in ['auto', 'auto-detect', '']:
            params['from'] = source_language
        
        body = [{'text': text} for text in texts]
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params, headers=self._get_headers(), json=body) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Batch translation API error: {error_text}")
                
                results = await response.json()
                
                # Format results
                formatted_results = []
                for i, result in enumerate(results):
                    translations = []
                    detected_language = result.get('detectedLanguage', {}).get('language')
                    
                    for translation in result.get('translations', []):
                        translations.append({
                            'language': translation['to'],
                            'text': translation['text']
                        })
                    
                    formatted_results.append({
                        'original_text': texts[i],
                        'translations': translations,
                        'detected_language': detected_language
                    })
                
                return formatted_results


# Singleton instance
_service_instance = None


def get_translation_service() -> TranslationService:
    """Get or create the translation service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = TranslationService()
    return _service_instance