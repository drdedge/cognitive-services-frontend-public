# backend/utils/config.py
"""
Minimal configuration for running with Document Intelligence only.
"""
import os
import logging
from typing import Optional, Dict, Any
from pydantic import Field, ConfigDict
from pydantic_settings import BaseSettings
from azure.core.credentials import AzureKeyCredential

logger = logging.getLogger(__name__)


class MinimalAzureConfig(BaseSettings):
    """Minimal configuration for Document Intelligence only."""
    
    # Document Intelligence (Required)
    doc_intelligence_endpoint: str
    doc_intelligence_key: str
    doc_intelligence_model: str = "layout"  # This will match AZURE_DOC_INTELLIGENCE_MODEL
    doc_intelligence_region: Optional[str] = Field(default=None, env="AZURE_DOC_INTELLIGENCE_REGION")
    
    # Make all other services with explicit env loading
    translator_endpoint: str = Field(default="", env="AZURE_TRANSLATOR_ENDPOINT")
    translator_key: str = Field(default="", env="AZURE_TRANSLATOR_KEY")
    translator_region: str = Field(default="", env="AZURE_TRANSLATOR_REGION")
    
    speech_endpoint: str = Field(default="", env="AZURE_SPEECH_ENDPOINT")
    speech_key: str = Field(default="", env="AZURE_SPEECH_KEY")
    speech_region: str = Field(default="", env="AZURE_SPEECH_REGION")
    
    storage_connection_string: str = Field(default="", env="AZURE_STORAGE_CONNECTION_STRING")
    storage_container: str = Field(default="cognitive-services", env="AZURE_STORAGE_CONTAINER")
    
    # Application settings
    cors_origins: str = Field(default="http://localhost:3000", env="CORS_ORIGINS")
    max_file_size_mb: int = 50
    job_timeout_minutes: int = 30
    cleanup_interval_hours: int = 24
    
    # Additional app settings (not prefixed with AZURE_)
    api_base_url: Optional[str] = "http://localhost:8000"
    frontend_port: Optional[int] = 3000
    
    # Performance
    max_concurrent_jobs: int = 10
    websocket_timeout_seconds: int = 300
    azure_timeout_seconds: int = 120
    
    model_config = ConfigDict(
        env_prefix="AZURE_",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding='utf-8',
        extra="ignore"  # Ignore extra fields instead of forbidding them
    )
    
    def get_doc_intelligence_credential(self) -> AzureKeyCredential:
        """Get Document Intelligence credential."""
        return AzureKeyCredential(self.doc_intelligence_key)
    
    def get_translator_credential(self) -> Optional[AzureKeyCredential]:
        """Get Translator credential."""
        if self.translator_key:
            return AzureKeyCredential(self.translator_key)
        return None
    
    def get_speech_credential(self) -> Optional[AzureKeyCredential]:
        """Get Speech Service credential."""
        if self.speech_key:
            return AzureKeyCredential(self.speech_key)
        return None
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024
    
    @property
    def job_timeout_seconds(self) -> int:
        """Get job timeout in seconds."""
        return self.job_timeout_minutes * 60
    
    @property
    def cleanup_interval_seconds(self) -> int:
        """Get cleanup interval in seconds."""
        return self.cleanup_interval_hours * 3600
    
    def is_service_configured(self, service: str) -> bool:
        """Check if a specific service is configured."""
        if service == "document_intelligence":
            return bool(self.doc_intelligence_endpoint and self.doc_intelligence_key)
        elif service == "translator":
            return bool(self.translator_endpoint and self.translator_key)
        elif service == "speech":
            return bool(self.speech_endpoint and self.speech_key)
        elif service == "storage":
            return bool(self.storage_connection_string)
        return False
    
    def get_configured_services(self) -> Dict[str, bool]:
        """Get dictionary of configured services."""
        return {
            "document_intelligence": self.is_service_configured("document_intelligence"),
            "translator": self.is_service_configured("translator"),
            "speech": self.is_service_configured("speech"),
            "storage": self.is_service_configured("storage")
        }


# Use the minimal config as the main config
AzureServiceConfig = MinimalAzureConfig


def load_config() -> AzureServiceConfig:
    """Load and validate configuration from environment."""
    try:
        # Try to load from .env file first
        if os.path.exists(".env"):
            logger.info("Loading configuration from .env file")
        else:
            # Try parent directory
            parent_env = os.path.join(os.path.dirname(__file__), "..", ".env")
            if os.path.exists(parent_env):
                logger.info(f"Loading configuration from {parent_env}")
                os.environ['ENV_FILE'] = parent_env
        
        config = AzureServiceConfig()
        
        # Log which services are configured
        configured_services = config.get_configured_services()
        logger.info("Configuration loaded successfully")
        logger.info(f"Configured services: {configured_services}")
        
        # Check if speech service is configured
        if config.speech_key and config.speech_endpoint:
            logger.info("Speech service appears to be configured")
        
        # Only require Document Intelligence
        if not config.is_service_configured("document_intelligence"):
            raise ValueError("Document Intelligence must be configured")
        
        # Warn about other services
        for service, is_configured in configured_services.items():
            if service != "document_intelligence" and not is_configured:
                logger.info(f"{service} is not configured - this service will be unavailable")
        
        return config
        
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        print("\n" + "="*60)
        print("CONFIGURATION ERROR")
        print("="*60)
        print(f"\nError: {e}")
        print("\nMake sure your .env file contains:")
        print("- AZURE_DOC_INTELLIGENCE_ENDPOINT")
        print("- AZURE_DOC_INTELLIGENCE_KEY")
        print("\nCurrent working directory:", os.getcwd())
        print("Looking for .env in:", os.path.abspath(".env"))
        print("="*60 + "\n")
        raise


def validate_azure_connection(config: AzureServiceConfig) -> Dict[str, bool]:
    """Validate Azure service connections."""
    results = {}
    
    # Only test Document Intelligence (required)
    try:
        from azure.ai.documentintelligence import DocumentIntelligenceClient
        client = DocumentIntelligenceClient(
            endpoint=config.doc_intelligence_endpoint,
            credential=config.get_doc_intelligence_credential()
        )
        results["document_intelligence"] = True
        logger.info("Document Intelligence connection validated")
    except Exception as e:
        logger.error(f"Document Intelligence connection failed: {e}")
        results["document_intelligence"] = False
    
    # Skip other services if not configured
    results["translator"] = config.is_service_configured("translator")
    results["speech_service"] = config.is_service_configured("speech")
    results["storage"] = config.is_service_configured("storage")
    
    return results


# Global configuration instance
_config: Optional[AzureServiceConfig] = None


def get_config() -> AzureServiceConfig:
    """Get global configuration instance."""
    global _config
    if _config is None:
        _config = load_config()
    return _config


def reload_config():
    """Reload configuration from environment."""
    global _config
    _config = load_config()