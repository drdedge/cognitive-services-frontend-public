#backend/utils/job_manager.py
"""
Job management system for tracking processing tasks
===================================================

Provides in-memory job storage with queue management for coordinating asynchronous
processing of cognitive services requests across multiple service types:

## Key Features:
- Multi-service job queuing with priority support
- Real-time job status tracking and progress updates
- Automatic retry logic with configurable policies
- Job expiration and lifecycle management
- Metrics collection for performance monitoring

The job manager handles concurrent job execution with configurable limits per
service type, maintains job history, and provides event handlers for status
changes and job completion notifications.

## Performance Optimizations:
- Async-safe locking for thread-safe operations
- Efficient queue processing with deque structures
- Background cleanup tasks for expired jobs
- In-memory storage with optional persistence hooks
- Minimal overhead for high-throughput scenarios
"""
import asyncio
import time
from typing import Dict, List, Optional, Any, Set, Callable
from datetime import datetime, timedelta
from collections import defaultdict, deque
from dataclasses import dataclass, field
import json
import threading

from models.base import JobStatus, ServiceType, ErrorDetails, ProcessingProgress
from models.job_models import Job, JobQueue, JobMetrics, RetryPolicy, JobConfiguration
from utils.logging import get_logger, log_job_event
from utils.exceptions import JobNotFoundException, JobTimeoutException, JobException


logger = get_logger(__name__)


@dataclass
class JobExecution:
    """Represents a job execution context."""
    job: Job
    started_at: datetime
    task: Optional[asyncio.Task] = None
    timeout_task: Optional[asyncio.Task] = None
    
    @property
    def duration_seconds(self) -> float:
        """Get execution duration in seconds."""
        return (datetime.utcnow() - self.started_at).total_seconds()
    
    @property
    def is_timeout(self) -> bool:
        """Check if execution has timed out."""
        if self.job.expires_at:
            return datetime.utcnow() > self.job.expires_at
        return False


