#backend/main.py
"""
Azure Cognitive Services API backend with FastAPI
==================================================

Provides a unified API for Azure Cognitive Services integration, handling document
intelligence, translation, and transcription services with real-time job tracking:

## Key Features:
- Multi-service API endpoints for cognitive processing
- Asynchronous job queue with WebSocket status updates  
- Modular service architecture with dynamic loading
- Comprehensive health monitoring and statistics
- Secure file handling with Azure Blob Storage

The backend uses FastAPI for high-performance async operations and includes
middleware for CORS, logging, and error handling. Services are loaded based on
available Azure credentials to support flexible deployment configurations.

## Performance Optimizations:
- Connection pooling for Azure SDK clients
- Background task processing for long operations
- Request/response logging with correlation IDs
- Automatic temporary file cleanup
- Graceful service degradation on failures
"""
import json
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Import configuration and check which services are available
from utils.config import get_config
from models.base import APIResponse, HealthStatus, create_error_response, create_success_response
from utils.logging import (
    setup_logging, get_logger, set_correlation_id, get_correlation_id,
    log_api_request, log_api_response
)

# Setup logging
setup_logging(level=os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)

# Check which services are configured before importing
config = get_config()
configured_services = config.get_configured_services()
logger.debug(f"Configured services: {configured_services}")

# Import only configured services
if configured_services.get("document_intelligence", False):
    from api import document_intelligence
    logger.debug("Document Intelligence API loaded")
else:
    document_intelligence = None
    logger.debug("Document Intelligence API not loaded - service not configured")

# Force load translation service for testing
# if configured_services.get("translator", False):
from api import translation
logger.debug("Translation API loaded (forced)")
# else:
#     translation = None
#     logger.warning("Translation API not loaded - service not configured")

# Force load transcription service for testing
# if configured_services.get("speech", False):
from api import transcription
logger.debug("Transcription API loaded (forced)")
# else:
#     transcription = None
#     logger.warning("Transcription API not loaded - service not configured")

# Storage is always imported as it might work with local files
from api import storage
from services.websocket import websocket_endpoint
from utils.azure_clients import get_client_manager
from utils.job_manager import get_job_manager
from utils.file_handler import get_file_handler
from utils.exceptions import ServiceException, to_http_exception, handle_azure_exception

# Application startup time
app_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown events."""
    logger.info("Starting Azure Cognitive Services API...")
    
    try:
        # Test Azure connections
        from utils.config import validate_azure_connection
        connection_status = validate_azure_connection(config)
        failed_services = [svc for svc, status in connection_status.items() if not status]
        
        if failed_services:
            logger.warning(f"Some Azure services are unavailable: {failed_services}")
        else:
            logger.info("All configured Azure services connected successfully")
        
        # Initialize Azure clients
        client_manager = get_client_manager()
        client_status = client_manager.test_all_connections()
        logger.debug(f"Azure clients initialized: {client_status}")
        
        # Start job manager
        job_manager = get_job_manager()
        await job_manager.start()
        logger.info("Job manager started")
        
        # Initialize file handler
        file_handler = get_file_handler()
        logger.info("File handler initialized")
        
        # Store startup info in app state
        app.state.startup_time = datetime.utcnow()
        app.state.azure_status = connection_status
        app.state.configured_services = configured_services
        
        logger.info("Azure Cognitive Services API started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown tasks
    logger.info("Shutting down Azure Cognitive Services API...")
    
    try:
        # Stop job manager
        job_manager = get_job_manager()
        await job_manager.stop()
        logger.info("Job manager stopped")
        
        # Cleanup temp files
        file_handler = get_file_handler()
        cleanup_count = await file_handler.cleanup_temp_files()
        logger.debug(f"Cleaned up {cleanup_count} temporary files")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
    
    logger.info("Azure Cognitive Services API shut down successfully")


# Create FastAPI app
app = FastAPI(
    title="Azure Cognitive Services API",
    description="Unified API for Document Intelligence, Translation, and Transcription services",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins if hasattr(config, 'cors_origins') else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Debug mode flag - set to True for verbose request/response logging
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

# Request logging middleware
@app.middleware("http")
async def logging_middleware(request: Request, call_next):
    """Log API requests and responses."""
    # Set correlation ID
    correlation_id = request.headers.get("X-Correlation-ID") or set_correlation_id()
    
    # Log request (only in debug mode)
    start_time = time.time()
    if DEBUG_MODE:
        log_api_request(
            logger,
            request.method,
            str(request.url.path),
            dict(request.query_params),
            dict(request.headers),
            getattr(request.state, "body_size", None)
        )
    
    # Process request
    try:
        response = await call_next(request)
        
        # Log response (only in debug mode or for errors)
        duration_ms = (time.time() - start_time) * 1000
        if DEBUG_MODE or response.status_code >= 400:
            log_api_response(
                logger,
                response.status_code,
                duration_ms,
                response_size=getattr(response, "content_length", None)
            )
        
        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response
        
    except Exception as e:
        # Always log error responses
        duration_ms = (time.time() - start_time) * 1000
        log_api_response(
            logger,
            500,
            duration_ms,
            error_code="INTERNAL_ERROR"
        )
        raise

# Include API routers for configured services
if document_intelligence is not None:
    app.include_router(
        document_intelligence.router,
        prefix="/api/document-intelligence",
        tags=["Document Intelligence"]
    )

if translation is not None:
    app.include_router(
        translation.router,
        prefix="/api/translation",
        tags=["Translation"]
    )

if transcription is not None:
    app.include_router(
        transcription.router,
        prefix="/api/transcription",
        tags=["Transcription"]
    )

# Storage router is always included
app.include_router(
    storage.router,
    prefix="/api/storage",
    tags=["Storage"]
)


# WebSocket endpoints
@app.websocket("/ws/{job_id}")
async def websocket_job_endpoint(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for job-specific updates."""
    await websocket_endpoint(websocket, job_id)


