"""
SparkJob routes — user-submitted compute jobs

Follows Core provider pattern with setup function.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import structlog

logger = structlog.get_logger(__name__)


class SubmitJobRequest(BaseModel):
    """Request to submit a SparkJob"""
    name: str
    requested_gpus: int = 1
    requested_memory_gb: int = 80
    estimated_duration_minutes: Optional[int] = None


class SparkJobResponse(BaseModel):
    """Response for a SparkJob"""
    id: str
    name: str
    status: str
    submitted_by: Optional[str] = None
    requested_gpus: int
    requested_memory_gb: int


def setup_spark_jobs_routes(app, engine, provider) -> APIRouter:
    """
    Setup SparkJob routes
    
    Args:
        app: FastAPI application
        engine: Storage engine
        provider: Accelerator provider instance
        
    Returns:
        Configured router
    """
    router = APIRouter(tags=["sparkJobs"])
    router = APIRouter(tags=["sparkJobs"])

    @router.post(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Accelerator/sparkJobs/{job_name}",
        response_model=SparkJobResponse,
        status_code=201,
    )
    async def submit_spark_job(
        subscription_id: str,
        resource_group: str,
        job_name: str,
        request: SubmitJobRequest,
    ) -> SparkJobResponse:
        """Submit a new SparkJob"""
        logger.info(
            "submit_spark_job",
            subscription_id=subscription_id,
            resource_group=resource_group,
            job_name=job_name,
        )

        # TODO: Implement with storage engine
        return SparkJobResponse(
            id=f"job-{job_name}",
            name=job_name,
            status="Pending",
            requested_gpus=request.requested_gpus,
            requested_memory_gb=request.requested_memory_gb,
        )

    @router.get(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Accelerator/sparkJobs",
        response_model=dict,
    )
    async def list_spark_jobs(
        subscription_id: str,
        resource_group: str,
        submitted_by: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> dict:
        """List SparkJobs in a resource group"""
        logger.info(
            "list_spark_jobs",
            subscription_id=subscription_id,
            resource_group=resource_group,
            submitted_by=submitted_by,
        )

        # TODO: Implement with storage engine
        return {
            "value": [],
            "nextLink": None,
        }

    @router.get(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Accelerator/sparkJobs/{job_id}",
        response_model=SparkJobResponse,
    )
    async def get_spark_job(
        subscription_id: str,
        resource_group: str,
        job_id: str,
    ) -> SparkJobResponse:
        """Get a specific SparkJob"""
        logger.info(
            "get_spark_job",
            subscription_id=subscription_id,
            resource_group=resource_group,
            job_id=job_id,
        )

        # TODO: Implement with storage engine
        raise HTTPException(status_code=404, detail="SparkJob not found")

    @router.post(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Accelerator/sparkJobs/{job_id}/cancel",
        status_code=202,
    )
    async def cancel_spark_job(
        subscription_id: str,
        resource_group: str,
        job_id: str,
    ) -> dict:
        """Cancel a SparkJob"""
        logger.info(
            "cancel_spark_job",
            subscription_id=subscription_id,
            resource_group=resource_group,
            job_id=job_id,
        )

        # TODO: Implement with storage engine
        raise HTTPException(status_code=404, detail="SparkJob not found")
    
    return router