class JobManager:
    """Manages job lifecycle, queuing, and execution."""
    
    def __init__(self, max_concurrent_jobs: int = 10):
        self.max_concurrent_jobs = max_concurrent_jobs
        
        # Job storage
        self.jobs: Dict[str, Job] = {}
        self.job_executions: Dict[str, JobExecution] = {}
        
        # Queue management
        self.queues: Dict[ServiceType, JobQueue] = {}
        self.pending_jobs: Dict[ServiceType, deque] = defaultdict(deque)
        self.processing_jobs: Set[str] = set()
        
        # Event handlers
        self.status_change_handlers: List[Callable[[Job], None]] = []
        self.completion_handlers: List[Callable[[Job], None]] = []
        
        # Background tasks
        self.cleanup_task: Optional[asyncio.Task] = None
        self.queue_processor_task: Optional[asyncio.Task] = None
        
        # Metrics
        self.metrics: Dict[ServiceType, JobMetrics] = {}
        
        # Thread safety
        self._lock = asyncio.Lock()
        
        # Initialize queues
        for service_type in ServiceType:
            self.queues[service_type] = JobQueue(
                queue_name=service_type.value,
                service_type=service_type,
                max_concurrent=max_concurrent_jobs // len(ServiceType)
            )
    
    async def start(self) -> None:
        """Start background job management tasks."""
        logger.info("Starting job manager")
        
        # Start cleanup task
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        # Start queue processor
        self.queue_processor_task = asyncio.create_task(self._queue_processor_loop())
        
        logger.info("Job manager started successfully")
    
    async def stop(self) -> None:
        """Stop job manager and cancel all running jobs."""
        logger.info("Stopping job manager")
        
        # Cancel background tasks
        if self.cleanup_task:
            self.cleanup_task.cancel()
        if self.queue_processor_task:
            self.queue_processor_task.cancel()
        
        # Cancel all running jobs
        async with self._lock:
            for job_id, execution in self.job_executions.items():
                if execution.task and not execution.task.done():
                    execution.task.cancel()
                    await self._update_job_status(job_id, JobStatus.CANCELLED)
        
        logger.info("Job manager stopped")
    
    async def create_job(
        self,
        service_type: ServiceType,
        parameters: Dict[str, Any],
        user_id: Optional[str] = None,
        priority: str = "normal",
        callback_url: Optional[str] = None,
        job_config: Optional[JobConfiguration] = None
    ) -> Job:
        """
        Create a new job.
        
        Args:
            service_type: Type of service to use
            parameters: Service-specific parameters
            user_id: User ID creating the job
            priority: Job priority
            callback_url: Optional callback URL
            job_config: Job configuration
            
        Returns:
            Created job instance
        """
        from models.base import generate_job_id
        
        job_id = generate_job_id(service_type)
        
        # Set expiration based on configuration
        if job_config:
            expires_at = datetime.utcnow() + timedelta(minutes=job_config.timeout_minutes)
        else:
            expires_at = datetime.utcnow() + timedelta(hours=24)  # Default 24 hours
        
        job = Job(
            job_id=job_id,
            service_type=service_type,
            user_id=user_id,
            priority=priority,
            parameters=parameters,
            callback_url=callback_url,
            expires_at=expires_at
        )
        
        async with self._lock:
            self.jobs[job_id] = job
            
            # Add to appropriate queue
            self.pending_jobs[service_type].append(job_id)
            self.queues[service_type].pending_jobs += 1
        
        log_job_event(
            logger,
            job_id,
            "created",
            status=job.status.value,
            message=f"Job created for {service_type.value}"
        )
        
        await self._notify_status_change(job)
        
        logger.info(f"Created job {job_id} for {service_type.value}")
        return job
    
    async def get_job(self, job_id: str) -> Job:
        """
        Get job by ID.
        
        Args:
            job_id: Job ID
            
        Returns:
            Job instance
            
        Raises:
            JobNotFoundException: If job doesn't exist
        """
        if job_id not in self.jobs:
            raise JobNotFoundException(job_id)
        
        return self.jobs[job_id]
    
    async def update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        progress: Optional[ProcessingProgress] = None,
        error: Optional[ErrorDetails] = None
    ) -> Job:
        """
        Update job status.
        
        Args:
            job_id: Job ID
            status: New status
            progress: Progress information
            error: Error details
            
        Returns:
            Updated job
        """
        async with self._lock:
            return await self._update_job_status(job_id, status, progress, error)
    
    async def _update_job_status(
        self,
        job_id: str,
        status: JobStatus,
        progress: Optional[ProcessingProgress] = None,
        error: Optional[ErrorDetails] = None
    ) -> Job:
        """Internal method to update job status (assumes lock is held)."""
        if job_id not in self.jobs:
            raise JobNotFoundException(job_id)
        
        job = self.jobs[job_id]
        old_status = job.status
        
        # Update job fields
        job.status = status
        job.updated_at = datetime.utcnow()
        
        if progress:
            job.progress = progress
        
        if error:
            job.error = error
        
        # Set timestamps based on status
        if status == JobStatus.PROCESSING and job.started_at is None:
            job.started_at = datetime.utcnow()
        elif status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            job.completed_at = datetime.utcnow()
            
            # Remove from processing set
            self.processing_jobs.discard(job_id)
            if job.service_type in self.queues:
                self.queues[job.service_type].processing_jobs = max(
                    0, self.queues[job.service_type].processing_jobs - 1
                )
        
        # Log status change
        log_job_event(
            logger,
            job_id,
            "status_changed",
            status=status.value,
            message=f"Status changed from {old_status.value} to {status.value}"
        )
        
        # Notify handlers
        await self._notify_status_change(job)
        
        if status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
            await self._notify_completion(job)
        
        return job
    
    async def cancel_job(self, job_id: str, reason: str = "User requested") -> Job:
        """
        Cancel a job.
        
        Args:
            job_id: Job ID
            reason: Cancellation reason
            
        Returns:
            Cancelled job
        """
        async with self._lock:
            job = await self.get_job(job_id)
            
            if job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                raise JobException(
                    message=f"Cannot cancel job in {job.status.value} status",
                    job_id=job_id
                )
            
            # Cancel running task if exists
            if job_id in self.job_executions:
                execution = self.job_executions[job_id]
                if execution.task and not execution.task.done():
                    execution.task.cancel()
            
            # Update status
            error = ErrorDetails(
                error_code="JOB_CANCELLED",
                error_message=f"Job cancelled: {reason}"
            )
            
            return await self._update_job_status(job_id, JobStatus.CANCELLED, error=error)
    
    async def retry_job(self, job_id: str) -> Job:
        """
        Retry a failed job.
        
        Args:
            job_id: Job ID
            
        Returns:
            Updated job
        """
        async with self._lock:
            job = await self.get_job(job_id)
            
            if not job.can_retry:
                raise JobException(
                    message="Job cannot be retried",
                    job_id=job_id,
                    details={
                        "status": job.status.value,
                        "retry_count": job.retry_count,
                        "max_retries": job.max_retries,
                        "is_expired": job.is_expired
                    }
                )
            
            # Increment retry count
            job.retry_count += 1
            job.error = None
            job.completed_at = None
            
            # Reset to pending and add back to queue
            job = await self._update_job_status(job_id, JobStatus.PENDING)
            self.pending_jobs[job.service_type].append(job_id)
            self.queues[job.service_type].pending_jobs += 1
            
            logger.info(f"Job {job_id} queued for retry (attempt {job.retry_count})")
            return job
    
    async def get_jobs_by_status(self, status: JobStatus) -> List[Job]:
        """Get all jobs with specified status."""
        return [job for job in self.jobs.values() if job.status == status]
    
    async def get_jobs_by_service(self, service_type: ServiceType) -> List[Job]:
        """Get all jobs for specified service type."""
        return [job for job in self.jobs.values() if job.service_type == service_type]
    
    async def get_user_jobs(self, user_id: str) -> List[Job]:
        """Get all jobs for specified user."""
        return [job for job in self.jobs.values() if job.user_id == user_id]
    
    async def get_queue_stats(self) -> Dict[ServiceType, JobQueue]:
        """Get queue statistics for all service types."""
        # Update current stats
        for service_type, queue in self.queues.items():
            queue.pending_jobs = len(self.pending_jobs[service_type])
            queue.processing_jobs = len([
                j for j in self.jobs.values()
                if j.service_type == service_type and j.status == JobStatus.PROCESSING
            ])
        
        return self.queues.copy()
    
    async def get_job_metrics(
        self,
        service_type: Optional[ServiceType] = None,
        period_hours: int = 24
    ) -> Dict[ServiceType, JobMetrics]:
        """
        Get job metrics for specified period.
        
        Args:
            service_type: Service type (all services if None)
            period_hours: Period in hours to calculate metrics
            
        Returns:
            Dictionary of metrics by service type
        """
        period_start = datetime.utcnow() - timedelta(hours=period_hours)
        period_end = datetime.utcnow()
        
        service_types = [service_type] if service_type else list(ServiceType)
        metrics = {}
        
        for svc_type in service_types:
            # Filter jobs for this service and period
            period_jobs = [
                job for job in self.jobs.values()
                if (job.service_type == svc_type and
                    job.created_at >= period_start and
                    job.created_at <= period_end)
            ]
            
            total_jobs = len(period_jobs)
            completed_jobs = len([j for j in period_jobs if j.status == JobStatus.COMPLETED])
            failed_jobs = len([j for j in period_jobs if j.status == JobStatus.FAILED])
            
            # Calculate average processing time
            avg_processing_time = None
            processing_times = [
                j.duration_seconds for j in period_jobs
                if j.duration_seconds is not None
            ]
            if processing_times:
                avg_processing_time = sum(processing_times) / len(processing_times)
            
            # Calculate total cost
            total_cost = sum(
                j.actual_cost for j in period_jobs
                if j.actual_cost is not None
            )
            
            metrics[svc_type] = JobMetrics(
                service_type=svc_type,
                period_start=period_start,
                period_end=period_end,
                total_jobs=total_jobs,
                completed_jobs=completed_jobs,
                failed_jobs=failed_jobs,
                average_processing_time=avg_processing_time,
                total_cost=total_cost if total_cost > 0 else None
            )
        
        return metrics
    
    def add_status_change_handler(self, handler: Callable[[Job], None]) -> None:
        """Add a handler for job status changes."""
        self.status_change_handlers.append(handler)
    
    def add_completion_handler(self, handler: Callable[[Job], None]) -> None:
        """Add a handler for job completion."""
        self.completion_handlers.append(handler)
    
    async def _notify_status_change(self, job: Job) -> None:
        """Notify all status change handlers."""
        for handler in self.status_change_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(job)
                else:
                    handler(job)
            except Exception as e:
                logger.error(f"Error in status change handler: {e}")
    
    async def _notify_completion(self, job: Job) -> None:
        """Notify all completion handlers."""
        for handler in self.completion_handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(job)
                else:
                    handler(job)
            except Exception as e:
                logger.error(f"Error in completion handler: {e}")
    
    async def _queue_processor_loop(self) -> None:
        """Background loop to process job queues."""
        while True:
            try:
                await self._process_queues()
                await asyncio.sleep(1)  # Check every second
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in queue processor: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _process_queues(self) -> None:
        """Process pending jobs in all queues."""
        for service_type in ServiceType:
            queue = self.queues[service_type]
            
            # Check if we can process more jobs for this service
            if (queue.processing_jobs < queue.max_concurrent and
                len(self.pending_jobs[service_type]) > 0):
                
                # Get next job from queue
                job_id = self.pending_jobs[service_type].popleft()
                queue.pending_jobs = max(0, queue.pending_jobs - 1)
                
                # Start processing
                await self._start_job_processing(job_id)
    
    async def _start_job_processing(self, job_id: str) -> None:
        """Start processing a job."""
        async with self._lock:
            if job_id not in self.jobs:
                logger.warning(f"Job {job_id} not found when starting processing")
                return
            
            job = self.jobs[job_id]
            
            # Check if job has expired
            if job.is_expired:
                await self._update_job_status(
                    job_id,
                    JobStatus.FAILED,
                    error=ErrorDetails(
                        error_code="JOB_EXPIRED",
                        error_message="Job expired before processing could start"
                    )
                )
                return
            
            # Update status to processing
            await self._update_job_status(job_id, JobStatus.PROCESSING)
            
            # Add to processing set
            self.processing_jobs.add(job_id)
            self.queues[job.service_type].processing_jobs += 1
            
            # Create execution context
            execution = JobExecution(
                job=job,
                started_at=datetime.utcnow()
            )
            
            # Note: Actual job execution would be handled by service-specific handlers
            # This is just the infrastructure for tracking job lifecycle
            self.job_executions[job_id] = execution
            
            logger.info(f"Started processing job {job_id}")
    
    async def _cleanup_loop(self) -> None:
        """Background loop to clean up expired and completed jobs."""
        while True:
            try:
                await self._cleanup_jobs()
                await asyncio.sleep(3600)  # Clean up every hour
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
    
    async def _cleanup_jobs(self) -> None:
        """Clean up expired and old completed jobs."""
        now = datetime.utcnow()
        cleanup_before = now - timedelta(hours=24)  # Keep jobs for 24 hours
        
        jobs_to_cleanup = []
        
        async with self._lock:
            for job_id, job in self.jobs.items():
                # Clean up completed jobs older than 24 hours
                if (job.status in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED] and
                    job.completed_at and job.completed_at < cleanup_before):
                    jobs_to_cleanup.append(job_id)
                
                # Clean up expired jobs
                elif job.is_expired and job.status not in [JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED]:
                    await self._update_job_status(
                        job_id,
                        JobStatus.FAILED,
                        error=ErrorDetails(
                            error_code="JOB_EXPIRED",
                            error_message="Job expired"
                        )
                    )
                    jobs_to_cleanup.append(job_id)
            
            # Remove cleaned up jobs
            for job_id in jobs_to_cleanup:
                del self.jobs[job_id]
                self.job_executions.pop(job_id, None)
        
        if jobs_to_cleanup:
            logger.info(f"Cleaned up {len(jobs_to_cleanup)} jobs")

    async def complete_job(
        self,
        job_id: str,
        results_path: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        final_cost: Optional[float] = None
    ) -> Job:
        """
        Complete a job with results.
        
        Args:
            job_id: Job ID
            results_path: Path to results file in storage
            metadata: Service-specific metadata
            final_cost: Final processing cost
            
        Returns:
            Updated job
        """
        async with self._lock:
            if job_id not in self.jobs:
                raise JobNotFoundException(job_id)
            
            job = self.jobs[job_id]
            
            # Update job fields
            job.status = JobStatus.COMPLETED
            job.completed_at = datetime.utcnow()
            job.updated_at = datetime.utcnow()
            
            if results_path:
                job.results_path = results_path
            
            if metadata:
                job.metadata = metadata
            
            if final_cost is not None:
                job.actual_cost = final_cost
            
            # Remove from processing set
            self.processing_jobs.discard(job_id)
            if job.service_type in self.queues:
                self.queues[job.service_type].processing_jobs = max(
                    0, self.queues[job.service_type].processing_jobs - 1
                )
            
            # Log completion
            log_job_event(
                logger,
                job_id,
                "completed",
                status=job.status.value,
                message=f"Job completed successfully"
            )
            
            # Notify handlers
            await self._notify_status_change(job)
            await self._notify_completion(job)
            
            return job


    async def fail_job(
        self,
        job_id: str,
        error_message: str,
        error_code: str = "JOB_FAILED",
        error_details: Optional[Dict[str, Any]] = None
    ) -> Job:
        """
        Mark job as failed with error details.
        
        Args:
            job_id: Job ID
            error_message: Error message
            error_code: Error code
            error_details: Additional error details
            
        Returns:
            Updated job
        """
        error = ErrorDetails(
            error_code=error_code,
            error_message=error_message,
            details=error_details or {},
            severity="medium"
        )
        
        return await self.update_job_status(
            job_id,
            JobStatus.FAILED,
            error=error
        )


    async def update_job_results(
        self,
        job_id: str,
        results_path: str,
        metadata: Dict[str, Any]
    ) -> Job:
        """
        Update job with results information.
        
        Args:
            job_id: Job ID
            results_path: Path to results file
            metadata: Service-specific metadata
            
        Returns:
            Updated job
        """
        async with self._lock:
            if job_id not in self.jobs:
                raise JobNotFoundException(job_id)
            
            job = self.jobs[job_id]
            job.results_path = results_path
            job.metadata = metadata
            job.updated_at = datetime.utcnow()
            
            logger.info(f"Updated job {job_id} with results at {results_path}")
            
            return job


    async def update_job_progress(
        self,
        job_id: str,
        progress_percentage: int,
        message: str,
        current_step: Optional[str] = None
    ) -> Job:
        """
        Update job progress.
        
        Args:
            job_id: Job ID
            progress_percentage: Progress percentage (0-100)
            message: Progress message
            current_step: Current processing step
            
        Returns:
            Updated job
        """
        progress = ProcessingProgress(
            current_step=current_step or message,
            progress_percentage=progress_percentage,
            message=message
        )
        
        return await self.update_job_status(
            job_id,
            JobStatus.PROCESSING,
            progress=progress
        )
# Global job manager instance
_job_manager: Optional[JobManager] = None


def get_job_manager() -> JobManager:
    """Get global job manager instance."""
    global _job_manager
    if _job_manager is None:
        _job_manager = JobManager()
    return _job_manager


def reset_job_manager():
    """Reset global job manager (useful for testing)."""
    global _job_manager
    if _job_manager:
        asyncio.create_task(_job_manager.stop())
    _job_manager = None