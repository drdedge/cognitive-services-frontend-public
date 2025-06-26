# backend/services/websocket/manager.py
"""
WebSocket manager for real-time communication.
Handles job-specific WebSocket connections and message broadcasting.
"""
import asyncio
import json
import logging
from typing import Dict, Set, Optional, Any, List
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager

from models.base import (
    WebSocketMessage, JobUpdateMessage, ErrorMessage, CompletionMessage,
    JobStatus, ErrorDetails, ProcessingProgress
)
from utils.logging import get_logger, set_correlation_id


logger = get_logger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for job updates."""
    
    def __init__(self):
        # Map job_id to set of WebSocket connections
        self.job_connections: Dict[str, Set[WebSocket]] = {}
        # Map WebSocket to job_id for cleanup
        self.connection_jobs: Dict[WebSocket, str] = {}
        # Global connections (not job-specific)
        self.global_connections: Set[WebSocket] = set()
        # Connection metadata
        self.connection_metadata: Dict[WebSocket, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket, job_id: Optional[str] = None) -> None:
        """
        Connect a WebSocket for job updates.
        
        Args:
            websocket: WebSocket connection
            job_id: Job ID to subscribe to updates (None for global updates)
        """
        await websocket.accept()
        
        async with self._lock:
            if job_id:
                # Job-specific connection
                if job_id not in self.job_connections:
                    self.job_connections[job_id] = set()
                
                self.job_connections[job_id].add(websocket)
                self.connection_jobs[websocket] = job_id
                
                logger.info(f"WebSocket connected for job {job_id}")
            else:
                # Global connection
                self.global_connections.add(websocket)
                logger.info("Global WebSocket connected")
            
            # Store connection metadata
            self.connection_metadata[websocket] = {
                "connected_at": datetime.utcnow(),
                "job_id": job_id,
                "message_count": 0
            }
    
    async def disconnect(self, websocket: WebSocket) -> None:
        """
        Disconnect a WebSocket.
        
        Args:
            websocket: WebSocket connection to disconnect
        """
        async with self._lock:
            # Remove from job-specific connections
            if websocket in self.connection_jobs:
                job_id = self.connection_jobs[websocket]
                if job_id in self.job_connections:
                    self.job_connections[job_id].discard(websocket)
                    
                    # Clean up empty job connection sets
                    if not self.job_connections[job_id]:
                        del self.job_connections[job_id]
                
                del self.connection_jobs[websocket]
                logger.info(f"WebSocket disconnected from job {job_id}")
            
            # Remove from global connections
            self.global_connections.discard(websocket)
            
            # Clean up metadata
            if websocket in self.connection_metadata:
                metadata = self.connection_metadata[websocket]
                duration = (datetime.utcnow() - metadata["connected_at"]).total_seconds()
                logger.info(
                    f"WebSocket connection closed after {duration:.1f}s, "
                    f"sent {metadata['message_count']} messages"
                )
                del self.connection_metadata[websocket]
    
    async def send_to_job(self, job_id: str, message: WebSocketMessage) -> int:
        """
        Send message to all connections subscribed to a job.
        
        Args:
            job_id: Job ID
            message: Message to send
            
        Returns:
            Number of connections message was sent to
        """
        if job_id not in self.job_connections:
            # No connections for job
            return 0
        
        message_data = json.loads(message.json())
        connections_to_remove = set()
        sent_count = 0
        
        for websocket in self.job_connections[job_id].copy():
            try:
                await websocket.send_json(message_data)
                
                # Update message count
                if websocket in self.connection_metadata:
                    self.connection_metadata[websocket]["message_count"] += 1
                
                sent_count += 1
                # Message sent to job connection
                
            except Exception as e:
                logger.warning(f"Failed to send message to job {job_id} connection: {e}")
                connections_to_remove.add(websocket)
        
        # Clean up failed connections
        if connections_to_remove:
            async with self._lock:
                for websocket in connections_to_remove:
                    await self.disconnect(websocket)
        
        logger.info(f"Sent job update to {sent_count} connections for job {job_id}")
        return sent_count
    
    async def send_to_all(self, message: WebSocketMessage) -> int:
        """
        Send message to all global connections.
        
        Args:
            message: Message to send
            
        Returns:
            Number of connections message was sent to
        """
        if not self.global_connections:
            return 0
        
        message_data = json.loads(message.json())
        connections_to_remove = set()
        sent_count = 0
        
        for websocket in self.global_connections.copy():
            try:
                await websocket.send_json(message_data)
                
                # Update message count
                if websocket in self.connection_metadata:
                    self.connection_metadata[websocket]["message_count"] += 1
                
                sent_count += 1
                
            except Exception as e:
                logger.warning(f"Failed to send global message: {e}")
                connections_to_remove.add(websocket)
        
        # Clean up failed connections
        if connections_to_remove:
            async with self._lock:
                for websocket in connections_to_remove:
                    await self.disconnect(websocket)
        
        logger.info(f"Sent global message to {sent_count} connections")
        return sent_count
    
    async def broadcast_job_update(
        self,
        job_id: str,
        status: JobStatus,
        progress: Optional[ProcessingProgress] = None,
        error: Optional[ErrorDetails] = None
    ) -> int:
        """
        Broadcast job status update.
        
        Args:
            job_id: Job ID
            status: New job status
            progress: Progress information
            error: Error details if applicable
            
        Returns:
            Number of connections notified
        """
        message = JobUpdateMessage(
            job_id=job_id,
            status=status,
            progress=progress,
            error=error
        )
        
        return await self.send_to_job(job_id, message)
    
    async def broadcast_job_completion(
        self,
        job_id: str,
        results_url: Optional[str] = None,
        final_cost: Optional[float] = None,
        processing_time_seconds: Optional[float] = None,
        data: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Broadcast job completion.
        
        Args:
            job_id: Job ID
            results_url: URL to download results
            final_cost: Final processing cost
            processing_time_seconds: Total processing time
            data: Additional data to include in message
            
        Returns:
            Number of connections notified
        """
        message = CompletionMessage(
            job_id=job_id,
            results_url=results_url,
            final_cost=final_cost,
            processing_time_seconds=processing_time_seconds,
            data=data or {}
        )
        
        return await self.send_to_job(job_id, message)
    
    async def broadcast_error(
        self,
        error: ErrorDetails,
        job_id: Optional[str] = None
    ) -> int:
        """
        Broadcast error message.
        
        Args:
            error: Error details
            job_id: Job ID if error is job-specific
            
        Returns:
            Number of connections notified
        """
        message = ErrorMessage(
            job_id=job_id,
            error=error
        )
        
        if job_id:
            return await self.send_to_job(job_id, message)
        else:
            return await self.send_to_all(message)
    
    def get_connection_count(self, job_id: Optional[str] = None) -> int:
        """
        Get number of active connections.
        
        Args:
            job_id: Job ID to check (None for all connections)
            
        Returns:
            Number of active connections
        """
        if job_id:
            return len(self.job_connections.get(job_id, set()))
        else:
            total = len(self.global_connections)
            for connections in self.job_connections.values():
                total += len(connections)
            return total
    
    def get_active_jobs(self) -> List[str]:
        """Get list of job IDs with active connections."""
        return list(self.job_connections.keys())
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get connection statistics."""
        return {
            "total_connections": self.get_connection_count(),
            "global_connections": len(self.global_connections),
            "job_connections": {
                job_id: len(connections) 
                for job_id, connections in self.job_connections.items()
            },
            "active_jobs": len(self.job_connections)
        }


# Global connection manager instance
connection_manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket, job_id: Optional[str] = None):
    """
    WebSocket endpoint for job updates.
    
    Args:
        websocket: WebSocket connection
        job_id: Optional job ID to subscribe to specific job updates
    """
    # Set correlation ID for logging
    correlation_id = set_correlation_id()
    
    try:
        await connection_manager.connect(websocket, job_id)
        
        logger.info(
            f"WebSocket connection established",
            extra={
                "job_id": job_id,
                "correlation_id": correlation_id
            }
        )
        
        # Send initial connection confirmation
        welcome_message = WebSocketMessage(
            type="connection_established",
            data={
                "job_id": job_id,
                "correlation_id": correlation_id,
                "server_time": datetime.utcnow().isoformat()
            }
        )
        await websocket.send_json(json.loads(welcome_message.json()))
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                # Wait for incoming messages (with timeout)
                data = await asyncio.wait_for(
                    websocket.receive_json(),
                    timeout=300.0  # 5 minute timeout
                )
                
                # Handle ping/pong for keep-alive
                if data.get("type") == "ping":
                    pong_message = WebSocketMessage(
                        type="pong",
                        data={"server_time": datetime.utcnow().isoformat()}
                    )
                    await websocket.send_json(json.loads(pong_message.json()))
                    
                elif data.get("type") == "subscribe":
                    # Handle subscription to different job
                    new_job_id = data.get("job_id")
                    if new_job_id and new_job_id != job_id:
                        await connection_manager.disconnect(websocket)
                        await connection_manager.connect(websocket, new_job_id)
                        job_id = new_job_id
                        logger.info(f"WebSocket resubscribed to job {job_id}")
                
            except asyncio.TimeoutError:
                # Send ping to check if connection is still alive
                try:
                    ping_message = WebSocketMessage(
                        type="ping",
                        data={"server_time": datetime.utcnow().isoformat()}
                    )
                    await websocket.send_json(json.loads(ping_message.json()))
                except:
                    # Connection is dead
                    break
            
            except WebSocketDisconnect:
                break
            
            except Exception as e:
                logger.warning(f"Error handling WebSocket message: {e}")
                break
    
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected by client")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    
    finally:
        await connection_manager.disconnect(websocket)
        logger.info("WebSocket connection closed")


@asynccontextmanager
async def websocket_context(job_id: str):
    """
    Context manager for WebSocket operations during job processing.
    
    Args:
        job_id: Job ID
        
    Usage:
        async with websocket_context(job_id) as ws_manager:
            await ws_manager.send_progress(50, "Processing...")
    """
    class WebSocketJobManager:
        def __init__(self, job_id: str):
            self.job_id = job_id
        
        async def send_progress(self, percentage: int, message: str = None):
            """Send progress update."""
            progress = ProcessingProgress(
                current_step=message or f"Processing... {percentage}%",
                progress_percentage=percentage,
                message=message
            )
            await connection_manager.broadcast_job_update(
                self.job_id,
                JobStatus.PROCESSING,
                progress=progress
            )
        
        async def send_error(self, error_code: str, error_message: str, details: Dict[str, Any] = None):
            """Send error update."""
            error = ErrorDetails(
                error_code=error_code,
                error_message=error_message,
                details=details or {}
            )
            await connection_manager.broadcast_job_update(
                self.job_id,
                JobStatus.FAILED,
                error=error
            )
        
        async def send_completion(
            self,
            results_url: str = None,
            final_cost: float = None,
            processing_time: float = None
        ):
            """Send completion notification."""
            await connection_manager.broadcast_job_completion(
                self.job_id,
                results_url=results_url,
                final_cost=final_cost,
                processing_time_seconds=processing_time
            )
    
    manager = WebSocketJobManager(job_id)
    try:
        yield manager
    except Exception as e:
        # Send error notification if job fails
        await manager.send_error(
            error_code="JOB_PROCESSING_ERROR",
            error_message=str(e)
        )
        raise


# Convenience functions for document intelligence service
async def send_progress_update(job_id: str, percentage: int, message: str):
    """Send progress update for document intelligence processing."""
    progress = ProcessingProgress(
        current_step=message,
        progress_percentage=percentage,
        message=message
    )
    await connection_manager.broadcast_job_update(
        job_id,
        JobStatus.PROCESSING,
        progress=progress
    )


async def send_completion_notification(job_id: str, results_data: Dict[str, Any]):
    """Send completion notification with results data."""
    message = CompletionMessage(
        job_id=job_id,
        results_url=results_data.get("download_url"),
        data=results_data
    )
    await connection_manager.send_to_job(job_id, message)


async def send_error_notification(job_id: str, error_message: str):
    """Send error notification."""
    error = ErrorDetails(
        error_code="PROCESSING_ERROR",
        error_message=error_message
    )
    await connection_manager.broadcast_error(error, job_id)


def get_websocket_manager():
    """Get the global websocket manager instance."""
    return connection_manager


# Legacy support for existing code
manager = connection_manager