"""
GPU Scheduler - Optimize GPU allocation for ML workloads
"""

import asyncio
import heapq
import logging
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set

from .types import (
    GPUAllocation,
    GPUJob,
    GPUType,
)

logger = logging.getLogger(__name__)


class GPUScheduler:
    """
    Optimizes GPU allocation for ML workloads.
    
    Features:
    - Priority-based scheduling
    - Fair sharing across agents
    - Gang scheduling for multi-GPU jobs
    - Bin packing optimization
    """
    
    def __init__(
        self,
        gpu_inventory: Dict[GPUType, int],
        enable_preemption: bool = False,
    ):
        """
        Initialize GPU scheduler.
        
        Args:
            gpu_inventory: Available GPUs by type
            enable_preemption: Allow preemption of lower-priority jobs
        """
        self.gpu_inventory = gpu_inventory
        self.enable_preemption = enable_preemption
        
        # Track GPU state
        self._available_gpus: Dict[GPUType, Set[str]] = defaultdict(set)
        self._allocated_gpus: Dict[str, GPUAllocation] = {}
        
        # Initialize GPU IDs
        for gpu_type, count in gpu_inventory.items():
            for i in range(count):
                gpu_id = f"{gpu_type.value}_{i}"
                self._available_gpus[gpu_type].add(gpu_id)
        
        # Job queues (priority queue)
        self._pending_jobs: List[GPUJob] = []
        self._running_jobs: Dict[str, GPUJob] = {}
        self._completed_jobs: List[GPUJob] = []
        
        self._lock = asyncio.Lock()
        
        logger.info(
            f"Initialized GPUScheduler: {sum(gpu_inventory.values())} GPUs, "
            f"preemption={'enabled' if enable_preemption else 'disabled'}"
        )
    
    async def submit_job(
        self,
        job: GPUJob,
    ) -> str:
        """
        Submit a GPU job for scheduling.
        
        Args:
            job: GPU job to schedule
            
        Returns:
            Job ID
        """
        async with self._lock:
            # Add to priority queue (negative priority for max heap)
            heapq.heappush(
                self._pending_jobs,
                (-job.priority, job.created_at, job),
            )
            
            logger.info(
                f"Submitted job {job.job_id} (priority={job.priority}, "
                f"gpus={job.gpu_count}x{job.gpu_type.value})"
            )
            
            return job.job_id
    
    async def schedule(self) -> List[GPUAllocation]:
        """
        Run scheduling algorithm to allocate GPUs.
        
        Returns:
            List of new allocations made
        """
        async with self._lock:
            allocations = []
            
            # Process pending jobs in priority order
            remaining_jobs = []
            
            while self._pending_jobs:
                _, _, job = heapq.heappop(self._pending_jobs)
                
                # Try to allocate GPUs
                allocation = await self._try_allocate(job)
                
                if allocation:
                    allocations.append(allocation)
                    self._running_jobs[job.job_id] = job
                    job.started_at = datetime.utcnow()
                else:
                    # Can't allocate, keep in queue
                    heapq.heappush(
                        remaining_jobs,
                        (-job.priority, job.created_at, job),
                    )
            
            # Restore unallocated jobs
            self._pending_jobs = remaining_jobs
            
            if allocations:
                logger.info(f"Scheduled {len(allocations)} jobs")
            
            return allocations
    
    async def _try_allocate(self, job: GPUJob) -> Optional[GPUAllocation]:
        """Try to allocate GPUs for a job"""
        available = self._available_gpus.get(job.gpu_type, set())
        
        if len(available) < job.gpu_count:
            logger.debug(
                f"Insufficient GPUs for job {job.job_id}: "
                f"need {job.gpu_count}, have {len(available)}"
            )
            return None
        
        # Allocate GPUs (gang scheduling - all or nothing)
        allocated_gpu_ids = []
        
        for _ in range(job.gpu_count):
            gpu_id = available.pop()
            allocated_gpu_ids.append(gpu_id)
        
        # Create allocation
        allocation = GPUAllocation(
            job_id=job.job_id,
            gpu_ids=allocated_gpu_ids,
            gpu_type=job.gpu_type,
        )
        
        self._allocated_gpus[job.job_id] = allocation
        
        logger.info(
            f"Allocated {job.gpu_count} {job.gpu_type.value} GPUs to job {job.job_id}"
        )
        
        return allocation
    
    async def release_job(self, job_id: str) -> bool:
        """
        Release GPUs from a completed job.
        
        Args:
            job_id: Job to release
            
        Returns:
            True if successful, False if job not found
        """
        async with self._lock:
            allocation = self._allocated_gpus.get(job_id)
            
            if not allocation:
                logger.warning(f"No allocation found for job {job_id}")
                return False
            
            # Return GPUs to available pool
            for gpu_id in allocation.gpu_ids:
                self._available_gpus[allocation.gpu_type].add(gpu_id)
            
            # Mark allocation as released
            allocation.released_at = datetime.utcnow()
            
            # Move job to completed
            job = self._running_jobs.pop(job_id, None)
            if job:
                job.completed_at = datetime.utcnow()
                self._completed_jobs.append(job)
            
            del self._allocated_gpus[job_id]
            
            logger.info(
                f"Released {len(allocation.gpu_ids)} GPUs from job {job_id}"
            )
            
            return True
    
    async def get_utilization(self) -> Dict[str, any]:
        """
        Get GPU utilization metrics.
        
        Returns:
            Utilization dictionary
        """
        total_gpus = sum(self.gpu_inventory.values())
        available_gpus = sum(len(gpus) for gpus in self._available_gpus.values())
        allocated_gpus = total_gpus - available_gpus
        
        by_type = {}
        for gpu_type, total_count in self.gpu_inventory.items():
            available_count = len(self._available_gpus.get(gpu_type, set()))
            allocated_count = total_count - available_count
            
            by_type[gpu_type.value] = {
                "total": total_count,
                "allocated": allocated_count,
                "available": available_count,
                "utilization": (allocated_count / total_count * 100) if total_count > 0 else 0,
            }
        
        return {
            "total_gpus": total_gpus,
            "allocated_gpus": allocated_gpus,
            "available_gpus": available_gpus,
            "utilization": (allocated_gpus / total_gpus * 100) if total_gpus > 0 else 0,
            "by_type": by_type,
            "pending_jobs": len(self._pending_jobs),
            "running_jobs": len(self._running_jobs),
            "completed_jobs": len(self._completed_jobs),
        }
    
    async def get_queue_stats(self) -> Dict[str, any]:
        """
        Get queue statistics.
        
        Returns:
            Queue stats dictionary
        """
        if not self._pending_jobs:
            return {
                "queue_depth": 0,
                "avg_wait_time_seconds": 0.0,
                "max_wait_time_seconds": 0.0,
            }
        
        now = datetime.utcnow()
        wait_times = [
            (now - job.created_at).total_seconds()
            for _, _, job in self._pending_jobs
        ]
        
        return {
            "queue_depth": len(self._pending_jobs),
            "avg_wait_time_seconds": sum(wait_times) / len(wait_times),
            "max_wait_time_seconds": max(wait_times),
        }
    
    async def preempt_low_priority_jobs(
        self,
        min_priority: int,
    ) -> List[str]:
        """
        Preempt jobs below a priority threshold.
        
        Args:
            min_priority: Minimum priority to keep running
            
        Returns:
            List of preempted job IDs
        """
        if not self.enable_preemption:
            logger.warning("Preemption is disabled")
            return []
        
        async with self._lock:
            preempted_job_ids = []
            
            for job_id, job in list(self._running_jobs.items()):
                if job.priority < min_priority:
                    # Release GPUs
                    await self.release_job(job_id)
                    
                    # Re-queue job
                    await self.submit_job(job)
                    
                    preempted_job_ids.append(job_id)
                    
                    logger.info(
                        f"Preempted job {job_id} (priority={job.priority} < {min_priority})"
                    )
            
            return preempted_job_ids
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, any]]:
        """
        Get status of a job.
        
        Args:
            job_id: Job to query
            
        Returns:
            Status dictionary or None if not found
        """
        # Check running jobs
        job = self._running_jobs.get(job_id)
        if job:
            allocation = self._allocated_gpus.get(job_id)
            return {
                "status": "running",
                "job": job,
                "allocation": allocation,
            }
        
        # Check pending jobs
        for _, _, job in self._pending_jobs:
            if job.job_id == job_id:
                return {
                    "status": "pending",
                    "job": job,
                    "allocation": None,
                }
        
        # Check completed jobs
        for job in self._completed_jobs:
            if job.job_id == job_id:
                return {
                    "status": "completed",
                    "job": job,
                    "allocation": None,
                }
        
        return None
    
    async def optimize_placement(self) -> Dict[str, any]:
        """
        Optimize GPU placement using bin packing.
        
        Returns:
            Optimization report
        """
        # Simple first-fit decreasing algorithm
        # Sort jobs by GPU count (descending)
        sorted_jobs = sorted(
            [j for _, _, j in self._pending_jobs],
            key=lambda j: j.gpu_count,
            reverse=True,
        )
        
        # Try to pack jobs
        packed = 0
        total = len(sorted_jobs)
        
        for job in sorted_jobs:
            available = len(self._available_gpus.get(job.gpu_type, set()))
            if available >= job.gpu_count:
                packed += 1
        
        packing_efficiency = (packed / total * 100) if total > 0 else 0
        
        return {
            "total_pending_jobs": total,
            "jobs_that_can_fit": packed,
            "packing_efficiency": packing_efficiency,
        }
