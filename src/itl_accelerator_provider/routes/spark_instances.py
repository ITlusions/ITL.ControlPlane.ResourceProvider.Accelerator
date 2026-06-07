"""
SparkOllamaInstance routes — provisioned LLM instances

Follows Core provider pattern with setup function.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import structlog

logger = structlog.get_logger(__name__)


class ProvisionInstanceRequest(BaseModel):
    """Request to provision an Ollama instance"""
    name: str
    model: str
    gpus: int = 1
    memory_gb: int = 80


class SparkOllamaInstanceResponse(BaseModel):
    """Response for a SparkOllamaInstance"""
    id: str
    name: str
    model: str
    phase: str
    gpus_allocated: int
    memory_allocated_gb: int


def setup_spark_instances_routes(app, engine, provider) -> APIRouter:
    """
    Setup SparkOllamaInstance routes
    
    Args:
        app: FastAPI application
        engine: Storage engine
        provider: Accelerator provider instance
        
    Returns:
        Configured router
    """
    router = APIRouter(tags=["sparkOllamaInstances"])
    router = APIRouter(tags=["sparkOllamaInstances"])

    @router.post(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Accelerator/sparkNodes/{node_id}/sparkOllamaInstances/{instance_name}",
        status_code=202,
    )
    async def provision_ollama_instance(
        subscription_id: str,
        resource_group: str,
        node_id: str,
        instance_name: str,
        request: ProvisionInstanceRequest,
    ) -> dict:
        """Provision Ollama instance on SparkNode (returns 202 Accepted)"""
        logger.info(
            "provision_ollama_instance",
            subscription_id=subscription_id,
            resource_group=resource_group,
            node_id=node_id,
            instance_name=instance_name,
        )

        # TODO: Implement with storage engine
        return {
            "id": f"instance-{instance_name}",
            "status": "Provisioning",
            "status_url": f"/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Accelerator/sparkNodes/{node_id}/sparkOllamaInstances/{instance_name}",
        }

    @router.get(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Accelerator/sparkNodes/{node_id}/sparkOllamaInstances/{instance_id}"
    )
    async def get_ollama_instance(
        subscription_id: str,
        resource_group: str,
        node_id: str,
        instance_id: str,
    ) -> SparkOllamaInstanceResponse:
        """Get Ollama instance details"""
        logger.info(
            "get_ollama_instance",
            subscription_id=subscription_id,
            resource_group=resource_group,
            node_id=node_id,
            instance_id=instance_id,
        )

        # TODO: Implement with storage engine
        raise HTTPException(status_code=404, detail="Instance not found")

    @router.get(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Accelerator/sparkNodes/{node_id}/sparkOllamaInstances/{instance_id}/stats"
    )
    async def get_instance_stats(
        subscription_id: str,
        resource_group: str,
        node_id: str,
        instance_id: str,
        hours: int = 24,
    ) -> dict:
        """Get usage statistics for instance"""
        logger.info(
            "get_instance_stats",
            subscription_id=subscription_id,
            resource_group=resource_group,
            node_id=node_id,
            instance_id=instance_id,
            hours=hours,
        )

        # TODO: Implement with storage engine
        return {
            "instance_id": instance_id,
            "total_requests": 0,
            "total_tokens": 0,
            "avg_response_time_ms": 0,
            "success_rate": 1.0,
        }

    @router.delete(
        "/subscriptions/{subscription_id}/resourceGroups/{resource_group}/providers/ITL.Accelerator/sparkNodes/{node_id}/sparkOllamaInstances/{instance_id}",
        status_code=204,
    )
    async def deprovision_ollama_instance(
        subscription_id: str,
        resource_group: str,
        node_id: str,
        instance_id: str,
    ) -> None:
        """Deprovision Ollama instance"""
        logger.info(
            "deprovision_ollama_instance",
            subscription_id=subscription_id,
            resource_group=resource_group,
            node_id=node_id,
            instance_id=instance_id,
        )

        # TODO: Implement with storage engine
        raise HTTPException(status_code=404, detail="Instance not found")
    
    return router