@app.websocket("/ws")
async def websocket_global_endpoint(websocket: WebSocket):
    """WebSocket endpoint for global updates."""
    await websocket_endpoint(websocket)


# API endpoints
@app.get("/", response_model=APIResponse)
async def root():
    """Root endpoint with API information."""
    available_endpoints = {
        "storage": "/api/storage",
        "health": "/health",
        "docs": "/docs",
        "websocket": "/ws/{job_id}"
    }
    
    available_features = ["Secure file handling"]
    
    if document_intelligence is not None:
        available_endpoints["document_intelligence"] = "/api/document-intelligence"
        available_features.append("Document Intelligence with table extraction")
    
    if translation is not None:
        available_endpoints["translation"] = "/api/translation"
        available_features.append("Multi-language text translation")
    
    if transcription is not None:
        available_endpoints["transcription"] = "/api/transcription"
        available_features.append("Audio transcription with speaker diarization")
    
    available_features.extend([
        "Real-time job status updates via WebSocket",
        "Health monitoring and statistics"
    ])
    
    return create_success_response(
        data={
            "name": "Azure Cognitive Services API",
            "version": "1.0.0",
            "description": "Unified API for Document Intelligence, Translation, and Transcription",
            "configured_services": configured_services,
            "endpoints": available_endpoints,
            "features": available_features
        },
        correlation_id=get_correlation_id()
    )


@app.get("/health", response_model=HealthStatus)
async def health_check():
    """Comprehensive health check endpoint."""
    uptime_seconds = time.time() - app_start_time
    
    # Test Azure service connections
    try:
        client_manager = get_client_manager()
        service_status = client_manager.get_connection_status()
        
        # Overall health is good if at least one service is available
        overall_status = "healthy" if any(service_status.values()) else "degraded"
        
        return HealthStatus(
            status=overall_status,
            services=service_status,
            version="1.0.0",
            uptime_seconds=uptime_seconds
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return HealthStatus(
            status="unhealthy",
            services={},
            uptime_seconds=uptime_seconds
        )


@app.get("/stats", response_model=APIResponse)
async def get_stats():
    """Get API statistics and metrics."""
    try:
        # Job manager stats
        job_manager = get_job_manager()
        queue_stats = await job_manager.get_queue_stats()
        job_metrics = await job_manager.get_job_metrics()
        
        # WebSocket stats
        from services.websocket import connection_manager
        ws_stats = connection_manager.get_connection_stats()
        
        # Azure client stats
        client_manager = get_client_manager()
        azure_status = client_manager.get_connection_status()
        
        return create_success_response(
            data={
                "uptime_seconds": time.time() - app_start_time,
                "configured_services": configured_services,
                "job_queues": {
                    queue.service_type.value: {
                        "pending": queue.pending_jobs,
                        "processing": queue.processing_jobs,
                        "max_concurrent": queue.max_concurrent
                    }
                    for queue in queue_stats.values()
                },
                "job_metrics": {
                    metrics.service_type.value: {
                        "total_jobs": metrics.total_jobs,
                        "completed_jobs": metrics.completed_jobs,
                        "failed_jobs": metrics.failed_jobs,
                        "success_rate": metrics.success_rate,
                        "average_processing_time": metrics.average_processing_time
                    }
                    for metrics in job_metrics.values()
                },
                "websocket_connections": ws_stats,
                "azure_services": azure_status
            },
            correlation_id=get_correlation_id()
        )
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return create_error_response(
            error_code="STATS_ERROR",
            error_message="Failed to retrieve statistics",
            correlation_id=get_correlation_id()
        )


# Exception handlers
@app.exception_handler(ServiceException)
async def service_exception_handler(request: Request, exc: ServiceException):
    """Handle service exceptions."""
    correlation_id = get_correlation_id()
    logger.error(f"Service exception: {exc.message}", extra={
        "error_code": exc.error_code,
        "details": exc.details,
        "correlation_id": correlation_id
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(create_error_response(
            error_code=exc.error_code,
            error_message=exc.message,
            details=exc.details,
            correlation_id=correlation_id
        )),
        headers={"X-Correlation-ID": correlation_id or "unknown"}
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    correlation_id = get_correlation_id()
    
    return JSONResponse(
        status_code=exc.status_code,
        content=jsonable_encoder(create_error_response(
            error_code="HTTP_ERROR",
            error_message=str(exc.detail),
            correlation_id=correlation_id
        )),
        headers={"X-Correlation-ID": correlation_id or "unknown"}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    correlation_id = get_correlation_id()
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True, extra={
        "correlation_id": correlation_id
    })
    
    return JSONResponse(
        status_code=500,
        content=jsonable_encoder(create_error_response(
            error_code="INTERNAL_ERROR",
            error_message="An unexpected error occurred",
            correlation_id=correlation_id
        )),
        headers={"X-Correlation-ID": correlation_id or "unknown"}
    )


# Run the application
if __name__ == "__main__":
    import uvicorn
    
    # Run with uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=False,
        access_log=False  # We handle logging in middleware
    )